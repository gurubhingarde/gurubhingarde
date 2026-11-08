"""
TSC Reader — Extract safety mechanisms and baseline DC% from a TSC workbook.

Returns a dict mapping (node_id, mechanism_id) to {name, dc, dc_raw}.

Tab contract (as emitted by tsc-builder/scripts/generate_tsc.py:415-424):

  04_Safety_Mechanism_Catalog   header row 4 | FSR_ID, Allocated ASIL, Branch,
                                Linked Node, Mechanism ID, Mechanism Name,
                                Default DC%, Detection Time (target), Selection

Historic note (issue #53): this reader previously asked for
"05_Safety_Mechanisms_From_TSC" — which is fmeda-builder's OWN echo tab, not
anything tsc-builder emits — and probed only column 1 for the header. Since
"Mechanism ID" sits in column 5, a rename alone would not have been enough.
The result was a silently empty parse and a header-only echo tab that looked
like a TSC with no mechanisms. Legacy name is retained as a fallback so
hand-built workbooks using the old layout still load.

Every other TSC reader in the repo (hw-architecture-builder, sw-arch-builder,
safety-case-builder) already used "04_Safety_Mechanism_Catalog".
"""

import sys

from openpyxl import load_workbook

# Preferred sheet name first, legacy aliases after.
MECHANISM_SHEETS = ("04_Safety_Mechanism_Catalog", "05_Safety_Mechanisms_From_TSC")

# Header can sit anywhere in this window; tsc-builder puts it at row 4 under a
# merged title row and a merged analyst note.
HEADER_SCAN_ROWS = 10
HEADER_SCAN_COLS = 20


def _pick(wb, names):
    """Return the first sheet present from `names`, else None."""
    for name in names:
        if name in wb.sheetnames:
            return wb[name], name
    return None, None


def _warn(msg):
    print(f"tsc_reader: WARNING: {msg}", file=sys.stderr)


def _find_header_row(ws):
    """Locate the header row by scanning ALL columns, not just column 1."""
    for r in range(1, HEADER_SCAN_ROWS + 1):
        for c in range(1, HEADER_SCAN_COLS + 1):
            val = ws.cell(r, c).value
            if val and "mechanism id" in str(val).strip().lower():
                return r
    return None


def _parse_dc(value):
    """
    Parse a Default DC% cell into a float percentage.

    tsc-builder's catalog carries qualitative ranges as text — "60-80%",
    ">=99%", "90-99%". The old float() call raised on every one of those and
    silently fell back to 0.0, so even a correct tab lookup would have imported
    a baseline of zero. Ranges collapse to their midpoint; bounded forms take
    the bound.
    """
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace("%", "").replace("≥", ">=").replace("≤", "<=")
    text = text.replace(">=", "").replace("<=", "").replace(">", "").replace("<", "")
    # "99%+" is the catalog's other way of writing ">=99%".
    text = text.rstrip("+").strip()
    # Normalise en/em dashes to a plain hyphen before splitting a range.
    text = text.replace("–", "-").replace("—", "-")

    parts = [p.strip() for p in text.split("-") if p.strip()]
    try:
        nums = [float(p) for p in parts]
    except (ValueError, TypeError):
        return 0.0

    if not nums:
        return 0.0
    if len(nums) == 1:
        return nums[0]
    return sum(nums[:2]) / 2.0


def read_tsc(tsc_path: str) -> dict:
    """
    Read the TSC's safety mechanism catalog and extract:
    - Mechanism ID
    - Mechanism Name
    - Default DC%  (numeric, plus the original text in `dc_raw`)
    - Linked Node  (forward-filled across alternative-candidate rows)

    Returns: {(node_id, mech_id): {name, dc, dc_raw}}

    A zero-row import is reported on stderr rather than returned silently.
    """
    wb = load_workbook(tsc_path, data_only=True)

    ws, sheet_name = _pick(wb, MECHANISM_SHEETS)
    if ws is None:
        _warn(
            f"{tsc_path}: no safety mechanism catalog tab found (looked for "
            f"{', '.join(MECHANISM_SHEETS)}). Is this a TSC workbook produced "
            f"by tsc-builder? No mechanisms imported."
        )
        wb.close()
        return {}

    if sheet_name != MECHANISM_SHEETS[0]:
        _warn(f"{tsc_path}: using legacy tab '{sheet_name}'.")

    header_row = _find_header_row(ws)
    if not header_row:
        _warn(
            f"{tsc_path}: found tab '{sheet_name}' but no 'Mechanism ID' header "
            f"in rows 1-{HEADER_SCAN_ROWS}. No mechanisms imported."
        )
        wb.close()
        return {}

    # Identify columns
    col_mech_id = None
    col_mech_name = None
    col_dc = None
    col_node = None

    for c in range(1, HEADER_SCAN_COLS + 1):
        h = ws.cell(header_row, c).value
        if not h:
            continue
        h = str(h).lower()
        if "mechanism id" in h:
            col_mech_id = c
        elif "mechanism name" in h:
            col_mech_name = c
        elif "default dc" in h or "dc%" in h:
            col_dc = c
        elif "node" in h or "linked" in h:
            col_node = c

    mechanisms = {}
    last_node = ""

    for r in range(header_row + 1, ws.max_row + 1):
        mech_id = ws.cell(r, col_mech_id).value if col_mech_id else None
        mech_name = ws.cell(r, col_mech_name).value if col_mech_name else None
        dc_raw = ws.cell(r, col_dc).value if col_dc else None
        node_id = ws.cell(r, col_node).value if col_node else ""

        # tsc-builder writes FSR_ID / ASIL / Branch / Linked Node only on the
        # first ("[primary]") candidate row; alternatives leave them blank.
        # Carry the last seen node forward so alternatives keep their owner.
        node_id = str(node_id).strip() if node_id else ""
        if node_id:
            last_node = node_id
        else:
            node_id = last_node

        if not mech_id:
            continue

        mech_id = str(mech_id).strip()
        mech_name = str(mech_name).strip() if mech_name else ""

        key = (node_id, mech_id) if node_id else (None, mech_id)
        mechanisms[key] = {
            "name": mech_name,
            "dc": _parse_dc(dc_raw),
            "dc_raw": str(dc_raw).strip() if dc_raw is not None else "",
        }

    wb.close()

    if not mechanisms:
        _warn(
            f"{tsc_path}: tab '{sheet_name}' header found at row {header_row} but "
            f"zero mechanism rows parsed. Downstream FMEDA will have an empty "
            f"mechanism baseline."
        )

    return mechanisms


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tsc_reader.py <tsc.xlsx>")
        sys.exit(1)
    mechs = read_tsc(sys.argv[1])
    import json
    print(json.dumps({f"{k[0]}|{k[1]}": v for k, v in mechs.items()}, indent=2))
