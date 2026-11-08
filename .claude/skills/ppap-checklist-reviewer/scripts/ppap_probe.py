"""
PPAP content probe — extracts title metadata, PSW signoff, submission level,
element statuses, dimensional results, process capability, and customer-specific requirements
from a PPAP package xlsx (produced by ppap-package-builder).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


def _norm(s: Any) -> str:
    if s is None:
        return ""
    return str(s).strip()


def _find_sheet_by_keywords(sheet_names: list[str], keywords: list[str]) -> str:
    for name in sheet_names:
        s_lower = name.lower()
        if any(k.lower() in s_lower for k in keywords):
            return name
    return ""


def _find_header_row(ws, max_search: int = 30) -> tuple[int, dict[str, int]]:
    """Find header row by looking for cells with column headers."""
    # #63: prefer a >=3-cell header; accept a 2-cell header only if no wider row exists,
    # so a two-column tab is located without letting a 2-cell key/value row pre-empt a real header.
    fallback: tuple[int, dict[str, int]] = (0, {})
    for r in range(1, min(ws.max_row, max_search) + 1):
        cells = [(c, _norm(ws.cell(r, c).value)) for c in range(1, ws.max_column + 1)]
        non_empty = [(c, v) for c, v in cells if v]
        if len(non_empty) >= 2:
            if all(len(v) < 100 and not v.startswith("=") for c, v in non_empty):
                header_map = {v.lower(): c for c, v in non_empty}
                if len(non_empty) >= 3:
                    return r, header_map
                if not fallback[0]:
                    fallback = (r, header_map)
    return fallback


def _col_for(header_map: dict[str, int], candidates: list[str]) -> int:
    for cand in candidates:
        cand_lower = cand.lower()
        for header, col in header_map.items():
            if cand_lower in header:
                return col
    return 0


@dataclass
class DimensionalResult:
    characteristic: str = ""
    nominal: str = ""
    tolerance_lower: str = ""
    tolerance_upper: str = ""
    measured_value: str = ""
    status: str = ""  # "OK", "Out-of-Spec"


@dataclass
class ProcessCapability:
    characteristic: str = ""
    cpk: str = ""
    ppk: str = ""
    status: str = ""  # "OK", "Low"


@dataclass
class ProbedPpap:
    path: str = ""
    sheet_names: list[str] = field(default_factory=list)

    # Title page metadata
    customer: str = ""
    supplier: str = ""
    part_name: str = ""
    part_number: str = ""
    submission_level: str = ""

    # PSW (Part Submission Warrant)
    psw_part_name: str = ""
    psw_part_number: str = ""
    psw_supplier_code: str = ""
    psw_customer_code: str = ""
    psw_drawing_change_level: str = ""
    psw_drawing_date: str = ""
    psw_submission_level: str = ""
    psw_declaration: str = ""
    psw_signature_block_populated: bool = False

    # Element submission statuses (Elements 1-18)
    element_statuses: dict[int, str] = field(default_factory=dict)  # {1: "Submitted", 2: "Not Required", ...}

    # Element 1 Design Records
    element1_drawing_number: str = ""
    element1_revision: str = ""
    element1_approval_status: str = ""

    # Element 4 DFMEA
    element4_dfmea_reference: str = ""
    element4_dfmea_hash: str = ""

    # Element 6 PFMEA
    element6_pfmea_reference: str = ""
    element6_pfmea_hash: str = ""

    # Element 7 Control Plan
    element7_control_plan_reference: str = ""
    element7_control_plan_hash: str = ""

    # Element 8 MSA Results
    element8_msa_results: list[dict] = field(default_factory=list)  # [{gage: str, r_and_r_pct: float}, ...]

    # Element 9 Dimensional Results
    dimensional_results: list[DimensionalResult] = field(default_factory=list)

    # Element 11 Process Capability
    process_capability: list[ProcessCapability] = field(default_factory=list)

    # Element 12 Lab Documentation
    element12_accredited_labs: list[str] = field(default_factory=list)

    # Element 17 Customer-Specific Requirements
    customer_specific_requirements: list[dict] = field(default_factory=list)  # [{requirement: str, evidence: str}, ...]


def probe(xlsx_path: str | Path) -> ProbedPpap:
    wb = load_workbook(xlsx_path, data_only=True)
    p = ProbedPpap(path=str(xlsx_path), sheet_names=list(wb.sheetnames))

    # Extract title page metadata
    title_sheet = "00_Title_Page" if "00_Title_Page" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["title"])
    if title_sheet and title_sheet in wb.sheetnames:
        ws = wb[title_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "customer" in label and not p.customer:
                    p.customer = value
                elif "supplier" in label and not p.supplier:
                    p.supplier = value
                elif "part name" in label and not p.part_name:
                    p.part_name = value
                elif "part number" in label and not p.part_number:
                    p.part_number = value
                elif "submission level" in label and not p.submission_level:
                    p.submission_level = value

    # Extract PSW (Part Submission Warrant)
    psw_sheet = "02_PSW_Part_Submission_Warrant" if "02_PSW_Part_Submission_Warrant" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["psw", "submission warrant"])
    if psw_sheet and psw_sheet in wb.sheetnames:
        ws = wb[psw_sheet]
        for r in range(1, min(ws.max_row + 1, 40)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "part name" in label and not p.psw_part_name:
                    p.psw_part_name = value
                elif "part number" in label and not p.psw_part_number:
                    p.psw_part_number = value
                elif "supplier code" in label and not p.psw_supplier_code:
                    p.psw_supplier_code = value
                elif "customer code" in label and not p.psw_customer_code:
                    p.psw_customer_code = value
                elif "drawing change level" in label and not p.psw_drawing_change_level:
                    p.psw_drawing_change_level = value
                elif "drawing" in label and "date" in label and not p.psw_drawing_date:
                    p.psw_drawing_date = value
                elif "submission level" in label and not p.psw_submission_level:
                    p.psw_submission_level = value
                elif "declaration" in label and not p.psw_declaration:
                    p.psw_declaration = value
        # Check for signature block
        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                cell_val = _norm(ws.cell(r, c).value)
                if "signature" in cell_val.lower() or "authorized representative" in cell_val.lower():
                    # Check if next row has content (signature)
                    if _norm(ws.cell(r + 1, c).value) or _norm(ws.cell(r + 1, c + 1).value):
                        p.psw_signature_block_populated = True

    # Extract element submission statuses (Element 18: Submission Status Matrix)
    element18_sheet = "20_Element18_Submission_Status_Matrix" if "20_Element18_Submission_Status_Matrix" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["submission status"])
    if element18_sheet and element18_sheet in wb.sheetnames:
        ws = wb[element18_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            element_col = _col_for(header_map, ["element", "number"])
            status_col = _col_for(header_map, ["status"])
            for r in range(header_row + 1, ws.max_row + 1):
                elem_num_str = _norm(ws.cell(r, element_col).value) if element_col else ""
                status = _norm(ws.cell(r, status_col).value) if status_col else ""
                if elem_num_str and status:
                    try:
                        elem_num = int(re.sub(r"\D", "", elem_num_str))
                        if 1 <= elem_num <= 18:
                            p.element_statuses[elem_num] = status
                    except ValueError:
                        pass

    # Extract Element 1 Design Records
    element1_sheet = "03_Element1_Design_Records" if "03_Element1_Design_Records" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["design record"])
    if element1_sheet and element1_sheet in wb.sheetnames:
        ws = wb[element1_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "drawing number" in label and not p.element1_drawing_number:
                    p.element1_drawing_number = value
                elif "revision" in label and not p.element1_revision:
                    p.element1_revision = value
                elif "approval" in label and not p.element1_approval_status:
                    p.element1_approval_status = value

    # Extract Element 4 DFMEA
    element4_sheet = "06_Element4_DFMEA_Reference" if "06_Element4_DFMEA_Reference" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["dfmea"])
    if element4_sheet and element4_sheet in wb.sheetnames:
        ws = wb[element4_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "reference" in label and not p.element4_dfmea_reference:
                    p.element4_dfmea_reference = value
                elif "hash" in label or "version" in label and not p.element4_dfmea_hash:
                    p.element4_dfmea_hash = value

    # Extract Element 6 PFMEA
    element6_sheet = "08_Element6_PFMEA_Reference" if "08_Element6_PFMEA_Reference" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["pfmea"])
    if element6_sheet and element6_sheet in wb.sheetnames:
        ws = wb[element6_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "reference" in label and not p.element6_pfmea_reference:
                    p.element6_pfmea_reference = value
                elif "hash" in label or "version" in label and not p.element6_pfmea_hash:
                    p.element6_pfmea_hash = value

    # Extract Element 7 Control Plan
    element7_sheet = "09_Element7_Control_Plan_Reference" if "09_Element7_Control_Plan_Reference" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["control plan"])
    if element7_sheet and element7_sheet in wb.sheetnames:
        ws = wb[element7_sheet]
        for r in range(1, min(ws.max_row + 1, 30)):
            for c in range(1, min(ws.max_column + 1, 6)):
                label = _norm(ws.cell(r, c).value).lower()
                value = _norm(ws.cell(r, c + 1).value)
                if not label or not value:
                    continue
                if "reference" in label and not p.element7_control_plan_reference:
                    p.element7_control_plan_reference = value
                elif "hash" in label or "version" in label and not p.element7_control_plan_hash:
                    p.element7_control_plan_hash = value

    # Extract Element 8 MSA Results
    element8_sheet = "10_Element8_MSA_Results" if "10_Element8_MSA_Results" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["msa"])
    if element8_sheet and element8_sheet in wb.sheetnames:
        ws = wb[element8_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            gage_col = _col_for(header_map, ["gage", "measurement"])
            rr_col = _col_for(header_map, ["r&r", "r and r", "repeatability"])
            for r in range(header_row + 1, ws.max_row + 1):
                gage = _norm(ws.cell(r, gage_col).value) if gage_col else ""
                rr_str = _norm(ws.cell(r, rr_col).value) if rr_col else ""
                if gage and rr_str:
                    try:
                        rr_pct = float(rr_str.replace("%", ""))
                        p.element8_msa_results.append({"gage": gage, "r_and_r_pct": rr_pct})
                    except ValueError:
                        p.element8_msa_results.append({"gage": gage, "r_and_r_pct": -1})

    # Extract Element 9 Dimensional Results
    element9_sheet = "11_Element9_Dimensional_Results" if "11_Element9_Dimensional_Results" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["dimensional"])
    if element9_sheet and element9_sheet in wb.sheetnames:
        ws = wb[element9_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            char_col = _col_for(header_map, ["characteristic", "name"])
            nominal_col = _col_for(header_map, ["nominal"])
            lower_col = _col_for(header_map, ["lower", "tolerance_lower", "lsl", "min"])
            upper_col = _col_for(header_map, ["upper", "tolerance_upper", "usl", "max"])
            measured_col = _col_for(header_map, ["measured", "actual", "result"])
            for r in range(header_row + 1, ws.max_row + 1):
                char = _norm(ws.cell(r, char_col).value) if char_col else ""
                if not char:
                    continue
                nominal = _norm(ws.cell(r, nominal_col).value) if nominal_col else ""
                lower = _norm(ws.cell(r, lower_col).value) if lower_col else ""
                upper = _norm(ws.cell(r, upper_col).value) if upper_col else ""
                measured = _norm(ws.cell(r, measured_col).value) if measured_col else ""
                status = "Out-of-Spec"
                try:
                    if measured and lower and upper:
                        m = float(measured)
                        l = float(lower)
                        u = float(upper)
                        status = "OK" if l <= m <= u else "Out-of-Spec"
                except ValueError:
                    pass
                p.dimensional_results.append(DimensionalResult(
                    characteristic=char,
                    nominal=nominal,
                    tolerance_lower=lower,
                    tolerance_upper=upper,
                    measured_value=measured,
                    status=status
                ))

    # Extract Element 11 Process Capability
    element11_sheet = "13_Element11_Initial_Process_Studies" if "13_Element11_Initial_Process_Studies" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["process stud", "capability"])
    if element11_sheet and element11_sheet in wb.sheetnames:
        ws = wb[element11_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            char_col = _col_for(header_map, ["characteristic", "name"])
            cpk_col = _col_for(header_map, ["cpk"])
            ppk_col = _col_for(header_map, ["ppk"])
            for r in range(header_row + 1, ws.max_row + 1):
                char = _norm(ws.cell(r, char_col).value) if char_col else ""
                if not char:
                    continue
                cpk = _norm(ws.cell(r, cpk_col).value) if cpk_col else ""
                ppk = _norm(ws.cell(r, ppk_col).value) if ppk_col else ""
                status = "OK"
                try:
                    if cpk:
                        cpk_val = float(cpk)
                        if cpk_val < 1.33:
                            status = "Low"
                    if ppk:
                        ppk_val = float(ppk)
                        if ppk_val < 1.33:
                            status = "Low"
                except ValueError:
                    pass
                p.process_capability.append(ProcessCapability(
                    characteristic=char,
                    cpk=cpk,
                    ppk=ppk,
                    status=status
                ))

    # Extract Element 12 Lab Documentation
    element12_sheet = "14_Element12_Lab_Documentation" if "14_Element12_Lab_Documentation" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["lab"])
    if element12_sheet and element12_sheet in wb.sheetnames:
        ws = wb[element12_sheet]
        for r in range(1, min(ws.max_row + 1, 50)):
            for c in range(1, min(ws.max_column + 1, 6)):
                cell_val = _norm(ws.cell(r, c).value)
                if "a2la" in cell_val.lower() or "iso 17025" in cell_val.lower():
                    lab_name = _norm(ws.cell(r, c + 1).value) or cell_val
                    if lab_name not in p.element12_accredited_labs:
                        p.element12_accredited_labs.append(lab_name)

    # Extract Element 17 Customer-Specific Requirements
    element17_sheet = "19_Element17_Customer_Specific_Requirements" if "19_Element17_Customer_Specific_Requirements" in wb.sheetnames else _find_sheet_by_keywords(p.sheet_names, ["customer", "specific"])
    if element17_sheet and element17_sheet in wb.sheetnames:
        ws = wb[element17_sheet]
        header_row, header_map = _find_header_row(ws)
        if header_row:
            req_col = _col_for(header_map, ["requirement"])
            evidence_col = _col_for(header_map, ["evidence"])
            for r in range(header_row + 1, ws.max_row + 1):
                req = _norm(ws.cell(r, req_col).value) if req_col else ""
                evidence = _norm(ws.cell(r, evidence_col).value) if evidence_col else ""
                if req:
                    p.customer_specific_requirements.append({"requirement": req, "evidence": evidence})

    return p


if __name__ == "__main__":
    import sys, json
    p = probe(sys.argv[1])
    summary = {
        "path": p.path,
        "customer": p.customer,
        "supplier": p.supplier,
        "part_name": p.part_name,
        "submission_level": p.submission_level,
        "psw_signature_populated": p.psw_signature_block_populated,
        "element_statuses": p.element_statuses,
        "n_dimensional_results": len(p.dimensional_results),
        "out_of_spec_count": sum(1 for d in p.dimensional_results if d.status == "Out-of-Spec"),
        "n_process_capability": len(p.process_capability),
        "low_cpk_count": sum(1 for pc in p.process_capability if pc.status == "Low"),
        "msa_results_count": len(p.element8_msa_results),
        "high_rr_count": sum(1 for m in p.element8_msa_results if m["r_and_r_pct"] > 30),
        "customer_requirements_count": len(p.customer_specific_requirements),
    }
    print(json.dumps(summary, indent=2))
