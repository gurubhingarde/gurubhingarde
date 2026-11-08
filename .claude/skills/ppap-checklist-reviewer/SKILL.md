---
name: ppap-checklist-reviewer
description: Review any PPAP package xlsx against AIAG PPAP 4th edition. Auto-fills checklist with 14 doc-quality (CR), 14 element-compliance (PPAPA), and 5 verification checks. Produces completion summary with visual dashboard highlighting out-of-spec dimensions, low-Cpk capability, and high-R&R gages. Does not modify source PPAP. Use when auditing, submitting, or confirming a PPAP package.
---

# PPAP Checklist Reviewer

Automates the tedious review of a Production Part Approval Process (PPAP) submission package against AIAG PPAP Manual 4th edition standards. Reads the PPAP xlsx, probes all 18 submission elements, runs 33 objective and subjective checks, and produces a checklist with findings, evidence references, and recommended actions.

The skill is opinionated about what to check (AIAG PPAP + submission-level rules) and conservative about what to assert. Every Fully-Compliant judgment cites the specific evidence found in the package. Subjective checks are drafted with "(Reviewer to verify)" so the human knows where judgment is required. The skill never modifies the source PPAP; all corrective actions go in the Recommended Actions column.

## When to use this skill

Use whenever the user wants to:
- Review or audit a PPAP submission package
- Confirm all 18 elements per AIAG submission level
- Check dimensional and process capability results
- Verify PSW signoff and customer requirements
- Produce an audit-ready checklist xlsx
- Get a roll-up of PPAP compliance status

The skill is the natural partner to `ppap-package-builder` — `ppap-package-builder` produces the artifact, `ppap-checklist-reviewer` confirms it.

## Workflow

### Step 1 — Get the PPAP path

Ask the user for the PPAP xlsx path. If they upload a folder, scan for `*.xlsx` and ask which is the PPAP.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <ppap.xlsx> <output_checklist.xlsx>
```

The script prints a JSON summary with counts (FC/LC/PC/NO/NA/Pending) and headline findings (out-of-spec dims, low Cpk, high R&R).

### Step 3 — Walk the user through the checklist

The checklist xlsx has 7 tabs. Direct attention in this order:

1. **Title** — confirm the PPAP being assessed is the right one.
2. **Summary** — read KPI tiles, pie chart, and Findings (NO + PC) table. Executive view.
3. **Confirmation Review (CR)** — 14 doc-quality checks. Focus on NO or Pending rows.
4. **PPAP Assessment (PPAPA)** — 14 element-specific checks per AIAG. This is the substance. Focus on NO or PC rows highlighting out-of-spec dims, low Cpk, high R&R gages.
5. **Verification Assessment (VA)** — 5 external references (drawing control, material certs, sample approval, FAR data, FMEA closure). Most are Pending.

For each Pending row, reviewer accepts or refines the drafted finding. For NO/PC rows, reviewer reads Recommended Action and decides whether to update source PPAP.

### Step 4 — Iterate

When user updates the PPAP and re-runs:
- New checklist is produced fresh; this skill v0.1 does not preserve manual edits.
- Recommended: keep old checklist for diff, run fresh each time.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | What PPAP is being assessed |
| 2 | General Info | TOC + References |
| 3 | Guide | Scoring guide (FC/LC/PC/NO/NA/Pending) |
| 4 | Summary | KPI dashboard + Findings table (NO + PC items) |
| 5 | Confirmation Review | 14 doc-quality checks |
| 6 | PPAP Assessment | 14 element checks per AIAG level |
| 7 | Verification Assessment | 5 external references |

## Auto-fill confidence model

| Confidence | When assigned | Examples |
|------------|---------------|----------|
| High | Verified directly from xlsx | "Part number populated", "Signature block filled" |
| Medium | Inferred from xlsx with caveat | "Elements present; reviewer to confirm submission status" |
| Low / draft | Subjective or external | "Drawing under change control" (external), "Sample approved" (external) |

Every Low-confidence draft starts with "(Auto-suggest, requires reviewer judgment)" so it is unambiguous to the reviewer that human attention is required.

## Common pitfalls

1. **Checklist is not a substitute for submission authority review.** AIAG PPAP and customer specifications require authorized personnel review. This skill is a workbench.
2. **NO rows usually point at missing fields.** Most common NO findings are missing PSW signoff, unsigned, or incomplete element references. These are quick fixes.
3. **Headline findings (out-of-spec, low Cpk, high R&R) require root-cause response.** The skill flags them; the engineer must investigate and correct.
4. **The skill does not modify the source PPAP.** All corrective actions go in Recommended Actions. Analyst decides whether to update source and re-run.

## Files in this skill

```
ppap-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py    # orchestrator + xlsx writer
│   ├── ppap_probe.py            # PPAP content extractor
│   ├── check_definitions.py     # 33 checks with verify logic
│   ├── dashboard.py             # shared dashboard renderer
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md           # scoring, confidence levels
    └── ppap_checks.md          # what each check verifies
```
