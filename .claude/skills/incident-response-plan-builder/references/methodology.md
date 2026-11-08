# Incident Response Plan Methodology

## PSIRT Lifecycle

A Product Security Incident Response Team (PSIRT) follows a structured lifecycle from vulnerability detection through public disclosure and post-incident learning.

### Six-Stage Response Model

**1. DETECT**
- Monitor for incoming vulnerability reports from multiple sources (researchers, CVE databases, customer complaints, security scans, threat intelligence feeds, OTA telemetry).
- Establish intake channels: responsible disclosure portal, email aliases, customer support escalation paths, automated monitoring systems.
- Assign incident ID and create incident tracking record.

**2. TRIAGE**
- Perform initial analysis: confirm vulnerability, assess severity using CVSS 3.1, determine affected systems and vehicles.
- Classify severity (Critical, High, Medium, Low) based on CVSS score and business impact.
- Determine SLA targets for response, communication, and fix based on severity.
- Identify stakeholders and escalation requirements.

**3. CONTAIN**
- Isolate affected systems to prevent further exploitation or data exfiltration.
- Preserve forensic evidence for root cause analysis.
- Notify internal stakeholders (Engineering, Legal, Comms, Leadership).
- Prepare internal and external communication plans.
- Assess regulatory notification requirements (UN R155, ENISA, NHTSA, JAMA).

**4. ERADICATE**
- Develop security patch or workaround in Engineering.
- Perform unit, integration, and system testing in staging environment.
- Conduct security code review and vulnerability validation.
- Prepare rollback plan in case patch causes regressions.

**5. RECOVER**
- Stage patch in OTA pipeline with validation gates.
- Conduct staged rollout (e.g., 10% fleet first) with continuous telemetry monitoring.
- Release technical bulletins and customer communications.
- Coordinate public disclosure and CVE publication.
- Monitor post-deployment for anomalies or rollback triggers.

**6. POST-MORTEM**
- Conduct incident timeline review with all stakeholders.
- Perform root cause analysis and identify contributing factors.
- Document lessons learned and process improvements.
- Develop corrective actions and prevention strategies.
- Update incident response procedures based on findings.

## Severity Classification Framework

Severity combines CVSS base score with business and technical context:

### Critical (CVSS 9.0–10.0)
- Remote code execution in core system (powertrain, steering, braking).
- Authentication bypass affecting all users.
- Unencrypted transmission of sensitive vehicle data.
- Example: Exploit enables attacker to disable brakes remotely.
- Response: Immediate escalation, emergency patch, mandatory customer communication.

### High (CVSS 7.0–8.9)
- Privilege escalation in a critical subsystem.
- Denial of service in vehicle connectivity.
- Information disclosure of customer data.
- Example: Attacker can escalate from infotainment to engine control.
- Response: Urgent fix, communication to affected customers, coordinated disclosure.

### Medium (CVSS 4.0–6.9)
- Limited privilege escalation or non-critical DoS.
- Information disclosure in non-sensitive component.
- Authentication or encryption weakness in lower-risk function.
- Example: Vulnerability in diagnostics port allows vehicle data leak.
- Response: Scheduled patch release, customer notification, security bulletin.

### Low (CVSS 0.1–3.9)
- Denial of service in non-critical service.
- Minor information disclosure.
- Design or configuration weakness with low impact.
- Example: Non-security defect found through security analysis.
- Response: Include in next quarterly patch, customer FAQ, documentation update.

## SLA Targets

SLAs are tied to severity and represent organization commitment:

| Severity | Response SLA | Communication SLA | Fix SLA | Escalation Path |
|---|---|---|---|---|
| Critical | 1 hour | 2 hours | 1 day | PSIRT Manager → SVP Product → CEO |
| High | 4 hours | 8 hours | 7 days | PSIRT Manager → VP Engineering → SVP |
| Medium | 24 hours | 48 hours | 30 days | PSIRT Manager → Engineering Lead |
| Low | 72 hours | 1 week | 90 days | PSIRT Manager → Engineering (standard process) |

