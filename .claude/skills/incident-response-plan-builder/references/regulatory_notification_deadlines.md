# Regulatory Notification Deadlines

## Overview

Different regulatory frameworks govern cybersecurity incident notification in the automotive industry. Organizations must track multiple jurisdictions and meet overlapping deadlines.

## UN R155 (ECE Cybersecurity Regulation)

**Jurisdiction**: European Economic Community (EEC) and broader ECE adoption.

**Applicability**: All vehicle manufacturers and suppliers operating in EU/ECE regions.

**Definition**: "Cybersecurity incidents" include unauthorized access, data modification, denial of service, or exploitation affecting vehicle cybersecurity requirements.

**Trigger Criteria**:
- Confirmed cybersecurity incident affecting one or more cybersecurity requirements.
- Incident has occurred in real-world field conditions (not just lab findings).
- Potential for safety impact or widespread customer exposure.

**Notification Deadline**: **72 hours** from discovery of the incident.

**Recipient**: 
- National ECE authority for each affected country.
- Other EU member state authorities as applicable.
- European Commission (for coordinated incidents).

**Content Required**:
1. Incident description (what was exploited, what was the attacker's objective).
2. Scope and timeline (affected vehicles, date range, ongoing vs. resolved).
3. Cybersecurity requirement(s) affected (per ISO/SAE 21434 §11 security requirements).
4. Remediation plan and timeline (patch release, rollout schedule, expected completion).
5. Customer impact assessment (how many vehicles, what data/functions compromised).
6. Public communication plan (if applicable).

**Notification Form**: Standard ECE template (available via national regulatory authority).

**Follow-up**: Quarterly status reports until incident is fully resolved.

---

## ENISA (EU Cybersecurity Act)

**Jurisdiction**: European Union (27 member states).

**Applicability**: Organizations classified as "essential entities" or "important entities" under NIS2 Directive; includes critical automotive infrastructure and large OEMs.

**Definition**: "Personal data breach" or "security incident" affecting confidentiality, integrity, or availability.

**Trigger Criteria**:
- Incident involving personal data (customer names, VINs, location history).
- Material security incident affecting operational resilience.
- Incident likely to cause "material harm" to individuals or organization.

**Notification Deadline**:
- To competent authority: **72 hours** from discovery.
- To affected individuals: **Without undue delay** (typically concurrent with authority notification).

**Recipient**:
- Competent national authority (e.g., data protection authority in affected country).
- Affected individuals (if personal data breach).
- Media (may be required if breach affects large number of individuals).

**Content Required**:
1. Nature of breach (what data, how was it accessed).
2. Categories of data subjects and approximate numbers.
3. Likely consequences of breach.
4. Technical measures and organizational measures taken or proposed.
5. Contact details of data protection officer or responsible person.
6. Measures to mitigate harm and prevent recurrence.

**Notification Form**: ENISA template or national data protection authority form.

**Follow-up**: Maintain communication with authority; provide investigation updates and final report within 30 days.

---

## NHTSA (US National Highway Traffic Safety Administration)

**Jurisdiction**: United States federal motor vehicle safety standards.

**Applicability**: Vehicle manufacturers and suppliers selling in US market; applies to safety-related defects.

**Definition**: A defect is a "failure to comply with a FMVSS (Federal Motor Vehicle Safety Standard)" or a safety-related malfunction.

**Trigger Criteria**:
- Cybersecurity incident results in safety-related defect (e.g., loss of braking, steering, visibility).
- Incident affects more than one vehicle (or represents design defect affecting production fleet).
- Manufacturer becomes aware through any means (customer complaints, internal testing, third-party report).

**Notification Deadline**:
- NHTSA Safety Defect Report (SDR): **No later than 5 business days** after determination that defect exists.
- Note: Discovery timeline may be earlier (incident occurs, manufacturer becomes aware, performs verification testing).

**Recipient**: 
- NHTSA Office of Defects Investigation (ODI).
- Optional: Public statement via press release (manufacturer discretion if proactive).

**Content Required**:
1. Description of defect (what is the safety issue, how does it occur).
2. Vehicles affected (model year, model name, production/sale dates, estimated number).
3. Safety consequences (what happens when defect occurs, potential injury).
4. Known number of complaints, injuries, or deaths related to defect.
5. Remedy (what is the fix, timeline for availability).
6. Risk of regulatory non-compliance (FMVSS citation if applicable).

**Notification Form**: NHTSA Form 570 (Safety Defect Report).

**Follow-up**: 
- Provide updates on remedy development and availability.
- Report quarterly on remedy take-rate and effectiveness.
- Submit final status once remedy is complete.

---

## JAMA (Japan Automobile Manufacturers Association)

**Jurisdiction**: Japan and Japanese domestic market.

**Applicability**: Vehicle manufacturers and suppliers with Japan market sales or manufacturing operations.

**Definition**: "Security incident" affecting vehicle safety systems or customer data.

**Trigger Criteria**:
- Cybersecurity vulnerability or incident confirmed in production vehicles.
- Incident affects cybersecurity or safety systems.
- Incident may require customer action or communication.

**Notification Deadline**: **7 calendar days** from discovery.

**Recipient**: 
- Japan Automobile Manufacturers Association (JAMA).
- Ministry of Land, Infrastructure, Transport and Tourism (MLIT).
- Optional: Individual customers (if personal data breach).

**Content Required**:
1. Incident description (in Japanese or English with Japanese translation).
2. Affected vehicles (model name, year, production range, estimated units).
3. Timeline and scope (when discovered, how long exploit was possible, how many vehicles affected).
4. Remediation plan and timeline (patch development, rollout schedule).
5. Workaround or interim measures (if any).
6. Customer communication plan.

**Notification Form**: JAMA template or MLIT incident report form (Japanese).

**Follow-up**: Provide updates at 30, 60, and 90 days; final report upon resolution.

---

## CCAS (China Cybersecurity Association / CNCERT/CC)

**Jurisdiction**: People's Republic of China.

**Applicability**: Vehicle manufacturers and suppliers with China market sales or manufacturing; critical infrastructure protection under CAC (Cyberspace Administration of China).

**Definition**: Cybersecurity incident affecting vehicle systems, customer data, or critical infrastructure.

**Trigger Criteria**:
- Confirmed cybersecurity vulnerability in production vehicles sold in China.
- Incident has or may have impact on public safety or customer privacy.
- Incident affects critical vehicle systems (braking, steering, power).

**Notification Deadline**: **7 calendar days** from discovery.

**Recipient**: 
- National Computer Network Emergency Response Technical Team/Coordination Center (CNCERT/CC).
- Cyberspace Administration of China (CAC) if critical infrastructure.
- Local public security authority.

**Content Required**:
1. Incident description (in Chinese or English with Chinese translation).
2. Affected vehicles (model, year, production range, estimated units in China).
3. Technical details of vulnerability (CVSS score, attack vector, impact).
4. Timeline (when discovered, when first affected users reported, expected patch date).
5. Remediation plan (patch details, rollout plan, timeline).
6. Risk mitigation measures (interim workarounds, user guidance).
7. Estimated economic and social impact.

**Notification Form**: CNCERT/CC incident report form (Chinese).

**Follow-up**: Provide updates every 14 days until incident is fully resolved; final impact assessment within 30 days of closure.

---

## Comparative Notification Timeline

| Regulator | Jurisdiction | Deadline | Trigger | Content Type |
|---|---|---|---|---|
| **UN R155** | EU/ECE | 72 hours | Cybersecurity incident affecting requirements | Incident desc, scope, remedy plan, customer impact |
| **ENISA** | EU (NIS2) | 72 hours | Personal data breach or material incident | Breach details, data subjects, mitigation measures |
| **NHTSA** | US | 5 business days | Safety-related defect | Defect desc, vehicles affected, remedy plan |
| **JAMA** | Japan | 7 days | Confirmed incident in production vehicles | Incident desc (Japanese), models, remedy timeline |
| **CCAS** | China | 7 days | Cybersecurity incident in production | Incident desc (Chinese), technical details, mitigation |

## Multi-Jurisdiction Overlap Example

A vulnerability in an electric steering control system affects:
- **Vehicles sold in Germany, France, Italy** — UN R155 applies (72h deadline)
- **Vehicles in EU with customer data involved** — ENISA applies (72h deadline)
- **Vehicles sold in US** — NHTSA applies (5 business days)
- **Vehicles sold in Japan** — JAMA applies (7 days)
- **Vehicles sold in China** — CCAS applies (7 days)

**Coordinated Response**:
1. **T=0 hours** — Incident confirmed; initiate PSIRT response.
2. **T=6 hours** — Severity assessed (Critical); determine regulatory scope.
3. **T=12 hours** — Prepare notifications for UN R155 and ENISA (72h deadline).
4. **T=24 hours** — Draft notifications; legal review.
5. **T=48 hours** — Submit UN R155 and ENISA notifications (meets 72h SLA).
6. **T=72 hours** — Begin work on NHTSA Form 570 (5-day deadline).
7. **T=96 hours** — Submit NHTSA notification.
8. **T=120 hours** — Submit JAMA and CCAS notifications (7-day deadline).

All notifications use same incident description; each regulatory form is translated and contextualized per jurisdiction.

---

## Post-Notification Obligations

Once initial notification is submitted, organizations must:

1. **Provide Updates** — Regular (weekly or bi-weekly) status reports to all regulatory bodies until incident is resolved.
2. **Customer Communication** — Maintain transparency with affected customers; provide technical guidance.
3. **Root Cause Analysis** — Provide findings and corrective actions within 30–60 days (varies by regulator).
4. **Prevention Measures** — Demonstrate process improvements to prevent similar incidents.
5. **Closure Report** — Final summary of incident timeline, remediation effectiveness, and lessons learned.

---

## Regulatory Contacts

**UN R155 / ECE**
- National authority for each ECE member state.
- UNECE Secretariat: [https://unece.org](https://unece.org)

**ENISA**
- National data protection authority (DPA) in each EU member state.
- ENISA: [https://www.enisa.europa.eu](https://www.enisa.europa.eu)

**NHTSA (US)**
- Office of Defects Investigation (ODI)
- Website: [https://www.nhtsa.gov](https://www.nhtsa.gov)
- Phone: 1-888-327-4236

**JAMA (Japan)**
- Japan Automobile Manufacturers Association
- Website: [https://www.jama.or.jp](https://www.jama.or.jp)

**CCAS / CNCERT/CC (China)**
- China Cybersecurity Association
- CNCERT/CC: [https://www.cert.org.cn](https://www.cert.org.cn)
