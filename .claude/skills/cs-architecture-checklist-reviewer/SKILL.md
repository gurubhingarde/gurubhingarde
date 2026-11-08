---
name: cs-architecture-checklist-reviewer
description: Run a confirmation-measures review on any AUTOSAR CS Architecture xlsx and produce a completed checklist (TOMCO-style) with auto-filled findings, evidence references, recommended actions, and roll-up statistics. Probes the source CS Architecture workbook (works on cs-architecture-builder outputs and best-effort on others), runs 42 standard checklist requirements split across Confirmation Review (14 generic doc-quality checks), Functional Safety Assessment (14 CS Architecture substantive checks covering elements, crypto, key management, secure boot, communication, access control), and Verification Assessment (14 verification checks). Auto-fills FC, LC, PC, NO, or NA for machine-verifiable checks and drafts low-confidence findings for subjective items. Does not modify the source document. Use this skill whenever the user wants to review, audit, assess, or confirm a CS Architecture workbook. Always use this skill instead of producing a freeform review in chat.
---

# CS Architecture Checklist Reviewer

This skill turns the audit and review of CS Architecture workbooks into a one-shot run that produces an audit-ready checklist xlsx with findings, evidence pointers, and recommended actions.

The skill is opinionated about what to check (confirmation review per AUTOSAR Security and ISO 26262) and conservative about what to assert. Every Fully-Compliant judgment cites specific evidence from the source document. Every subjective check is drafted with a "(Reviewer to verify)" preface so the human knows where judgment is required. The skill never modifies the source document; gaps land in Recommended Actions.

## When to use this skill

Use whenever the user wants to:
- Review or audit a CS Architecture workbook
- Produce a confirmation-measures checklist
- Run a security architecture assessment on a CS Architecture document
- Get a roll-up of document quality and substantive coverage
- Verify compliance with AUTOSAR Security Specification

## Workflow

### Step 1 — Get the CS Architecture path

Ask the user for the CS Architecture xlsx path. If they upload a folder, scan for *.xlsx files and ask which is the CS Architecture.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <cs_arch.xlsx> <output_checklist.xlsx>
python scripts/recalc.py <output_checklist.xlsx>      # optional
```

The script prints a JSON summary including counts of FC/LC/PC/NO/NA/PENDING per tab so you immediately see auto-fill yield.

### Step 3 — Walk the user through the review

The checklist xlsx has 7 tabs. Direct the user's attention in this order:

1. **Title** — confirm the CS Architecture being assessed is the right one.
2. **Summary** — read the statistics and the Findings (NO and PC) list. This is the executive view.
3. **Confirmation Review** — focus on rows with Assessment = "—" (pending) or "NO". These usually point at missing title-page fields or missing revision history.
4. **Functional Safety Assessment** — focus on rows with Assessment = "PC" or "NO". These are the substantive gaps. Pending rows typically need the human to verify against external specifications or apply judgment.
5. **Verification Assessment** — many rows will be Pending because they refer to external Verification Plan / Spec / Report. Focus on the completeness and alignment checks.

For each Pending row the reviewer accepts or refines the drafted finding and sets the Assessment value. For each PC or NO row, the reviewer reads the Recommended Action, decides whether to update the source CS Architecture, and re-runs the skill.

### Step 4 — Iterate

When the user updates the CS Architecture and re-runs the skill:
- The new checklist is produced fresh; the skill does not preserve manual edits to the previous checklist.
- Recommended workflow: keep the old checklist for diff comparison, run a new one each time the document changes.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | CS Architecture being assessed; reviewer info |
| 2 | General Info | TOC of the checklist |
| 3 | Guide | How to interpret ratings, confidence, obligations |
| 4 | Summary | Statistical roll-up + Findings list (NO + PC items) |
| 5 | Confirmation Review | 14 generic document-quality checks |
| 6 | Functional Safety Assessment | 14 CS Architecture substantive checks (elements, crypto, key mgmt, secure boot, communication, access control) |
| 7 | Verification Assessment | 14 verification and external artifact checks |

## Common pitfalls to flag

1. **Checklist is not a substitute for independent review.** AUTOSAR and ISO 26262 require confirmation reviews to be performed by an independent team. The skill is a workbench, not the reviewer.
2. **Many VA rows pending is normal.** Most VA checks reference external Verification Plan or Specification documents that live outside the xlsx. They are correctly marked Pending.
3. **NO rows usually point at title-page hygiene.** The most common NO findings are missing Title-page fields (Author, Approver, Status). These are easy fixes.
4. **The skill does not modify the source CS Architecture.** All corrective actions go in the Recommended Actions column. The analyst decides whether to update the document and re-run.

## Files in this skill

```
cs-architecture-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── cs_arch_probe.py             # CS Architecture content extractor
│   ├── check_definitions.py         # canonical check definitions
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── cs_architecture_checks.md
```
