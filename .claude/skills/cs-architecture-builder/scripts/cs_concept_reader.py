"""
CS Concept Reader — extracts CSRs, CAL allocations and threat context from a
CS Concept xlsx produced by cs-concept-builder.

Tab contract (as emitted by cs-concept-builder/scripts/generate_cs_concept.py):

  00_Title_Page          labels in col B, values in col C, from row 6
  02_CS_Goals_Echo       header row 2 | CSG ID, Threat, Asset, CAL, TARA IDs, CS Goal Text
  05_CSR_Catalog         header row 2 | CSR ID, Parent CSG, CAL, Branch, Node ID,
                                        Requirement Text, Verification Method
  06_CAL_Allocation      header row 2 | Node ID, Node Name, Type, Inherited CAL, CSR Count

Historic note: this reader previously looked for "02_CSRs_Catalog",
"03_CAL_Allocations" and "04_Threat_Mapping" — none of which cs-concept-builder
has ever emitted — and read the title page from columns A/B. The result was a
silently empty parse and a blank CS Architecture. Legacy names are retained as
fallbacks so hand-built workbooks using the old layout still load.
"""

from openpyxl import load_workbook

# Preferred sheet name first, legacy aliases after.
CSR_SHEETS = ("05_CSR_Catalog", "02_CSRs_Catalog")
CAL_SHEETS = ("06_CAL_Allocation", "03_CAL_Allocations")
GOALS_SHEETS = ("02_CS_Goals_Echo", "04_Threat_Mapping")
TITLE_SHEETS = ("00_Title_Page",)

HEADER_ROW = 2
FIRST_DATA_ROW = 3


def _pick(wb, names):
    """Return the first sheet present from `names`, else None."""
    for name in names:
        if name in wb.sheetnames:
            return wb[name]
    return None


def _cell(row, idx):
    """Safe positional read from a values_only tuple."""
    return row[idx] if len(row) > idx and row[idx] is not None else ""


def _split_list(value):
    if not value:
        return []
    return [p.strip() for p in str(value).split(",") if p.strip()]


def read_cs_concept(filepath: str) -> dict:
    """
    Read a CS Concept xlsx and extract:
      item            metadata from the title page
      csrs            Cybersecurity Requirements with CAL, branch, node, verification
      cal_allocations per-node inherited CAL and CSR count
      threat_mapping  CS Goals (threat/asset/CAL) with the CSRs derived from each

    Raises ValueError when no CSR catalog tab can be found — a blank parse used
    to propagate silently into an empty CS Architecture workbook.
    """
    wb = load_workbook(filepath, data_only=True)

    result = {
        "item": {},
        "csrs": [],
        "cal_allocations": [],
        "threat_mapping": [],
    }

    # ---- Title page: label in column B, value in column C ----------------
    ws = _pick(wb, TITLE_SHEETS)
    if ws is not None:
        for row in ws.iter_rows(min_row=4, max_row=30, values_only=True):
            label, value = _cell(row, 1), _cell(row, 2)
            if label and value:
                result["item"][str(label)] = value
        # Row 3 of the title block carries the item title as a merged banner.
        banner = ws.cell(row=3, column=1).value or ws.cell(row=3, column=2).value
        if banner and "Item Title" not in result["item"]:
            result["item"]["Item Title"] = banner

    # ---- CSR catalog ------------------------------------------------------
    ws = _pick(wb, CSR_SHEETS)
    if ws is None:
        wb.close()
        raise ValueError(
            f"{filepath}: no CSR catalog tab found (looked for "
            f"{', '.join(CSR_SHEETS)}). Is this a CS Concept workbook produced "
            f"by cs-concept-builder?"
        )

    for row in ws.iter_rows(min_row=FIRST_DATA_ROW, values_only=True):
        if not _cell(row, 0):
            continue
        node_id = _cell(row, 4)
        result["csrs"].append({
            "csr_id": _cell(row, 0),
            "parent_csg": _cell(row, 1),
            "cal": _cell(row, 2),
            # `tara_level` kept for downstream compatibility; CAL is the value
            # cs-concept-builder actually carries in this column.
            "tara_level": _cell(row, 2),
            "branch": _cell(row, 3),
            "title": _cell(row, 3),
            "node_id": node_id,
            "allocated_nodes": [node_id] if node_id else [],
            "description": _cell(row, 5),
            "requirement_text": _cell(row, 5),
            "verification_method": _cell(row, 6),
        })

    # ---- CAL allocation ---------------------------------------------------
    ws = _pick(wb, CAL_SHEETS)
    if ws is not None:
        for row in ws.iter_rows(min_row=FIRST_DATA_ROW, values_only=True):
            if not _cell(row, 0):
                continue
            result["cal_allocations"].append({
                "node_id": _cell(row, 0),
                "node_name": _cell(row, 1),
                "node_type": _cell(row, 2),
                "cal": _cell(row, 3),
                "csr_count": _cell(row, 4),
            })

    # ---- Threat context from the CS Goals echo ----------------------------
    ws = _pick(wb, GOALS_SHEETS)
    if ws is not None:
        csrs_by_goal = {}
        for csr in result["csrs"]:
            csrs_by_goal.setdefault(csr["parent_csg"], []).append(csr["csr_id"])

        for row in ws.iter_rows(min_row=FIRST_DATA_ROW, values_only=True):
            goal_id = _cell(row, 0)
            if not goal_id:
                continue
            result["threat_mapping"].append({
                "threat_id": goal_id,
                "attack_type": _cell(row, 1),
                "target_asset": _cell(row, 2),
                # Legacy key name; holds the asset, not a node ID.
                "target_node": _cell(row, 2),
                "severity": _cell(row, 3),
                "cal": _cell(row, 3),
                "driving_tara_ids": _split_list(_cell(row, 4)),
                "goal_text": _cell(row, 5),
                "linked_csrs": csrs_by_goal.get(goal_id, []),
            })

    wb.close()
    return result
