---
name: hsi-checklist-reviewer
description: Review any ISO 26262 HSI Specification xlsx and produce a checklist with findings, evidence references, recommended actions, and visual dashboard. Probes source HSI workbook (works on hsi-builder outputs and others), runs 34 checklist items across Confirmation Review (14 doc-quality checks), HSI Assessment (14 substantive checks per ISO 26262-4/5), and Verification Assessment (5 HSI-specific verification checks). Auto-fills FC/LC/PC/NO/NA for machine-verifiable checks, drafts low-confidence findings for subjective items. Does not modify source HSI. Use when user wants to review, audit, or assess any HSI Specification, or asks for HSI confirmation review or checklist.
---

# HSI Specification Checklist Reviewer

This skill automates the confirmation-measures review of ISO 26262 HSI Specifications — the part that asks you to open the xlsx, scroll through all signals, registers, timing rows, and failure modes checking that every signal has direction, encoding, owner, integrity protection, test cases, and ASIL allocation.

The skill:
- Probes the HSI content (hsi-builder format + best-effort on others).
- Runs 34 canonical checklist requirements with project-specific verification logic.
- For machine-verifiable checks: fills assessment, finding, page/section, recommended action.
- For subjective checks: drafts a finding marked Low confidence; reviewer accepts or edits.
- Writes a 7-tab xlsx (Title, General Info, Guide, Summary, Confirmation Review, HSI Assessment, Verification Assessment).

## When to use this skill

Use whenever the user wants to:
- Review or audit an HSI Specification workbook
- Produce a confirmation-measures checklist
- Run a doc-quality assessment on HSI
- Get a roll-up of HSI quality (gaps, missing signal attributes, incomplete sections)

## Workflow

### Step 1 — Get the HSI path

Ask the user for the HSI xlsx path. If they upload a folder, scan for `*.xlsx` and ask which is the HSI Specification.

### Step 2 — Generate the checklist

```bash
cd scripts
python generate_checklist.py <hsi.xlsx> <output_checklist.xlsx>
python recalc.py <output_checklist.xlsx>  # optional; surfaces any errors
```

The script prints a JSON summary with signal count, tab counts, and rating distribution.

### Step 3 — Walk the user through the review

Direct user attention in this order:

1. **Title** — confirm correct HSI Specification.
2. **Summary** — read statistics and Findings (NO and PC items).
3. **Confirmation Review** — focus on Assessment = "—" (pending) or "NO". Usually doc-quality issues.
4. **HSI Assessment** — focus on PC or NO. These are substantive gaps (missing signal attrs, timing specs, test cases, ASIL).
5. **Verification Assessment** — mostly Pending; requires external docs. Focus on any NO/PC.

### Step 4 — Iterate

When user updates HSI and re-runs:
- Generate fresh checklist (skill does not preserve edits from previous run).
- Compare old and new checklists for progress.

## Output structure (7 tabs)

| Tab | Purpose |
|-----|---------|
| Title | HSI being assessed; reviewer info |
| General Info | TOC and references |
| Guide | How to interpret ratings and obligations |
| Summary | Statistical roll-up with KPIs, pie chart, findings table |
| Confirmation Review | 14 generic doc-quality checks (ISO 26262-8 §10) |
| HSI Assessment | 14 substantive checks (signal catalog, attributes, timing, test cases, ASIL per ISO 26262-4/5) |
| Verification Assessment | 5 HSI-specific verification checks |

## Auto-fill confidence

- **High**: Verified directly from xlsx (signal count, revision, author, direction populated, ASIL set, timing rows present).
- **Medium**: Inferred from xlsx with caveat (signal encoding adequate, timing complete, test cases adequacy).
- **Low / draft**: Subjective or requires external artifact (scope coverage, consistency with TSC, diagnostics adequacy).

## Scoring model

| Rating | Meaning |
|--------|---------|
| FC | Fully Compliant — evidence found, requirement satisfied |
| LC | Largely Compliant — mostly correct, minor gaps |
| PC | Partially Compliant — significant gaps identified |
| NO | Not Compliant — requirement not met; corrective action recommended |
| NA | Not Applicable — check does not apply |
| — | Pending — requires reviewer judgment |

## Common findings

1. **Missing signal attributes** — signals present but direction, data type, bit width, owner, or ASIL not populated. Fix: complete the HSI Signal Catalog tab.
2. **Incomplete timing spec** — sample rate, max age, or latency budget missing. Fix: populate Timing Specification tab.
3. **No failure modes** — signal has no documented failure modes or reactions. Fix: add to Failure Modes & Reactions tab.
4. **Test coverage gaps** — signals without test cases. Fix: add nominal, fault, boundary, and timing test cases.
5. **Missing integrity protection** — safety-relevant signals lack Parity/CRC/SECDED/Dual-channel. Fix: specify in Signal Catalog Integrity Protection column.

## Files in this skill

```
hsi-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py        # orchestrator + xlsx writer
│   ├── hsi_probe.py                 # HSI content extractor
│   ├── check_definitions.py         # canonical check list
│   ├── dashboard.py                 # Summary tab visualizations
│   ├── recalc.py
│   └── office/
└── references/
    ├── methodology.md
    └── hsi_checks.md
```
