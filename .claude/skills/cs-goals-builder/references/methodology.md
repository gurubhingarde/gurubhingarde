# Cybersecurity Goals (CSG) Derivation Methodology

## Overview

Cybersecurity Goals (CSGs) are high-level security objectives derived directly from threat scenarios identified in Threat Analysis and Risk Assessment (TARA). They follow the same conceptual pattern as safety goals in ISO 26262 HARA — each CSG is a declarative statement of what the system must prevent or protect against, anchored to a specific threat scenario and cybersecurity property.

## Derivation Process

### 1. Source: TARA Risk Determination

CSGs are derived from the risk determination phase of TARA:

- **Input**: TARA worksheet (tab 09_Risk_Determination or 11_Cybersecurity_Goals if pre-existing CSGs are available)
- **Filter**: Only threat scenarios with Risk Value >= 3 (High or Critical risk) generate CSGs
- **Mapping**: Each high-risk threat scenario generates one or more CSG(s) depending on affected assets and properties

### 2. CSG Naming Convention

CSGs follow the **Prevent <Threat>** pattern:

- **Prevent unauthorized firmware modification**
- **Prevent secure boot bypass**
- **Prevent CAN message spoofing affecting brake commands**
- **Prevent calibration data tampering**
- **Prevent debug interface unauthorized access**

The "Prevent <X>" form is imperative and unambiguous, making it clear what the security control must accomplish.

### 3. Properties and Attributes

Each CSG specifies one or more cybersecurity properties it protects:

- **Confidentiality (C)** — Data must not be disclosed to unauthorized parties
- **Integrity (I)** — Data must not be altered or corrupted by unauthorized means
- **Authenticity (Auth)** — Sender/source identity must be verifiable
- **Authorization (Authz)** — Access must be restricted to authorized entities only
- **Non-Repudiation (NR)** — Originator cannot deny sending/creating data
- **Availability (Avail)** — System services must be accessible when needed

### 4. CAL Assignment

Each CSG is assigned a Cybersecurity Assurance Level (CAL 1-4) based on:

- **Risk Value** from TARA (1-5 scale)
- **Safety Impact** of the threat if exploited
- **Feasibility** of implementing controls at that CAL

**Auto-Suggestion Logic:**
- Risk Value 5 + Severe Safety Impact → **CAL 4**
- Risk Value 4 + Significant Impact → **CAL 3**
- Risk Value 3 + Moderate Impact → **CAL 2**
- Risk Value 1-2 + Low Impact → **CAL 1**

CAL assignments are justified in the 04_CAL_Determination tab and can be refined based on project-specific context.

### 5. Traceability

Each CSG is traceable to:
- The originating threat scenario ID from TARA
- The asset(s) affected
- The cybersecurity property protected
- The CAL and its justification

The 02_TARA_Echo tab provides read-only reference to imported threats for audit purposes.

## CSG vs. Safety Goals

| Aspect | Safety Goal (HARA) | Cybersecurity Goal (TARA) |
|--------|-------------------|--------------------------|
| **Source** | Hazard analysis | Threat analysis |
| **Focus** | Accidental failures | Intentional/deliberate attacks |
| **Example** | Prevent unintended brake apply | Prevent unauthorized brake command injection |
| **Assurance Level** | ASIL (A, B, C, D) | CAL (1, 2, 3, 4) |
| **Next Phase** | Functional Safety Concept (FSC) | Cybersecurity Concept (CSC) |

## Next Steps

Once CSGs are defined and reviewed:

1. **Cybersecurity Concept (CSC) Phase** — Each CSG drives one or more CSC requirements (technical security controls)
2. **Architecture Phase** — CSC requirements are mapped to hardware/software components
3. **Implementation & Verification** — Controls are coded, tested, and validated against CSGs

CSGs are stable points in the lifecycle; they do NOT change once approved. Changes to CSGs trigger re-assessment and traceability updates.
