"""
Fault tree visual renderer.

Reads a structured per-SG fault tree (top event, intermediates, basic events)
and renders a PNG (and SVG) using Graphviz, in standard FTA notation.

Visual conventions (informed by IEC 61025 / NUREG-0492; simplified for clarity):

- Top event:           red-filled rectangle with white bold text
- OR gate:             yellow shield/ellipse labeled "OR"
- AND gate:            blue ellipse labeled "AND"  (not used in default tree, but supported)
- Intermediate event:  light-blue rectangle
- Basic event:         light-gray circle
- Edge labels:         none (the gate carries the semantics)

Standalone usage (rare):
    python fault_tree_renderer.py <fsc.xlsx> <output_dir>

The xlsx must be a fsc-builder output containing tab "04_FTA_Combined".
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from graphviz import Digraph
from openpyxl import load_workbook


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

STYLE_TOP = {
    "shape": "box",
    "style": "filled,rounded",
    "fillcolor": "#C00000",
    "fontcolor": "white",
    "fontname": "Helvetica-Bold",
    "fontsize": "12",
    "margin": "0.2,0.15",
    "penwidth": "1.5",
}

STYLE_INTERMEDIATE = {
    "shape": "box",
    "style": "filled,rounded",
    "fillcolor": "#D9E2F3",
    "fontcolor": "#1F3864",
    "fontname": "Helvetica-Bold",
    "fontsize": "11",
    "margin": "0.18,0.12",
    "penwidth": "1.0",
}

STYLE_OR_GATE = {
    "shape": "invhouse",
    "style": "filled",
    "fillcolor": "#FFE699",
    "fontcolor": "#7F5F00",
    "fontname": "Helvetica-Bold",
    "fontsize": "11",
    "margin": "0.05,0.05",
    "width": "0.9",
    "height": "0.7",
}

STYLE_AND_GATE = {
    "shape": "house",
    "style": "filled",
    "fillcolor": "#BDD7EE",
    "fontcolor": "#1F3864",
    "fontname": "Helvetica-Bold",
    "fontsize": "11",
    "margin": "0.05,0.05",
}

STYLE_BASIC_EVENT = {
    "shape": "circle",
    "style": "filled",
    "fillcolor": "#F2F2F2",
    "fontcolor": "#404040",
    "fontname": "Helvetica",
    "fontsize": "9",
    "margin": "0.05,0.05",
    "width": "1.6",
    "fixedsize": "true",
}


def _wrap(text: str, width: int = 28) -> str:
    """Wrap long labels onto multiple lines for readability inside a node."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > width and current:
            lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return "\\n".join(lines)


# ---------------------------------------------------------------------------
# Tree representation
# ---------------------------------------------------------------------------

class FaultTree:
    def __init__(self, sg_id: str, sg_text: str, asil: str):
        self.sg_id = sg_id
        self.sg_text = sg_text
        self.asil = asil
        # intermediates: list[(intermediate_code, intermediate_text, gate_type, [basic events])]
        self.intermediates: list[tuple[str, str, str, list[tuple[str, str, str]]]] = []

    def add_intermediate(self, code: str, label: str, gate: str = "OR") -> None:
        self.intermediates.append((code, label, gate, []))

    def add_basic_event(self, intermediate_code: str, be_code: str, label: str, node_id: str) -> None:
        for code, _, _, basics in self.intermediates:
            if code == intermediate_code:
                basics.append((be_code, label, node_id))
                return
        raise KeyError(f"Intermediate {intermediate_code} not found in tree {self.sg_id}")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_fault_tree(tree: FaultTree, output_basename: Path | str, formats: Iterable[str] = ("png", "svg")) -> dict[str, str]:
    """
    Render a fault tree to PNG and SVG. Returns dict {format: path}.
    output_basename: path WITHOUT extension; the function appends .png and .svg.
    """
    output_basename = Path(output_basename)
    output_basename.parent.mkdir(parents=True, exist_ok=True)

    g = Digraph(comment=f"Fault Tree for {tree.sg_id}")
    g.attr(rankdir="TB", nodesep="0.45", ranksep="0.55", bgcolor="white")
    g.attr("graph", label=f"Fault Tree — {tree.sg_id} (ASIL {tree.asil})", labelloc="t", fontname="Helvetica-Bold", fontsize="14")

    # Top event
    top_id = f"{tree.sg_id}__top"
    g.node(top_id, label=_wrap(f"{tree.sg_id}\\nViolation: {tree.sg_text}"), **STYLE_TOP)

    # OR gate beneath top event (the standard top-level OR)
    top_gate_id = f"{tree.sg_id}__top_or"
    g.node(top_gate_id, label="OR", **STYLE_OR_GATE)
    g.edge(top_gate_id, top_id, arrowhead="none")

    # Intermediates
    for code, label, gate_type, basics in tree.intermediates:
        int_id = f"{tree.sg_id}__{code}"
        g.node(int_id, label=_wrap(label), **STYLE_INTERMEDIATE)
        g.edge(int_id, top_gate_id, arrowhead="none")

        # Gate beneath intermediate
        gate_id = f"{int_id}__gate"
        gate_style = STYLE_AND_GATE if gate_type.upper() == "AND" else STYLE_OR_GATE
        g.node(gate_id, label=gate_type.upper(), **gate_style)
        g.edge(gate_id, int_id, arrowhead="none")

        # Basic events
        if not basics:
            placeholder_id = f"{int_id}__none"
            g.node(placeholder_id, label="(no\\nbasic events)", **{**STYLE_BASIC_EVENT, "fillcolor": "#FFF2CC"})
            g.edge(placeholder_id, gate_id, arrowhead="none")
        else:
            for be_code, be_label, node_id in basics:
                be_id = f"{tree.sg_id}__{be_code}"
                circle_label = f"{node_id}\\n{_wrap(be_label, width=18)}"
                g.node(be_id, label=circle_label, **STYLE_BASIC_EVENT)
                g.edge(be_id, gate_id, arrowhead="none")

    paths: dict[str, str] = {}
    for fmt in formats:
        # cleanup=False because some mounted filesystems disallow deletion of the
        # intermediate .gv source file. We tolerate the leftover.
        rendered = g.render(filename=str(output_basename), format=fmt, cleanup=False)
        paths[fmt] = rendered
    # Best-effort cleanup of the intermediate dot source
    src = Path(str(output_basename))
    if src.exists():
        try:
            src.unlink()
        except OSError:
            pass
    return paths


