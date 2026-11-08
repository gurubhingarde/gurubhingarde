---
name: incident-response-plan-builder
description: Generate an audit-ready ISO/SAE 21434 Section 13 Incident Response Plan workbook with PSIRT roster, severity SLAs, detection sources, workflow stages, OTA patch management, regulatory notification procedures, and customer communication templates. Produces 13-tab xlsx defining team roles, incident triage classification, coordinated disclosure policy, and post-incident review templates. Use when the user mentions Incident Response Plan, PSIRT setup, vulnerability disclosure, or cybersecurity incident procedures per ISO/SAE 21434.
---

# Incident Response Plan Builder

An Incident Response Plan is the cornerstone of ISO/SAE 21434 Section 13 (Cybersecurity Incident Response). This skill produces a complete, audit-ready Incident Response Plan workbook by defining the PSIRT team, establishing severity thresholds with SLAs, documenting detection sources, detailing the six-stage response workflow (DETECT, TRIAGE, CONTAIN, ERADICATE, RECOVER, POST-MORTEM), coordinating vulnerability disclosure, managing OTA patch rollout, mapping regulatory notification requirements (UN R155, ENISA, NHTSA, JAMA), and providing customer communication templates.

The skill is opinionated about structure, not answers. Every role, SLA, and notification timeline has a placeholder ready for your organization-specific data. The Regulatory Notifications tab auto-populates deadlines and content requirements for major automotive cybersecurity frameworks, so your team meets compliance windows.

## When to use this skill

Use whenever the user wants to:
- Create or update an Incident Response Plan per ISO/SAE 21434 Section 13
- Define a PSIRT team structure and on-call schedule
- Establish vulnerability severity classification with CVSS thresholds and response SLAs
- Document vulnerability detection sources and intake procedures
- Plan the incident response workflow from detection through post-mortem
- Design a coordinated vulnerability disclosure policy with embargo periods
- Build an OTA patch rollout workflow with gates and rollback plans
- Map regulatory notification requirements (UN R155, ENISA, NHTSA, JAMA, CCAS)
- Prepare customer communication playbooks and templates
- Establish post-incident review and root cause analysis procedures

If the user asks a conceptual incident response question and does not need a deliverable, you can answer from the reference docs, but offer the workbook as the next step.

## Workflow

### Step 1 — Capture organizational context

Ask for these inputs in concise turns. The minimum viable input:

1. **Organization name and document ID** (e.g., "Acme Motors / IRP-2024-001")
2. **PSIRT Lead** name and email
3. **Target Cyber Assurance Level (CAL)** (CAL 1, 2, or 3)
4. **PSIRT roster** — Manager, Triage Engineer, Comms Lead, Legal, Engineering rep (names, roles, emails, on-call schedule)
5. **Severity thresholds** — Critical, High, Medium, Low with CVSS ranges and SLAs (response time, communication time, fix time)
6. **Regulators** relevant to your market (UN R155, ENISA, NHTSA, JAMA, CCAS)
7. **Key stakeholders** for incident escalation (Engineering leads, Legal, Comms, Customers)

### Step 2 — Read the reference docs

Before generating, read these if relevant:

- `references/methodology.md` — PSIRT lifecycle, incident stages, why each matters
- `references/cvss_quickref.md` — CVSS 3.1 base score interpretation (Critical, High, Medium, Low)
- `references/regulatory_notification_deadlines.md` — UN R155, ENISA, NHTSA, JAMA, CCAS notification windows and content

### Step 3 — Build the input JSON

Construct a JSON file conforming to the schema at the top of `scripts/generate_incident_response_plan.py`. A worked example lives in `examples/sample_incident_response_plan_esc.json` — start from it for any automotive product.

The schema is forgiving: omit any field and the script auto-populates sensible defaults (e.g., standard PSIRT roles, severity thresholds, regulatory requirements). The mandatory fields are `org.name` and `org.psirt_lead`.

### Step 4 — Generate

Run from a shell with Python and openpyxl:

