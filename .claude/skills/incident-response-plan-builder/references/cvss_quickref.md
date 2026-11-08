# CVSS 3.1 Quick Reference

## Common Vulnerability Scoring System (CVSS) v3.1

CVSS provides a standardized method for assessing vulnerability severity on a scale of 0.0 to 10.0.

### Base Metrics

The base score combines three metric groups:

#### Attack Vector (AV)
- **Network (N)** — Vulnerability exploitable remotely without physical access. Add +2 to score.
- **Adjacent (A)** — Requires network adjacency (local network only). Add +1.
- **Local (L)** — Requires local access to system. Add 0.
- **Physical (P)** — Requires physical contact. Add -1.

#### Attack Complexity (AC)
- **Low (L)** — No specialized conditions needed to exploit.
- **High (H)** — Requires specialized conditions (e.g., specific hardware version, race condition).

#### Privileges Required (PR)
- **None (N)** — No authentication or special privilege needed.
- **Low (L)** — Attacker must have low-level privileges (e.g., user account).
- **High (H)** — Attacker must have high privileges (e.g., admin, root).

#### User Interaction (UI)
- **None (N)** — Exploitation does not require user action.
- **Required (R)** — Victim must take an action (click link, open attachment).

#### Scope (S)
- **Unchanged (U)** — Vulnerability affects only the vulnerable component.
- **Changed (C)** — Vulnerability can affect resources beyond the vulnerable component.

#### Confidentiality Impact (C)
- **None (N)** — No loss of confidentiality.
- **Low (L)** — Limited information disclosure (non-sensitive data).
- **High (H)** — Total information disclosure (all data accessible).

#### Integrity Impact (I)
- **None (N)** — No modification of data or system.
- **Low (L)** — Limited ability to modify data (non-critical).
- **High (H)** — Complete compromise of integrity (attacker can modify all data).

#### Availability Impact (A)
- **None (N)** — No impact on availability.
- **Low (L)** — Reduced performance or availability of non-critical service.
- **High (H)** — Complete loss of availability (denial of service).

### Severity Rating by CVSS Score

| CVSS Score | Severity | Description | Automotive Example |
|---|---|---|---|
| 9.0–10.0 | **Critical** | Immediate action required; maximum impact | Remote code execution in braking system; authentication bypass affecting all vehicles |
| 7.0–8.9 | **High** | Urgent response needed; significant impact | Privilege escalation in steering control; denial of service in gateway |
| 4.0–6.9 | **Medium** | Important to address; moderate impact | Information disclosure of VIN; limited privilege escalation |
| 0.1–3.9 | **Low** | Should be addressed; minimal impact | Non-critical DoS; minor configuration issue |

### CVSS Vector Notation

CVSS is expressed as a vector string for reproducibility:

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
```

Breaking this down:
- **AV:N** — Network attack vector (remote)
- **AC:L** — Low attack complexity
- **PR:N** — No privileges required
- **UI:N** — No user interaction
- **S:C** — Scope changed (affects other systems)
- **C:H** — High confidentiality impact
- **I:H** — High integrity impact
- **A:H** — High availability impact

This example represents a critical vulnerability (9.9 score).

### Automotive CVSS Examples

#### Example 1: Remote Keyless Entry Code Clone
- **Vector**: `CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N`
- **Score**: 7.8 (High)
- **Rationale**: 
  - AV:A — Attacker must be physically near vehicle (adjacent network).
  - AC:L — Attack is straightforward.
  - PR:N — No credentials needed.
  - UI:N — No user interaction.
  - S:C — Attacker can unlock door or start engine.
  - C:H — Can clone unique device code.
  - I:L — Cannot modify permanent vehicle settings.
  - A:N — No availability impact.

#### Example 2: OBD-II Port Remote Access
- **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`
- **Score**: 9.9 (Critical)
- **Rationale**:
  - AV:N — Accessible over vehicle network (can reach OBD port).
  - AC:L — No special conditions.
  - PR:N — No authentication.
  - UI:N — No user action needed.
  - S:C — Can compromise other vehicle systems via OBD.
  - C:H — Can read all diagnostic data.
  - I:H — Can reprogram ECUs.
  - A:H — Can disable vehicle systems.

#### Example 3: Customer Data Leak via V2X Message
- **Vector**: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Score**: 7.5 (High)
- **Rationale**:
  - AV:N — Accessible remotely via V2X network.
  - AC:L — Simple interception.
  - PR:N — No authentication needed.
  - UI:N — No user action.
  - S:U — Only affects the vehicle (data is customer-specific).
  - C:H — Complete disclosure of driver location history, preferences.
  - I:N — Cannot modify data.
  - A:N — No service disruption.

### Remediation Guidance by Severity

| Severity | Timeline | Action | Example |
|---|---|---|---|
| Critical | 1–7 days | Emergency patch release; mandatory customer notification; possible recall | Stop shipping affected version; develop emergency firmware; deploy OTA immediately |
| High | 7–30 days | Urgent patch; technical bulletin; customer communication | Include in next scheduled OTA; notify affected customer segment; coordinate disclosure |
| Medium | 30–90 days | Regular patch cycle; security bulletin; optional customer notice | Include in next quarterly release; post in security portal; notify interested customers |
| Low | 90+ days | Next routine release; internal documentation; optional customer mention | Document in known issues; include in next release notes |

---

**Reference**: FIRST.org CVSS v3.1 Specification
https://www.first.org/cvss/v3.1/specification-document
