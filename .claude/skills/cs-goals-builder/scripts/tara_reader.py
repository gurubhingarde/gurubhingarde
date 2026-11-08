"""
TARA Reader — extracts cybersecurity goals, assets, threat scenarios, and risk values
from TARA xlsx workbook.

The reader looks for:
1. 11_Cybersecurity_Goals tab (if present, preferred source)
2. 09_Risk_Determination tab (falls back if no CSG tab; derives CSGs from high-risk threats)
3. Asset mapping and threat scenario details from relevant tabs

Returns:
  - List of cybersecurity goal objects with threat references, assets, risk values, CAL guidance
  - Threat scenario echo data for traceability
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def read_tara_xlsx(tara_path: str) -> dict[str, Any]:
    """
    Extract cybersecurity goals and related data from a TARA xlsx file.

    Returns:
      {
        "csg_goals": [{"csg_id", "threat_scenario_id", "asset", "cs_goal_text",
                       "risk_value", "cal_guidance", "property"}, ...],
        "threat_scenarios": [{"threat_id", "asset", "threat_description", "risk_value"}, ...],
        "assets": ["Asset1", "Asset2", ...],
        "metadata": {"source_tab": "11_Cybersecurity_Goals" | "09_Risk_Determination", "row_count": N}
      }
    """

    wb = load_workbook(tara_path, data_only=True)
    result = {
        "csg_goals": [],
        "threat_scenarios": [],
        "assets": set(),
        "metadata": {"source_tab": None, "row_count": 0}
    }

    asset_index = _build_asset_index(wb)
    stride_index = _build_stride_index(wb)

    # Try to read from 11_Cybersecurity_Goals first
    if "11_Cybersecurity_Goals" in wb.sheetnames:
        result.update(
            _read_csg_tab(
                wb["11_Cybersecurity_Goals"], result, asset_index, stride_index
            )
        )
        result["metadata"]["source_tab"] = "11_Cybersecurity_Goals"
    # Fall back to 09_Risk_Determination
    elif "09_Risk_Determination" in wb.sheetnames:
        result.update(
            _read_risk_determination_tab(
                wb["09_Risk_Determination"], result, asset_index, stride_index
            )
        )
        result["metadata"]["source_tab"] = "09_Risk_Determination"
    else:
        print(
            "WARNING: TARA has neither 11_Cybersecurity_Goals nor "
            "09_Risk_Determination; no CSGs derived",
            file=sys.stderr,
        )

    wb.close()

    # Convert assets set to sorted list
    result["assets"] = sorted(list(result["assets"]))

    return result


# --- Header aliasing -------------------------------------------------------
# tara-builder emits human-readable headers ("CSG ID", "Derived From Scenario",
# "Cybersecurity Goal"), not the snake_case names this reader originally assumed.
# Positional fallbacks silently mapped the goal text into `asset` and the risk
# number into `cs_goal_text`. Resolve by name, and only fall back positionally
# when no alias matches.
_HEADER_ALIASES = {
    "csg_id": ("csg_id", "csg", "goal_id"),
    "threat_scenario_id": ("threat_scenario_id", "derived_from_scenario",
                           "scenario_id", "threat_id", "derived_from"),
    "asset": ("asset", "asset_name", "asset_id", "affected_asset"),
    "cs_goal_text": ("cs_goal_text", "cybersecurity_goal", "goal_text",
                     "cs_goal", "goal", "threat_description", "description"),
    "risk_value": ("risk_value", "risk"),
    "cal": ("cal", "cal_guidance", "cal_level"),
}


# --- STRIDE -> cybersecurity property ---------------------------------------
# ISO/SAE 21434 goals are stated against a cybersecurity property. The property
# is not carried on tara-builder's 11_Cybersecurity_Goals tab; it is implied by
# the STRIDE category on 05_Threat_Scenarios, keyed by scenario ID. Previously
# every goal was emitted as "Confidentiality" regardless of category, so five of
# the six STRIDE classes produced a mislabelled goal and cs-concept-builder
# inherited the wrong property when fanning one CSR per goal per property.
_STRIDE_TO_PROPERTY = {
    "spoofing": "Authentication",
    "tampering": "Integrity",
    "repudiation": "Non-repudiation",
    "information_disclosure": "Confidentiality",
    "denial_of_service": "Availability",
    "elevation_of_privilege": "Authorization",
}

# Tolerated spellings seen in the wild / in abbreviated TARA exports.
_STRIDE_SYNONYMS = {
    "info_disclosure": "information_disclosure",
    "information_disclosure_(confidentiality)": "information_disclosure",
    "dos": "denial_of_service",
    "denial-of-service": "denial_of_service",
    "eop": "elevation_of_privilege",
    "elevation_of_privileges": "elevation_of_privilege",
    "privilege_escalation": "elevation_of_privilege",
    "spoof": "spoofing",
    "tamper": "tampering",
    "repudiate": "repudiation",
}

PROPERTY_UNDETERMINED = "Not Determined"


def _stride_to_property(raw) -> str | None:
    """Map a STRIDE category cell to a cybersecurity property.

    Returns None when the value is absent or unrecognised so the caller can warn
    rather than silently assert a property the TARA never claimed.
    """
    if raw is None:
        return None
    key = str(raw).strip().lower().replace(" ", "_").replace("/", "_")
    key = key.strip("_")
    if not key:
        return None
    key = _STRIDE_SYNONYMS.get(key, key)
    return _STRIDE_TO_PROPERTY.get(key)


def _build_stride_index(wb) -> dict:
    """scenario_id -> cybersecurity property, read from 05_Threat_Scenarios.

    The STRIDE column is resolved by header name and falls back to the column
    tara-builder writes it in (3) only when no header matches.
    """
    index: dict[str, str] = {}
    if "05_Threat_Scenarios" not in wb.sheetnames:
        print(
            "WARNING: TARA has no 05_Threat_Scenarios tab; cybersecurity "
            "property cannot be derived from STRIDE",
            file=sys.stderr,
        )
        return index

    ws = wb["05_Threat_Scenarios"]

    # Locate the header row (tara-builder puts a merged title on row 1).
    header_row = None
    for row_idx in range(1, min(ws.max_row, 8) + 1):
        first = ws.cell(row_idx, 1).value
        if first and str(first).strip().lower().replace(" ", "_") in (
            "scenario_id", "threat_id", "threat_scenario_id"
        ):
            header_row = row_idx
            break
    if header_row is None:
        return index

    headers = _normalize_headers(ws, header_row)
    stride_col = None
    for alias in ("stride_category", "stride", "category", "threat_category"):
        if alias in headers:
            stride_col = headers[alias]
            break
    if stride_col is None:
        stride_col = 3

    unmapped = []
    for row_idx in range(header_row + 1, ws.max_row + 1):
        sid = ws.cell(row_idx, 1).value
        if not sid:
            continue
        raw = ws.cell(row_idx, stride_col).value
        prop = _stride_to_property(raw)
        if prop:
            index[str(sid).strip()] = prop
        elif raw:
            unmapped.append(f"{str(sid).strip()}={raw!r}")

    if unmapped:
        print(
            "WARNING: unrecognised STRIDE category on "
            f"{len(unmapped)} scenario(s): {', '.join(unmapped[:5])}"
            f"{' ...' if len(unmapped) > 5 else ''}; property left undetermined",
            file=sys.stderr,
        )
    return index


def _normalize_headers(ws, header_row: int) -> dict:
    """Map normalized header text -> column index. Coerce non-string headers."""
    headers = {}
    for col_idx in range(1, ws.max_column + 1):
        header_val = ws.cell(header_row, col_idx).value
        if header_val is None:
            continue
        key = str(header_val).strip().lower().replace(" ", "_")
        if key and key not in headers:
            headers[key] = col_idx
    return headers


def _col(headers: dict, canonical: str, positional_default=None):
    """Resolve a canonical field to a column index via its aliases."""
    for alias in _HEADER_ALIASES.get(canonical, (canonical,)):
        if alias in headers:
            return headers[alias]
    return positional_default


def _coerce_risk(value, default: int = 3) -> int:
    """Accept int, float ('4.0') and numeric strings. Never silently downgrade."""
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return int(value)
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        print(
            f"WARNING: non-numeric risk value {value!r}; defaulting to {default}",
            file=sys.stderr,
        )
        return default


def _build_asset_index(wb) -> dict:
    """scenario_id -> asset name, resolved through 05_Threat_Scenarios and
    04_Asset_Inventory. Used when the CSG tab carries no asset column."""
    asset_names = {}
    if "04_Asset_Inventory" in wb.sheetnames:
        ws = wb["04_Asset_Inventory"]
        for row_idx in range(1, ws.max_row + 1):
            aid, aname = ws.cell(row_idx, 1).value, ws.cell(row_idx, 2).value
            if aid and aname and str(aid).strip().lower() not in ("asset id", "asset_id"):
                asset_names[str(aid).strip()] = str(aname).strip()

    scenario_asset = {}
    if "05_Threat_Scenarios" in wb.sheetnames:
        ws = wb["05_Threat_Scenarios"]
        for row_idx in range(1, ws.max_row + 1):
            sid, aid = ws.cell(row_idx, 1).value, ws.cell(row_idx, 2).value
            if not sid or not aid:
                continue
            if str(sid).strip().lower() in ("scenario id", "scenario_id"):
                continue
            aid = str(aid).strip()
            scenario_asset[str(sid).strip()] = asset_names.get(aid, aid)
    return scenario_asset


def _read_csg_tab(
    ws,
    result: dict,
    asset_index: dict | None = None,
    stride_index: dict | None = None,
) -> dict:
    """
    Read 11_Cybersecurity_Goals tab directly.
    Expected columns (after header):
      CSG_ID, Threat_Scenario_ID, Asset, CS_Goal_Text, Risk_Value, CAL_Guidance, Properties...
    """
    goals = []
    threats = []
    assets = result["assets"]

    # Detect header row (usually row 1)
    header_row = None
    for row_idx in range(1, 5):
        cell = ws.cell(row_idx, 1).value
        if cell and "CSG" in str(cell):
            header_row = row_idx
            break

    if not header_row:
        header_row = 1

    headers = _normalize_headers(ws, header_row)
    asset_index = asset_index or {}
    stride_index = stride_index or {}

    csg_col = _col(headers, "csg_id", 1)
    threat_col = _col(headers, "threat_scenario_id", 2)
    asset_col = _col(headers, "asset", None)
    goal_col = _col(headers, "cs_goal_text", None)
    risk_col = _col(headers, "risk_value", None)

    if goal_col is None:
        print(
            "WARNING: no goal-text column found in CSG tab; goals will be "
            "synthesized from threat IDs",
            file=sys.stderr,
        )

    # Read data rows
    for row_idx in range(header_row + 1, ws.max_row + 1):
        csg_id = ws.cell(row_idx, csg_col).value
        if not csg_id:
            continue

        threat_id = ws.cell(row_idx, threat_col).value or f"THREAT-{csg_id}"
        threat_id = str(threat_id).strip()

        if asset_col is not None:
            asset = ws.cell(row_idx, asset_col).value or "Unknown"
        else:
            # CSG tab has no asset column — resolve via threat scenario -> asset
            asset = asset_index.get(threat_id, "Unknown")

        cs_goal = (
            ws.cell(row_idx, goal_col).value if goal_col is not None else None
        ) or f"Prevent {threat_id}"

        risk_val = ws.cell(row_idx, risk_col).value if risk_col is not None else None
        risk_int = _coerce_risk(risk_val)

        cal_guidance = _suggest_cal(risk_int)

        goals.append({
            "csg_id": str(csg_id),
            "threat_scenario_id": threat_id,
            "asset": str(asset),
            "cs_goal_text": str(cs_goal),
            "risk_value": risk_int,
            "cal_guidance": cal_guidance,
            "property": stride_index.get(threat_id, PROPERTY_UNDETERMINED),
        })

        threats.append({
            "threat_id": threat_id,
            "asset": str(asset),
            "threat_description": str(cs_goal),
            "risk_value": risk_int
        })

        assets.add(str(asset))

    result["csg_goals"] = goals
    result["threat_scenarios"] = _deduplicate_threats(threats)
    result["metadata"]["row_count"] = len(goals)

    return result


def _read_risk_determination_tab(
    ws,
    result: dict,
    asset_index: dict | None = None,
    stride_index: dict | None = None,
) -> dict:
    """
    Read 09_Risk_Determination tab and derive CSGs from high-risk threat scenarios.
    Expected columns: Threat_ID, Asset, Description, Risk_Value, Severity, ...

    Filters for Risk_Value >= 3 (high risk) and creates a CSG per high-risk threat.
    """
    goals = []
    threats = []
    assets = result["assets"]

    # Detect header row
    header_row = None
    for row_idx in range(1, 5):
        cell = ws.cell(row_idx, 1).value
        if cell and ("threat" in str(cell).lower() or "scenario" in str(cell).lower()):
            header_row = row_idx
            break

    if not header_row:
        header_row = 1

    headers = _normalize_headers(ws, header_row)
    asset_index = asset_index or {}
    stride_index = stride_index or {}

    threat_col = _col(headers, "threat_scenario_id", 1)
    asset_col = _col(headers, "asset", None)
    desc_col = _col(headers, "cs_goal_text", None)
    risk_col = _col(headers, "risk_value", None)

    csg_counter = 0
    for row_idx in range(header_row + 1, ws.max_row + 1):
        threat_id = ws.cell(row_idx, threat_col).value
        if not threat_id:
            continue

        threat_id = str(threat_id).strip()
        if asset_col is not None:
            asset = ws.cell(row_idx, asset_col).value or "Unknown"
        else:
            asset = asset_index.get(threat_id, "Unknown")
        desc = (
            ws.cell(row_idx, desc_col).value if desc_col is not None else None
        ) or threat_id
        risk_val = ws.cell(row_idx, risk_col).value if risk_col is not None else None
        risk_int = _coerce_risk(risk_val, default=1)

        # Only include high-risk threats (risk value >= 3)
        if risk_int >= 3:
            csg_counter += 1
            csg_id = f"CSG-{csg_counter:03d}"
            cal_guidance = _suggest_cal(risk_int)

            goals.append({
                "csg_id": csg_id,
                "threat_scenario_id": str(threat_id),
                "asset": str(asset),
                "cs_goal_text": f"Prevent {desc}",
                "risk_value": risk_int,
                "cal_guidance": cal_guidance,
                "property": stride_index.get(
                    str(threat_id), PROPERTY_UNDETERMINED
                ),
            })

            threats.append({
                "threat_id": str(threat_id),
                "asset": str(asset),
                "threat_description": str(desc),
                "risk_value": risk_int
            })

            assets.add(str(asset))

    result["csg_goals"] = goals
    result["threat_scenarios"] = _deduplicate_threats(threats)
    result["metadata"]["row_count"] = len(goals)

    return result


def _suggest_cal(risk_value: int) -> str:
    """
    Auto-suggest CAL (Cybersecurity Assurance Level) based on risk value.

    CAL 4 (Highest): Risk Value 5 + severe safety impact
    CAL 3: Risk Value 4
    CAL 2: Risk Value 3
    CAL 1: Risk Value 1-2
    """
    if risk_value >= 5:
        return "CAL 4"
    elif risk_value == 4:
        return "CAL 3"
    elif risk_value == 3:
        return "CAL 2"
    else:
        return "CAL 1"


def _deduplicate_threats(threats: list[dict]) -> list[dict]:
    """Remove duplicate threat scenarios by threat_id."""
    seen = {}
    for threat in threats:
        tid = threat["threat_id"]
        if tid not in seen:
            seen[tid] = threat
    return list(seen.values())


def main():
    if len(sys.argv) < 2:
        print("Usage: python tara_reader.py <tara.xlsx>")
        sys.exit(1)

    tara_path = sys.argv[1]
    result = read_tara_xlsx(tara_path)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
