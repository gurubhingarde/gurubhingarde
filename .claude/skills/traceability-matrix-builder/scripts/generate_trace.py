"""Traceability Matrix builder - generates ISO 26262 bidirectional RTM.

Reads the input JSON and emits all 11 tabs advertised in SKILL.md. Every tab
below the Title page is populated from the input; nothing is hard-coded.

Coverage model (documented on the Validation Rules tab so an assessor can see
the definition the numbers were computed under):

  * A requirement is COVERED if at least one lower-level element points at it
    (a lower-level requirement or design element via `traces_to`, or a test
    case via `verifies`). Otherwise it is an ORPHAN REQUIREMENT.
  * A stakeholder need is COVERED if at least one requirement traces to it.
  * A test case is an ORPHAN TEST if its `verifies` list is empty or names an
    ID that does not exist in the catalog.
"""

from __future__ import annotations

import json
import sys
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

NAVY = "1F3864"
LIGHT_BLUE = "D9E2F3"
AMBER = "FFE699"
RED = "F8CBAD"
GREEN = "C6E0B4"

THIN = Side(style="thin", color="8EA9DB")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

COVERAGE_THRESHOLD = 95.0

# (input key, catalog category, element type, link field)
SOURCES = [
    ("stakeholder_needs", "Stakeholder Need", "Need", None),
    ("system_requirements", "System Requirement", "Requirement", "traces_to"),
    ("subsystem_requirements", "Subsystem Requirement", "Requirement", "traces_to"),
    ("component_requirements", "Component Requirement", "Requirement", "traces_to"),
    ("design_elements", "Design Element", "Design", "traces_to"),
    ("test_cases", "Test Case", "Test", "verifies"),
]

REQUIREMENT_KEYS = ("system_requirements", "subsystem_requirements", "component_requirements")


def _header(ws, row, labels, width=None):
    for col, label in enumerate(labels, start=1):
        c = ws.cell(row=row, column=col, value=label)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
        ws.column_dimensions[get_column_letter(col)].width = (width or 26)


def _title(ws, text):
    ws["A1"] = text
    ws["A1"].font = Font(size=14, bold=True, color=NAVY)


