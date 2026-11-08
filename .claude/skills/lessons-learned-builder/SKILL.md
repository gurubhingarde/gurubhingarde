---
name: lessons-learned-builder
description: Generate an audit-ready lessons learned register workbook per ISO 26262-2 Section 5 and IATF 16949 capturing lessons from incidents, internal audits, root cause analyses, and customer returns including root cause, corrective action, recommended best practice, and applicability scope for organizational learning.
---

# Lessons Learned Builder

ISO 26262-2 Section 5 and IATF 16949 Section 10.2.4 require systematic capture and organizational dissemination of lessons learned from safety programs. This skill produces an audit-ready Lessons Learned Register workbook.

## When to use this skill

Use whenever the user wants to:
- Create or update a lessons learned register per ISO 26262-2 Section 5
- Document lessons from incidents, audits, RCAs, and customer returns
- Capture root cause analysis and recommended corrective actions
- Define applicability scope and distribution plan
- Track implementation and effectiveness of lessons
- Build organizational learning documentation

## Workflow

### Step 1 — Gather lesson inputs

Ask for:

1. **Project context and scope**
2. **Lesson sources** — incidents, internal audits, RCAs, customer returns
3. **For each lesson**: summary, root cause, recommended corrective action, best practice, applicability scope
4. **Distribution plan** — who should be aware of this lesson
5. **Application tracking** — where/how the lesson has been applied

### Step 2 — Build input JSON

Create input.json conforming to the schema in `scripts/generate_ll.py`.

### Step 3 — Generate

```bash
python scripts/generate_ll.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 4 — Present

Display the output xlsx highlighting:
- The **Lesson Catalog** tab — is each lesson clearly summarized with root cause and action?
- The **Categorization** tab — are lessons appropriately categorized (technical/process/tool/org)?
- The **Distribution Plan** tab — who needs to know about each lesson?
- The **Application Tracker** tab — where has each lesson been applied?

## Output structure (9 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Project name, document ID, lesson period, owner |
| 01 | Document Control | Revision history |
| 02 | Lesson Catalog | Rows per lesson: ID, source, summary, root cause, corrective action, best practice, applicability |
| 03 | Categorization | Lesson categories: technical, process, tool, organizational |
| 04 | Distribution Plan | Lesson ID, distribution target (group/role), delivery method, target completion |
| 05 | Application Tracker | Lesson ID, applied in (project/program), application context, application date, effectiveness rating |
| 06 | Trend Analysis | Trending of lessons by source (incident vs. audit vs. RCA) |
| 07 | Effectiveness Review | Lesson ID, effectiveness assessment (did the lesson prevent similar issues?), review date |
| 08 | References | ISO 26262-2 Section 5, IATF 16949 Section 10, organizational learning standards |

## Files in this skill

```
lessons-learned-builder/
├── SKILL.md
├── scripts/
│   ├── generate_ll.py
│   ├── recalc.py
│   └── office/
├── references/
│   └── methodology.md
└── examples/
    └── sample_lessons_learned.json
```
