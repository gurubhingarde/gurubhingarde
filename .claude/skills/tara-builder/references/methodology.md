# ISO/SAE 21434 §15 Threat Analysis and Risk Assessment (TARA) Methodology

## Overview

TARA is the cyber analog of HARA — a 7-step Cartesian process for identifying cybersecurity threats, rating their impact and attack feasibility, determining risk, and specifying treatment decisions per ISO/SAE 21434 Clause 15.

## Seven-Step Process

### Step 1: Asset Identification

Identify all assets in the item with cybersecurity properties:
- **Data assets**: firmware images, calibration data, configuration, credentials, keys, DTCs, logs
- **Hardware assets**: processors, communication interfaces, storage, debug ports
- **Software assets**: bootloaders, applications, middleware, libraries
- **Communication assets**: CAN, LIN, Ethernet, wireless channels

Each asset must have cybersecurity properties documented:
- **Confidentiality (C)**: Data must not be readable by unauthorized parties
- **Integrity (I)**: Data must not be modifiable by unauthorized parties
- **Availability (A)**: Asset must be accessible when needed
- **Authenticity (Auth)**: Entity identity must be verifiable
- **Authorization (Authz)**: Access control enforced
- **Non-repudiation (NR)**: Action origin must be traceable

### Step 2: Threat Scenario Identification

For each asset and cybersecurity property, identify threat scenarios using **STRIDE**:
- **Spoofing**: Impersonating a system entity
- **Tampering**: Modifying asset data or state
- **Repudiation**: Denying action (forgery)
- **Information Disclosure**: Unauthorized access to data
- **Denial of Service**: Making asset unavailable
- **Elevation of Privilege**: Gaining unauthorized access rights

Classify threat agent types: Casual Hacker, Skilled Attacker, Insider, Organized Crime, Nation-State.

### Step 3: Impact Rating

Rate the worst-case impact across four dimensions using Severe/Major/Moderate/Negligible:
- **Safety (S)**: Injury or fatality risk (ISO 26262 severity mapping)
- **Financial (F)**: Direct economic loss
- **Operational (Op)**: Service disruption, recall costs
- **Privacy (Pr)**: Personal data exposure, regulatory violation

The *worst* impact across these four dimensions becomes the scenario's overall Impact Rating.

### Step 4: Attack Path Analysis

For each threat scenario, document:
- **Entry point**: How threat agent accesses the system (physical, remote, adjacent)
- **Attack vector**: Network, local, physical, wireless
- **Preconditions**: What must be true for attack to work (tool availability, access)
- **Propagation steps**: How threat propagates through the system
- **Exit point**: Where the attacker exits or the impact manifests

### Step 5: Attack Feasibility Rating

Rate the difficulty of executing the attack based on five factors:

| Factor | Very Low | Low | Medium | High |
|--------|----------|-----|--------|------|
| **Elapsed Time** | Year+ | Months | Weeks | Days |
| **Specialist Expertise** | Multiple experts | Expert | Proficient | Layman |
| **Knowledge of Item** | Critical (closed) | Sensitive (restricted) | Restricted (some) | Public (open) |
| **Window of Opportunity** | Difficult | Moderate | Easy | Unlimited |
| **Equipment** | Multiple bespoke | Bespoke | Specialized | Standard |

Compute Feasibility as the **lowest** (most favorable to attacker) factor rating. If any factor is "Very Low", feasibility is Very Low.

### Step 6: Risk Determination

Create a Risk Value (1-5) using Impact × Feasibility lookup:

```
                 Impact
           Negligible Major Severe
Feasibility
Very Low       1       2     3
Low            2       3     4
Medium         2       3     5
High           3       4     5
```

Risk 5 = Critical, 4 = High, 3 = Medium, 2 = Low, 1 = Minimal.

### Step 7: Risk Treatment Decision

For each threat scenario, select a treatment per risk value and target Cybersecurity Assurance Level (CAL):
- **Avoid**: Eliminate the threat (design change, disable function)
- **Reduce**: Mitigate feasibility or impact (add detection, encryption)
- **Share**: Transfer risk via contract, insurance, or warning
- **Retain**: Accept residual risk (document approval)

Residual risk must be acceptable per the target CAL.

## Cybersecurity Assurance Level (CAL)

| CAL | Scope | Targets |
|-----|-------|---------|
| 1 | Prevent casual hacker threats | Standard security practices |
| 2 | Prevent skilled attacker threats | Cryptographic integrity, authentication |
| 3 | Prevent insider + organized crime | Advanced detection, key management |
| 4 | Prevent nation-state threats | Hardware security, formal methods |

Higher CAL items require lower residual risk (avoid/reduce over retain).

## Artifacts Generated

TARA workbook contains:
1. Title Page
2. Document Control (revision history)
3. Assumptions (attacker model, environment, scope)
4. Item Description & cyber-relevant interfaces
5. Asset Inventory
6. Threat Scenarios (STRIDE matrix)
7. Impact Assessment (S/F/Op/Pr per scenario)
8. Attack Path Analysis (entry, vector, propagation)
9. Feasibility Rating (five-factor scoring)
10. Risk Determination (Impact × Feasibility lookup)
11. Risk Treatment (decisions, residual risk)
12. Cybersecurity Goals (derived from high-risk scenarios)
13. References