Response SLA = acknowledge receipt and assign triage engineer.
Communication SLA = internal stakeholder notification of severity and timeline.
Fix SLA = patch released to customers (critical may have temporary workaround).

## Vulnerability Disclosure

### Coordinated Disclosure Principle
Researchers and PSIRT agree on embargo period (typically 90 days) during which the vulnerability is kept confidential while a patch is developed. Public disclosure occurs simultaneously with patch availability.

### Researcher Engagement
- Acknowledge receipt within 24 hours.
- Assign a triage contact (usually Triage Engineer).
- Establish regular communication cadence (e.g., weekly updates).
- Provide patch timeline and expected disclosure date.
- Offer researcher credit if requested.

### CVE Assignment
- Contact MITRE for CVE ID during containment phase.
- Include CVSS score and remediation availability in CVE record.
- Publish in National Vulnerability Database (NVD) upon disclosure.
- Coordinate timing with patch availability.

## OTA Patch Lifecycle

Over-the-air updates enable rapid patch delivery to production vehicles:

1. **Fix Development** — Engineering develops security patch with code review.
2. **Unit & Integration Test** — QA validates patch in lab environment.
3. **Staging OTA Test** — Deploy to test fleet; validate OTA mechanism and no side effects.
4. **Pre-Production Validation** — Security team and Comms review patch and messaging.
5. **Staged Rollout** — Deploy to 10% of fleet; monitor telemetry for 24 hours.
6. **Full Production Rollout** — Deploy to all vehicles; maintain active customer communication.

Rollback plan is prepared and rehearsed for each stage.

## Regulatory Notification Framework

Different regulatory bodies have specific incident notification requirements:

### UN R155 (ECE Cybersecurity Regulation)
- Applies to all European vehicle manufacturers and suppliers.
- Requires notification to national authorities if cybersecurity incident affects "cybersecurity requirements."
- Deadline: 72 hours from discovery.
- Content: Incident description, affected systems, remediation plan, customer impact.

### ENISA (EU Cybersecurity Act)
- Applies to "essential and important entities" including critical automotive infrastructure.
- Requires breach notification to relevant authority and affected customers.
- Deadline: 72 hours from discovery.
- Content: Breach notification, impact assessment, customer communication.

### NHTSA (US National Highway Traffic Safety Administration)
- Applies to US vehicle manufacturers and safety-related systems.
- Triggered if incident is related to vehicle safety (e.g., braking, steering).
- Deadline: Safety issue requires prompt notification; typically 3–5 days.
- Content: Vehicle identification, defect description, remedy plan.

### JAMA (Japan Automobile Manufacturers Association)
- Applies to vehicles sold in Japan.
- Requires notification to JAMA and Ministry of Land, Infrastructure, Transport and Tourism (MLIT).
- Deadline: 7 days.
- Content: Japanese translation of incident details and remedy.

### CCAS (China Cybersecurity Association)
- Applies to vehicles sold in China or containing Chinese components.
- Cybersecurity incident notification to Chinese authorities.
- Deadline: 7 days.
- Content: Chinese translation of incident report and remediation.

## Post-Incident Learning

### Root Cause Analysis
Identify the primary cause of the vulnerability:
- Design flaw (e.g., weak authentication model).
- Implementation defect (e.g., buffer overflow).
- Configuration error (e.g., debug port left enabled).
- Process gap (e.g., inadequate security code review).

### Contributing Factors
Document systemic issues that enabled or hid the vulnerability:
- Insufficient security testing coverage.
- Lack of threat modeling in design phase.
- Inadequate access controls during development.
- Missing security champion on team.

### Lessons Learned
Capture what went well and what could improve:
- Did the PSIRT structure enable fast response?
- Were communication channels clear and effective?
- Did OTA rollout proceed smoothly?
- Were customers satisfied with transparency?

### Corrective Actions
Define process improvements to prevent recurrence:
- Add security requirement to future designs.
- Improve security code review checklist.
- Enhance security testing automation.
- Update threat model to include new attack vector.
- Conduct team training on identified gap.

All lessons and corrective actions are tracked and reviewed in next design cycle (ISO 26262 feedback loop).
