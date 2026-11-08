---
name: secure-coding-guidelines-checklist-reviewer
description: Run a confirmation-measures review on any Secure Coding Guidelines xlsx and produce a completed checklist with auto-filled findings, evidence references, recommended actions, and statistics. Runs 42 standard checks across Confirmation Review (14 generic doc-quality), Secure Coding Guidelines Assessment (14 scope/rules/memory/integer/string/crypto/auth/logging/CWE/tool/deviation checks), and Verification Assessment (14 verification checks). Auto-fills FC, LC, PC, NO, or NA ratings. Does not modify source document. Use this skill whenever the user wants to review, audit, assess, or confirm a Secure Coding Guidelines workbook. Always use this skill instead of producing a freeform review.
---

# Secure Coding Guidelines Checklist Reviewer

This skill turns the audit of Secure Coding Guidelines workbooks into a one-shot run that produces an audit-ready checklist with findings, evidence pointers, and recommended actions.

The skill checks scope definition, coding rules catalog completeness (>= 30 typical), CERT C/MISRA coverage, CWE Top 25 mapping, memory/integer/string safety rules, cryptography rules (no deprecated algorithms), authentication principles, logging rules (no secrets/PII), tool configurations (Coverity/CodeSonar/Polyspace), and deviation process documentation.

## When to use this skill

Use whenever the user wants to review, audit, assess, or confirm a Secure Coding Guidelines workbook addressing ISO/SAE 21434, CERT C, MISRA, AUTOSAR C++14, or CWE coverage requirements.

## Workflow

### Step 1 — Get the guidelines path

Ask the user for the Secure Coding Guidelines xlsx path.

### Step 2 — Generate the checklist

```bash
python scripts/generate_checklist.py <guidelines.xlsx> <output_checklist.xlsx>
```

### Step 3 — Review tabs in order

1. **Title** — confirm the guidelines being assessed
2. **Summary** — read statistics and Findings list
3. **Confirmation Review** — focus on NO rows
4. **Secure Coding Guidelines Assessment** — focus on PC/NO rows (substantive gaps)
5. **Verification Assessment** — focus on completeness and tool/process verification

### Step 4 — Iterate

When updates are made, re-run the script to produce a fresh checklist.

## Output structure (7 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Guidelines being assessed; reviewer info |
| 2 | General Info | TOC and conventions |
| 3 | Guide | How to interpret ratings |
| 4 | Summary | Dashboard with findings |
| 5 | Confirmation Review | 14 document-quality checks |
| 6 | Secure Coding Guidelines Assessment | 14 guidelines substantive checks |
| 7 | Verification Assessment | 14 verification checks |

## Files in this skill

```
secure-coding-guidelines-checklist-reviewer/
├── SKILL.md
├── scripts/
│   ├── generate_checklist.py
│   ├── sec_coding_probe.py
│   ├── check_definitions.py
│   ├── recalc.py
│   └── office/soffice.py
└── references/
    ├── methodology.md
    └── scg_checks.md
```