def _row(ws, row, values, fill=None):
    for col, value in enumerate(values, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.alignment = Alignment(vertical="top", wrap_text=True)
        c.border = BOX
        if fill:
            c.fill = PatternFill("solid", fgColor=fill)


def build_catalog(data):
    """Flatten every input list into one catalog of trace elements."""
    catalog = []
    for key, category, etype, link_field in SOURCES:
        for element in data.get(key, []) or []:
            catalog.append(
                {
                    "key": key,
                    "category": category,
                    "id": element.get("id", ""),
                    "title": element.get("title", ""),
                    "type": etype,
                    "links": list(element.get(link_field, []) or []) if link_field else [],
                    "result": element.get("result", ""),
                }
            )
    return catalog


def analyse(catalog):
    """Compute upstream/downstream maps, orphans and coverage percentages."""
    by_id = {e["id"]: e for e in catalog if e["id"]}

    downstream = {eid: [] for eid in by_id}   # target id -> [ids pointing at it]
    dangling = []                              # (source id, unknown target id)
    for element in catalog:
        for target in element["links"]:
            if target in downstream:
                downstream[target].append(element["id"])
            else:
                dangling.append((element["id"], target))

    needs = [e for e in catalog if e["key"] == "stakeholder_needs"]
    reqs = [e for e in catalog if e["key"] in REQUIREMENT_KEYS]
    tests = [e for e in catalog if e["key"] == "test_cases"]

    orphan_needs = [e for e in needs if not downstream.get(e["id"])]
    orphan_reqs = [e for e in reqs if not downstream.get(e["id"])]
    orphan_tests = [
        e for e in tests if not [t for t in e["links"] if t in by_id]
    ]

    def pct(good, total):
        return round(100.0 * good / total, 1) if total else 0.0

    metrics = {
        "need_coverage": pct(len(needs) - len(orphan_needs), len(needs)),
        "requirement_coverage": pct(len(reqs) - len(orphan_reqs), len(reqs)),
        "test_coverage": pct(len(tests) - len(orphan_tests), len(tests)),
    }
    traced_total = len(needs) + len(reqs) + len(tests)
    traced_ok = traced_total - len(orphan_needs) - len(orphan_reqs) - len(orphan_tests)
    metrics["overall_coverage"] = pct(traced_ok, traced_total)

    return {
        "by_id": by_id,
        "downstream": downstream,
        "dangling": dangling,
        "needs": needs,
        "reqs": reqs,
        "tests": tests,
        "orphan_needs": orphan_needs,
        "orphan_reqs": orphan_reqs,
        "orphan_tests": orphan_tests,
        "metrics": metrics,
    }


def forward_chains(catalog, an):
    """Needs -> system -> subsystem -> component -> design -> test, one row per leaf path."""
    by_id = an["by_id"]
    children = {eid: [] for eid in by_id}
    for element in catalog:
        for target in element["links"]:
            if target in children:
                children[target].append(element["id"])

    order = {
        "stakeholder_needs": 0,
        "system_requirements": 1,
        "subsystem_requirements": 2,
        "component_requirements": 3,
        "design_elements": 4,
        "test_cases": 5,
    }

    rows = []

    def walk(eid, path):
        element = by_id[eid]
        slot = order[element["key"]]
        path = list(path)
        path[slot] = eid
        kids = children.get(eid, [])
        if not kids:
            rows.append(path)
            return
        for kid in kids:
            walk(kid, path)

    for need in an["needs"]:
        walk(need["id"], [""] * 6)

    # requirements that hang off no need at all still deserve a forward row
    covered = {cell for row in rows for cell in row if cell}
    for element in an["reqs"]:
        if element["id"] not in covered:
            walk(element["id"], [""] * 6)

    return rows


def main(input_json: str, output_xlsx: str):
    with open(input_json) as f:
        data = json.load(f)

    item = data.get("item", {})
    name = item.get("name", "Unnamed Item")
    doc_id = item.get("doc_id", "TM-001")
    revision = item.get("revision", "1.0")

    catalog = build_catalog(data)
    an = analyse(catalog)
    metrics = an["metrics"]

    wb = Workbook()
    wb.remove(wb.active)

    # 1 -------------------------------------------------- Title
    ws = wb.create_sheet("Title")
    ws.merge_cells("A2:C2")
    c = ws["A2"]
    c.value = "Traceability Matrix"
    c.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.alignment = Alignment(horizontal="center")
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 46
    for row, (label, value) in enumerate(
        [
            ("Item", name),
            ("Document ID", doc_id),
            ("Revision", revision),
            ("Generated", date.today().isoformat()),
            ("Standards", "ISO 26262, ISO/SAE 21434, IEEE 1012"),
            ("Scope", item.get("scope", "Bidirectional trace: needs to test results")),
        ],
        start=4,
    ):
        ws.cell(row=row, column=1, value=label).font = Font(bold=True)
        ws.cell(row=row, column=2, value=value)

    # 2 -------------------------------------------------- Document Control
    ws = wb.create_sheet("Document Control")
    _title(ws, "Document Control")
    _header(ws, 3, ["Version", "Date", "Author", "Change Description", "Approver"])
    history = data.get("document_control", []) or [
        {
            "version": revision,
            "date": date.today().isoformat(),
            "author": item.get("author", "TBD"),
            "description": "Initial generated traceability matrix",
            "approver": item.get("approver", "TBD"),
        }
    ]
    for i, entry in enumerate(history, start=4):
        _row(
            ws,
            i,
            [
                entry.get("version", ""),
                entry.get("date", ""),
                entry.get("author", ""),
                entry.get("description", ""),
                entry.get("approver", ""),
            ],
        )

    # 3 -------------------------------------------------- Trace Source Catalog
    # Column order is the reviewer's probe contract: category, id, title, type.
    ws = wb.create_sheet("Trace Source Catalog")
    _header(ws, 1, ["Category", "Element ID", "Title", "Type", "Links To"])
    for i, element in enumerate(catalog, start=2):
        _row(
            ws,
            i,
            [
                element["category"],
                element["id"],
                element["title"],
                element["type"],
                ", ".join(element["links"]),
            ],
        )

    # 4 -------------------------------------------------- Forward Traceability
    ws = wb.create_sheet("Forward Traceability")
    _title(ws, "Forward Traceability - stakeholder need to test case")
    _header(
        ws,
        3,
        [
            "Stakeholder Need",
            "System Requirement",
            "Subsystem Requirement",
            "Component Requirement",
            "Design Element",
            "Test Case",
            "Break",
        ],
    )
    rows = forward_chains(catalog, an)
    for i, path in enumerate(rows, start=4):
        broken = "" if path[5] else "No test case on this path"
        _row(ws, i, list(path) + [broken], fill=AMBER if broken else None)
    if not rows:
        _row(ws, 4, ["(no trace paths derivable from input)"] + [""] * 6, fill=RED)

    # 5 -------------------------------------------------- Backward Traceability
    ws = wb.create_sheet("Backward Traceability")
    _title(ws, "Backward Traceability - test case to stakeholder need")
    _header(ws, 3, ["Test Case", "Title", "Verifies", "Upstream Chain", "Terminates At Need"])
    by_id = an["by_id"]

    def upward(eid, seen=None):
        seen = seen or set()
        if eid in seen or eid not in by_id:
            return []
        seen.add(eid)
        chain = [eid]
        for parent in by_id[eid]["links"]:
            chain += upward(parent, seen)
        return chain

    for i, test in enumerate(an["tests"], start=4):
        chain = []
        for target in test["links"]:
            chain += upward(target)
        need = [cid for cid in chain if by_id.get(cid, {}).get("key") == "stakeholder_needs"]
        _row(
            ws,
            i,
            [
                test["id"],
                test["title"],
                ", ".join(test["links"]) or "(none)",
                " -> ".join(chain) or "(none)",
                ", ".join(need) or "NO",
            ],
            fill=RED if not need else None,
        )

    # 6 -------------------------------------------------- Coverage Analysis
    # Rows 4-7 are the metric block; the orphan register starts at row 10 with a
    # "Orphan Requirement" / "Orphan Test Case" label in column A. trace_probe.py
    # reads both by label, not by fixed offset.
    ws = wb.create_sheet("Coverage Analysis")
    _title(ws, "Coverage Analysis Report")
    _header(ws, 3, ["Metric", "Value (%)", "Threshold (%)", "Verdict"])
    metric_rows = [
        ("Need coverage", metrics["need_coverage"]),
        ("Requirement coverage", metrics["requirement_coverage"]),
        ("Test coverage", metrics["test_coverage"]),
        ("Overall coverage", metrics["overall_coverage"]),
    ]
    for i, (label, value) in enumerate(metric_rows, start=4):
        ok = value >= COVERAGE_THRESHOLD
        _row(
            ws,
            i,
            [label, value, COVERAGE_THRESHOLD, "PASS" if ok else "FAIL"],
            fill=GREEN if ok else RED,
        )

    _header(ws, 9, ["Orphan Type", "Element ID", "Title", "Reason"])
    orphan_rows = (
        [("Orphan Requirement", e, "No downstream requirement, design or test references this ID")
         for e in an["orphan_reqs"]]
        + [("Orphan Test Case", e, "Verifies no known requirement ID")
           for e in an["orphan_tests"]]
        + [("Orphan Stakeholder Need", e, "No requirement traces to this need")
           for e in an["orphan_needs"]]
    )
    for i, (label, element, reason) in enumerate(orphan_rows, start=10):
        _row(ws, i, [label, element["id"], element["title"], reason], fill=RED)
    if not orphan_rows:
        _row(ws, 10, ["None", "", "", "No orphans detected in this input"], fill=GREEN)

    # 7 -------------------------------------------------- Trace Quality Metrics
    ws = wb.create_sheet("Trace Quality Metrics")
    _title(ws, "Trace Quality Metrics")
    _header(ws, 3, ["Metric", "Count", "Note"])
    quality = [
        ("Stakeholder needs", len(an["needs"]), ""),
        ("Requirements (all levels)", len(an["reqs"]), ""),
        ("Design elements", len([e for e in catalog if e["key"] == "design_elements"]), ""),
        ("Test cases", len(an["tests"]), ""),
        ("Catalog elements total", len(catalog), ""),
        ("Orphan requirements", len(an["orphan_reqs"]), "Target 0"),
        ("Orphan test cases", len(an["orphan_tests"]), "Target 0"),
        ("Orphan stakeholder needs", len(an["orphan_needs"]), "Target 0"),
        ("Dangling link references", len(an["dangling"]), "Links naming an unknown ID"),
        ("Forward trace paths", len(rows), ""),
    ]
    for i, entry in enumerate(quality, start=4):
        _row(ws, i, list(entry))

    # 8 -------------------------------------------------- Gap Identification
    ws = wb.create_sheet("Gap Identification")
    _title(ws, "Gap Identification")
    _header(ws, 3, ["Gap ID", "Gap Type", "Element ID", "Description", "Severity"])
    gaps = []
    for element in an["orphan_reqs"]:
        gaps.append(("Untraced requirement", element["id"],
                     f"{element['title']} has no downstream link", "High"))
    for element in an["orphan_tests"]:
        gaps.append(("Unlinked test case", element["id"],
                     f"{element['title']} verifies no known requirement", "Medium"))
    for element in an["orphan_needs"]:
        gaps.append(("Unimplemented need", element["id"],
                     f"{element['title']} has no requirement tracing to it", "High"))
    for source, target in an["dangling"]:
        gaps.append(("Dangling reference", source,
                     f"References '{target}', which is not in the catalog", "High"))
    for path in rows:
        if not path[5]:
            leaf = [cell for cell in path if cell][-1] if any(path) else ""
            gaps.append(("Unverified path", leaf, "Forward path terminates without a test case",
                         "Medium"))
    for i, (gtype, eid, desc, sev) in enumerate(gaps, start=4):
        _row(ws, i, [f"GAP-{i - 3:03d}", gtype, eid, desc, sev],
             fill=RED if sev == "High" else AMBER)
    if not gaps:
        _row(ws, 4, ["-", "None", "", "No gaps identified", "-"], fill=GREEN)

    # 9 -------------------------------------------------- Trace Convention Rules
    ws = wb.create_sheet("Trace Convention Rules")
    _title(ws, "Trace Convention Rules")
    _header(ws, 3, ["Rule ID", "Applies To", "ID Pattern", "Link Rule"])
    conventions = data.get("convention_rules") or [
        {"applies_to": "Stakeholder Need", "pattern": "SN-nnn", "link": "Traced from by >=1 system requirement"},
        {"applies_to": "System Requirement", "pattern": "SYS-REQ-nnn", "link": "traces_to a stakeholder need"},
        {"applies_to": "Subsystem Requirement", "pattern": "SUB-REQ-nnn", "link": "traces_to a system requirement"},
        {"applies_to": "Component Requirement", "pattern": "CMP-REQ-nnn", "link": "traces_to a subsystem requirement"},
        {"applies_to": "Design Element", "pattern": "DES-nnn", "link": "traces_to a component requirement"},
        {"applies_to": "Test Case", "pattern": "TC-nnn", "link": "verifies >=1 requirement"},
    ]
    for i, rule in enumerate(conventions, start=4):
        _row(ws, i, [f"CV-{i - 3:03d}", rule.get("applies_to", ""), rule.get("pattern", ""),
                     rule.get("link", "")])

    # 10 ------------------------------------------------- Validation Rules
    ws = wb.create_sheet("Validation Rules")
    _title(ws, "Validation Rules")
    _header(ws, 3, ["Rule ID", "Rule", "Threshold", "Measured", "Verdict"])
    validation = [
        ("Requirement coverage is mandatory", 100.0, metrics["requirement_coverage"]),
        ("Test coverage must meet threshold", COVERAGE_THRESHOLD, metrics["test_coverage"]),
        ("Overall coverage must meet threshold", COVERAGE_THRESHOLD, metrics["overall_coverage"]),
        ("Orphan requirements must be zero", 0.0, float(len(an["orphan_reqs"]))),
        ("Orphan test cases must be zero", 0.0, float(len(an["orphan_tests"]))),
    ]
    for i, (rule, threshold, measured) in enumerate(validation, start=4):
        ok = measured <= threshold if "zero" in rule else measured >= threshold
        _row(ws, i, [f"VR-{i - 3:03d}", rule, threshold, measured, "PASS" if ok else "FAIL"],
             fill=GREEN if ok else RED)
    _row(ws, 4 + len(validation) + 1,
         ["Coverage definition", "A requirement is covered when at least one lower-level "
          "requirement, design element or test case references its ID.", "", "", ""])

    # 11 ------------------------------------------------- References
    ws = wb.create_sheet("References")
    _title(ws, "References")
    _header(ws, 3, ["Ref ID", "Document", "Clause / Note"])
    refs = data.get("references") or [
        {"document": "ISO 26262-8:2018", "note": "Clause 6 - specification and management of safety requirements"},
        {"document": "ISO 26262-8:2018", "note": "Clause 9 - verification"},
        {"document": "ISO/SAE 21434:2021", "note": "Clause 10 - product development, requirement traceability"},
        {"document": "IEEE 1012-2016", "note": "V&V traceability analysis"},
    ]
    for i, ref in enumerate(refs, start=4):
        _row(ws, i, [f"REF-{i - 3:03d}", ref.get("document", ""), ref.get("note", "")])

    wb.save(output_xlsx)
    print(f"Traceability Matrix generated: {output_xlsx}")
    print(
        f"  catalog={len(catalog)} orphan_reqs={len(an['orphan_reqs'])} "
        f"orphan_tests={len(an['orphan_tests'])} overall={metrics['overall_coverage']}%"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.json> <output.xlsx>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
