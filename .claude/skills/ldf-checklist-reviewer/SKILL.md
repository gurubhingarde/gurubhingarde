---
name: ldf-checklist-reviewer
description: Run a confirmation review on any LDF specification xlsx. Systematically probes cluster definition, node attributes, frames, signals, schedule tables, and validates baud rate, signal allocation, schedule coverage, and frame publishers per ISO 17987. Produces a detailed assessment workbook with 30 checks.
---

# LDF Checklist Reviewer

A LDF confirmation review validates that a LIN Description File specification is complete, internally consistent, and ready for implementation. This skill automatically probes the xlsx structure, extracts cluster metadata, nodes, frames, signals, and schedule tables, then runs 30 systematic checks covering both document structure (presence, metadata, revision control) and technical substance (baud rate, frame publishers, signal uniqueness, schedule feasibility).

The result is a detailed assessment workbook showing:
- Pass/Fail/Partial/Not Applicable ratings with high-confidence findings
- Recommended actions for gaps
- A summary dashboard with color-coded compliance status

## When to use this skill

Use whenever the user has a completed LDF xlsx and wants to:
- Validate cluster completeness before implementation
- Confirm all nodes, frames, and signals are properly defined
- Check that schedule tables cover all required frames
- Verify baud rate compliance with LIN spec
- Prepare an LDF for design review or certification
- Audit an existing LDF against ISO 17987

## Workflow

### Step 1 — Upload or provide the LDF xlsx

Ask the user for their LDF file. If they have a Canva design or another source, they should export it to xlsx first.

### Step 2 — Run the review

```bash
python scripts/generate_checklist.py <ldf.xlsx> <checklist_output.xlsx>
```

The script will:
1. Probe the xlsx structure using `ldf_probe.py`
2. Run 30 checks via `check_definitions.py`
3. Build an assessment workbook with detailed findings

### Step 3 — Present results

Display the output xlsx and highlight:
- **Status dashboard** (color-coded summary of all checks)
- **Document Structure section** — metadata, revision control, completeness
- **Technical Assessment section** — cluster, nodes, frames, signals, schedules
- **Recommended Actions** — sorted by priority

### Step 4 — Iterate

For each recommended action, either:
- Update the source LDF xlsx and re-run the review
- Document the decision (e.g., "Not Applicable — diagnostic frames only")

## Check Categories

### Document Structure (Confirmation Review, ~14 checks)

- **CR-01** Document Structure: ≥5 tabs present
- **CR-02** Template Version: Latest LDF template version used
- **CR-03** Table of Contents: TOC tab present and navigable
- **CR-04a** Title: Clear, scope-defining cluster name
- **CR-04b** Author/Approver: Populated on Title page
- **CR-04c** Revision: Unique revision identifier
- **CR-04d** Change History: Revision log with dates and authors
- **CR-04e** Status: Draft/Review/Released/Superseded field
- **CR-05** Current Revision: Match between Title page and Document Control
- **CR-06** Configuration Management: Document stored in CM system
- **CR-07** Headers/Footers: Company logo, document ID, revision in page headers
- **CR-08** TOC Completeness: All tabs referenced
- **CR-09** Cross-References: Linked documents (FSC, HSI, etc.)
- **CR-10** Sections Complete: ≥95% of structured fields populated

### Technical Assessment (~16 checks)

#### Cluster Configuration
- **TSA-01** Cluster Metadata: Name, abbreviation, project populated
- **TSA-02** LIN Version: Valid (2.0, 2.1, 2.2A)
- **TSA-03** Baud Rate: Within 1–20 kbps range
- **TSA-04** Timing Master: Single master node assigned

#### Nodes
- **TSA-05** Master Node Defined: Name, identifier present
- **TSA-06** Slave Nodes: ≥1 slave node defined with identifier
- **TSA-07** Node Roles: Each slave has a defined function (publisher/subscriber)

#### Frames
- **TSA-08** Frame Definitions: ≥1 frame with ID, name, type, length
- **TSA-09** Frame Types: Mix of unconditional/event-triggered as required
- **TSA-10** Frame Publishers: Every frame has exactly 1 publisher
- **TSA-11** Frame Subscribers: Subscribers consistent with schedule

#### Signals
- **TSA-12** Signal Definitions: ≥1 signal with name, frame, type
- **TSA-13** Signal Allocation: Each signal in exactly 1 frame
- **TSA-14** Signal Encoding: Scaling, offset, units populated
- **TSA-15** Signal Bounds: Min/max consistent with encoding

#### Schedule Tables
- **TSA-16** Schedule Tables: ≥1 schedule defined per operational mode
- **TSA-17** Schedule Coverage: All frames present in at least 1 mode
- **TSA-18** Schedule Timing: Slots non-overlapping, total time ≤ cycle

## Output structure (2 tabs)

| Tab | Purpose |
|-----|---------|
| Summary Dashboard | Color-coded compliance overview of all 30 checks |
| Detailed Findings | Each check with rating, finding, recommended action, confidence |

## Files in this skill

```
ldf-checklist-reviewer/
├── SKILL.md                                    # this file
├── scripts/
│   ├── generate_checklist.py                   # orchestrator + xlsx writer
│   ├── ldf_probe.py                            # LDF xlsx parser
│   ├── check_definitions.py                    # 30 check implementations
│   ├── dashboard.py                            # summary dashboard builder
│   ├── recalc.py                               # LibreOffice formula recalc
│   └── office/
│       ├── __init__.py
│       └── soffice.py                          # LibreOffice helper
└── references/
    ├── methodology.md                          # LDF review methodology
    └── ldf_checks.md                           # check catalog with rationale
```