# ---------------------------------------------------------------------------
# Build trees from FSC xlsx
# ---------------------------------------------------------------------------

def trees_from_fsc_xlsx(fsc_xlsx_path: str | Path) -> list[FaultTree]:
    """Read 04_FTA_Combined and 02_SGs_From_HARA, reconstruct one FaultTree per SG."""
    wb = load_workbook(fsc_xlsx_path, data_only=True)
    if "04_FTA_Combined" not in wb.sheetnames:
        raise ValueError("FSC xlsx missing '04_FTA_Combined' tab.")

    # Map SG_ID → ASIL from 02_SGs_From_HARA
    sg_meta: dict[str, dict[str, str]] = {}
    if "02_SGs_From_HARA" in wb.sheetnames:
        ws = wb["02_SGs_From_HARA"]
        for r in range(5, ws.max_row + 1):
            sg = ws.cell(r, 1).value
            if sg and str(sg).startswith("SG-"):
                sg_meta[str(sg)] = {
                    "asil": str(ws.cell(r, 4).value or "QM"),
                    "sg_text": str(ws.cell(r, 6).value or ""),
                }

    ws = wb["04_FTA_Combined"]
    trees: dict[str, FaultTree] = {}
    current_intermediate: dict[str, str] = {}  # sg_id -> last intermediate code seen

    for r in range(5, ws.max_row + 1):
        sg_id = ws.cell(r, 1).value
        level = ws.cell(r, 2).value
        code = ws.cell(r, 4).value
        desc = ws.cell(r, 5).value or ""
        node_id = ws.cell(r, 6).value or "—"

        if not sg_id or not str(sg_id).startswith("SG-"):
            continue
        sg_id = str(sg_id)

        if level == 0:
            meta = sg_meta.get(sg_id, {"asil": "QM", "sg_text": str(desc)})
            sg_text = meta["sg_text"] or str(desc).split(": ", 1)[-1]
            trees[sg_id] = FaultTree(sg_id=sg_id, sg_text=sg_text, asil=meta["asil"])
        elif level == 1:
            label_clean = str(desc).replace("└──", "").strip()
            trees[sg_id].add_intermediate(str(code), label_clean, gate="OR")
            current_intermediate[sg_id] = str(code)
        elif level == 2:
            int_code = current_intermediate.get(sg_id)
            if not int_code:
                continue
            be_label = str(desc).split("•", 1)[-1].strip()
            be_label = be_label.split(" causes branch")[0].strip()
            be_label = be_label.replace("Input failure of ", "").replace("Process failure of ", "").replace("Output failure of ", "")
            import re as _re
            be_label = _re.sub(r"\s*\(Node\s+\S+,\s*type=[^)]+\)\s*$", "", be_label).strip()
            trees[sg_id].add_basic_event(int_code, str(code), be_label, str(node_id))

    return list(trees.values())


def render_all_trees_for_xlsx(fsc_xlsx_path: str | Path, output_dir: str | Path, max_trees: int | None = None) -> list[dict]:
    """Convenience: build trees from xlsx and render PNG+SVG for each. Returns list of metadata dicts."""
    output_dir = Path(output_dir)
    trees = trees_from_fsc_xlsx(fsc_xlsx_path)
    if max_trees:
        trees = trees[:max_trees]
    results: list[dict] = []
    for tree in trees:
        basename = output_dir / f"FT_{tree.sg_id}"
        paths = render_fault_tree(tree, basename)
        results.append({"sg_id": tree.sg_id, "asil": tree.asil, **paths})
    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fault_tree_renderer.py <fsc.xlsx> <output_dir>", file=sys.stderr)
        sys.exit(2)
    out = render_all_trees_for_xlsx(sys.argv[1], sys.argv[2])
    print(f"Rendered {len(out)} fault trees:")
    for r in out:
        print(f"  {r['sg_id']} (ASIL {r['asil']}): {r.get('png')}")
