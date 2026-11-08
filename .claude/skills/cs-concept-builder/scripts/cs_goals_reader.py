"""
CS Goals Reader — extracts cybersecurity goals from cs-goals-builder xlsx.

Tab contract (as emitted by cs-goals-builder/scripts/generate_cs_goals.py):

  00_Title_Page            labels in col B, values in col C, from row 6
  02_TARA_Echo             header row 1 | Threat_ID, Asset, Threat_Description, Risk_Value
  03_Cybersecurity_Goals   header row 1 | CSG_ID, Threat_Scenario_Ref, Asset, CS_Goal_Text,
                                          CAL, Cybersecurity_Property,
                                          Residual_Risk_Acceptance, Goal_Owner

Columns are located BY HEADER NAME, and the header row is located by scanning
for the CSG ID header — never assumed.

Historic note (issue #65): this reader previously read columns 1-6 by fixed
position starting at row 5. cs-goals-builder puts its header on row 1, so the
first three goals were never read at all, and CAL / TARA IDs / goal text were
each taken from the column to their left (goal text landed in CAL, CAL in TARA
IDs, the security property in goal text). Every CSR therefore carried goal text
as its CAL and every node's inherited CAL collapsed to CAL-1. Found by the
column-level chain-contract audit (#64).
"""

import re
import sys

from openpyxl import load_workbook

HEADER_SCAN_ROWS = 10

# field -> acceptable header spellings (normalised: lowercase, alphanumerics only)
GOAL_COLUMNS = {
    "csg_id": ("csgid", "csg"),
    "scenario_ref": ("threatscenarioref", "threatscenario", "tarascenario", "taraids", "drivingtaraids"),
    "asset": ("asset",),
    "cal": ("cal",),
    "csg_text": ("csgoaltext", "csgtext", "cybersecuritygoal", "goaltext"),
    "property": ("cybersecurityproperty", "securityproperty", "property"),
}


def _norm(value) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value or "").lower())


def _warn(msg: str) -> None:
    print(f"cs_goals_reader: WARNING: {msg}", file=sys.stderr)


def _normalise_cal(value) -> str:
    """'CAL 4' / 'CAL4' / 'cal-4' / 4 -> 'CAL-4' (the form the generator compares against)."""
    m = re.search(r"(\d)", str(value or ""))
    return f"CAL-{m.group(1)}" if m else ""


def _header_map(ws, wanted: dict) -> tuple[int | None, dict]:
    """Find the header row (the row naming the first field) and map field -> 1-based column."""
    first_field = next(iter(wanted))
    for r in range(1, HEADER_SCAN_ROWS + 1):
        row_norm = {c: _norm(ws.cell(r, c).value) for c in range(1, ws.max_column + 1)}
        if not any(v in wanted[first_field] for v in row_norm.values()):
            continue
        cols = {}
        for field, spellings in wanted.items():
            for c, v in row_norm.items():
                if v in spellings:
                    cols[field] = c
                    break
        return r, cols
    return None, {}


def _threat_descriptions(wb) -> dict:
    """Threat_ID -> Threat_Description from 02_TARA_Echo, when present."""
    if "02_TARA_Echo" not in wb.sheetnames:
        return {}
    ws = wb["02_TARA_Echo"]
    hdr, cols = _header_map(ws, {"threat_id": ("threatid",), "desc": ("threatdescription",)})
    if not hdr or "desc" not in cols:
        return {}
    out = {}
    for r in range(hdr + 1, ws.max_row + 1):
        tid = ws.cell(r, cols["threat_id"]).value
        if tid:
            out[str(tid).strip()] = ws.cell(r, cols["desc"]).value or ""
    return out


def read_cs_goals(cs_goals_path: str) -> dict:
    """Extract item metadata and cybersecurity goals from a cs-goals-builder xlsx."""
    wb = load_workbook(cs_goals_path, data_only=True)

    # Item metadata
    item: dict[str, str] = {}
    if "00_Title_Page" in wb.sheetnames:
        ws = wb["00_Title_Page"]
        for r in range(6, 25):
            label = ws.cell(row=r, column=2).value
            value = ws.cell(row=r, column=3).value
            if label and value:
                item[str(label).strip()] = str(value).strip()
        title_text = ws.cell(row=3, column=1).value or ""
        if title_text:
            item["Item Title"] = title_text

    # Cybersecurity goals tab: preferred name, else any tab with a CSG ID header.
    goal_tab = "03_Cybersecurity_Goals" if "03_Cybersecurity_Goals" in wb.sheetnames else None
    if goal_tab is None:
        for sheet_name in wb.sheetnames:
            if "goal" in sheet_name.lower() or "csg" in sheet_name.lower():
                if _header_map(wb[sheet_name], GOAL_COLUMNS)[0]:
                    goal_tab = sheet_name
                    break
    if not goal_tab:
        raise ValueError("CS Goals workbook is missing cybersecurity goals tab.")

    ws = wb[goal_tab]
    header_row, cols = _header_map(ws, GOAL_COLUMNS)
    if not header_row:
        raise ValueError(f"'{goal_tab}': no CSG ID header in rows 1-{HEADER_SCAN_ROWS}.")
    missing = [f for f in ("cal", "csg_text") if f not in cols]
    if missing:
        raise ValueError(f"'{goal_tab}': header row {header_row} has no column for {', '.join(missing)}.")

    threat_desc = _threat_descriptions(wb)

    def _get(r, field):
        c = cols.get(field)
        return ws.cell(r, c).value if c else None

    csg: list[dict] = []
    for r in range(header_row + 1, ws.max_row + 1):
        csg_id = _get(r, "csg_id")
        if not csg_id or not str(csg_id).startswith("CSG-"):
            continue
        ref = str(_get(r, "scenario_ref") or "").strip()
        cal = _normalise_cal(_get(r, "cal"))
        if not cal:
            _warn(f"{csg_id}: no CAL in '{goal_tab}' row {r}; defaulting to CAL-3.")
            cal = "CAL-3"
        csg.append({
            "csg_id": str(csg_id),
            # Threat description when the TARA echo carries it, else the scenario reference.
            "threat": threat_desc.get(ref) or ref,
            "asset": _get(r, "asset") or "",
            "cal": cal,
            "driving_tara_ids": ref,
            "csg_text": _get(r, "csg_text") or "",
            "property": _get(r, "property") or "",
        })

    if not csg:
        raise ValueError("CS Goals workbook contained no cybersecurity goals.")

    return {"item": item, "cybersecurity_goals": csg, "cs_goals_path": cs_goals_path}