```bash
python scripts/generate_incident_response_plan.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

The first command produces the workbook. The second recalculates any formulas.

### Step 5 — Present and iterate

Present the resulting xlsx and explicitly call out what to review:

- **PSIRT Roster** — Does the team structure match your organization?
- **Triage Classification** — Are the severity definitions and SLAs aligned with your risk appetite?
- **Detection Sources** — Are all your incident sources covered (disclosure researchers, customer complaints, internal scans, IDS, threat intel)?
- **Response Workflow** — Does the six-stage process (DETECT, TRIAGE, CONTAIN, ERADICATE, RECOVER, POST-MORTEM) fit your operational model?
- **OTA Patch Workflow** — Are gates, owners, and rollback procedures realistic for your vehicle architecture?
- **Regulatory Notifications** — Are deadlines and content requirements correct for your markets?
- **Customer Communications** — Do templates match your brand voice and legal requirements?

When the user asks for changes, modify the input JSON and regenerate. The xlsx is derived; the JSON is source of truth.

## Output structure (13 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 00 | Title Page | Organization, item, doc ID, PSIRT lead, contact, target CAL |
| 01 | Document Control | Revision history and release record |
| 02 | PSIRT Roster | Team members: name, role (Manager/Triage/Comms/Legal/Engineering), org, email, phone, on-call schedule |
| 03 | Triage Classification | Severity (Critical/High/Medium/Low) with CVSS thresholds, response/comm/fix SLAs, escalation triggers |
| 04 | Detection Sources | Vulnerability sources (researcher, CVE, customer, scan, IDS, threat intel, OTA) — handler, intake form, priority |
| 05 | Response Workflow | Six stages: DETECT, TRIAGE, CONTAIN, ERADICATE, RECOVER, POST-MORTEM — roles, activities, deliverables, escalation |
| 06 | Coordinated Disclosure | Researcher contact, embargo period, CVE coordination, public disclosure timing, credit policy |
| 07 | OTA Patch Workflow | Vulnerability to fix dev to test to rollout — per stage: gates, owners, rollback plan |
| 08 | Regulatory Notifications | UN R155, ENISA, NHTSA, JAMA, CCAS — trigger, deadline, content, owner |
| 09 | Customer Communications | Playbook: severity to comms channel (technical bulletin/notification/press release) and message templates |
| 10 | Post-Incident Review | Template for incident timeline, root cause analysis, lessons learned, corrective actions |
| 11 | Communication Templates | Researcher acknowledgment, CVE assignment, internal escalation, customer bulletin, press release |
| 12 | References | ISO/SAE 21434, UN R155, FIRST.org PSIRT framework, CVSS, standards |

## PSIRT roles and responsibilities

The default PSIRT roster includes:

- **PSIRT Manager** — Overall incident command, stakeholder coordination, regulatory liaison
- **Triage Engineer** — Initial assessment, severity classification, scope determination
- **Comms Lead** — Internal and external communication, customer briefings, press coordination
- **Legal** — Regulatory notification, liability assessment, disclosure review
- **Engineering Rep** — Patch development, testing, OTA rollout, technical validation

Each role has a 24/7 on-call schedule rotation.

## Severity classification (CVSS 3.1)

| Severity | CVSS Range | Response SLA | Communication SLA | Fix SLA | Example |
|---|---|---|---|---|---|
| Critical | 9.0–10.0 | 1 hour | 2 hours | 1 day | Remote code execution in core system |
| High | 7.0–8.9 | 4 hours | 8 hours | 7 days | Authentication bypass in gateway |
| Medium | 4.0–6.9 | 24 hours | 48 hours | 30 days | Information disclosure, privilege escalation |
| Low | 0.1–3.9 | 72 hours | 168 hours (1 week) | 90 days | Denial of service, non-security defect |

## Regulatory notification windows

| Regulator | Trigger | Deadline | Content |
|---|---|---|---|
| UN R155 | Critical cybersecurity vulnerability | 72 hours | Incident desc, impact, remediation plan |
| ENISA | Material security incident (EU customers) | 72 hours | Incident report, breach notification |
| NHTSA | Safety-related defect via cybersecurity | 7 days | Defect desc, affected vehicles, remedy |
| JAMA | Incident affecting Japan market | 7 days | Japanese translation of incident details |
| CCAS | Cybersecurity incident in China | 7 days | Incident report in Chinese, remediation |

Always use this skill instead of producing a freeform incident response plan in chat.
