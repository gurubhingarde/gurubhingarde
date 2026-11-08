# RACI Assignment per Safety Work Product

## RACI Definition

- **R** (Responsible) — Does the work; produces the artifact
- **A** (Accountable) — Has final authority; approves release
- **C** (Consulted) — Provides input; must be asked before decisions
- **I** (Informed) — Kept in the loop; notified after key decisions
- **—** (Not applicable) — No involvement in this work product

## Standard OEM–Tier-1–IC Split

This table shows the default RACI recommendations for each safety work product. Use this as a starting point; override via the `raci_overrides` array in the input JSON if your program has a different split.

### Concept Phase

| Work Product | OEM | Tier-1 | IC Supplier | Notes |
|---|---|---|---|---|
| **HARA** | A,R | C | I | OEM owns hazard analysis; Tier-1 reviews feasibility; IC supplier informed of target ASIL |
| **Item Definition** | A,R | C | I | OEM defines system boundary and safety goals; Tier-1 provides input on architecture |

### System Design Phase

| Work Product | OEM | Tier-1 | IC Supplier | Notes |
|---|---|---|---|---|
| **FSC (Functional Safety Concept)** | A | R | C | Tier-1 leads FSC development; OEM approves; IC supplier consulted on chip-level assumptions |
| **TSC (Technical Safety Concept)** | A | R | C | Tier-1 leads TSC; OEM approves; IC supplier consulted on diagnostic coverage |

### Hardware Development

| Work Product | OEM | Tier-1 | IC Supplier | Notes |
|---|---|---|---|---|
| **HW Safety Reqs** | I | A,R | C | Tier-1 derives HW reqs from TSC; OEM informed; IC supplier consulted on part selection |
| **HW Architecture** | I | A,R | C | Tier-1 owns HW design; OEM informed; IC supplier (if applicable) inputs on on-chip architecture |
| **HSI (HW-SW Interface)** | I | A,R | C | Tier-1 defines register layout, interrupt timing, memory model; OEM informed; IC supplier defines protocol |
| **FMEDA (HW)** | I | A,R | R | Tier-1 leads system-level FMEDA; OEM informed; IC supplier owns chip-level FMEDA |

### Software Development

| Work Product | OEM | Tier-1 | IC Supplier | Notes |
|---|---|---|---|---|
| **SW Safety Reqs** | I | A,R | — | Tier-1 derives from TSC; OEM informed; typically no IC supplier role |
| **SW Architecture** | I | A,R | — | Tier-1 owns architecture; OEM reviews; IC supplier not involved at this level |
| **SW Unit Design & Code** | I | A,R | — | Tier-1 owns implementation; OEM audits; IC supplier (if soft-core) provides HDL |
| **SW Verification & Unit Test** | I | A,R | — | Tier-1 executes all unit tests; OEM reviews evidence; IC supplier provides simulation models |

### Validation Phase

| Work Product | OEM | Tier-1 | IC Supplier | Notes |
|---|---|---|---|---|
| **Safety Plan** | A | A | C | OEM & Tier-1 jointly author; IC supplier consulted on chip-level testing approach |
| **Safety Case** | A,R | R | R | OEM owns item-level + top-level; Tier-1 authors subsystem cases; IC supplier authors chip-level case |
| **Integration Test Report** | I | A,R | C | Tier-1 executes; OEM reviews; IC supplier provides chip-level test data if needed |
| **Production Acceptance** | A | R | C | OEM owns acceptance criteria; Tier-1 verifies at gate; IC supplier provides wafer-level evidence |

## Rationale by Party Role

### OEM (Original Equipment Manufacturer)

**Owns** hazard analysis, safety goals, item-level safety case, and final integration.

- HARA is OEM responsibility because hazard assessment depends on vehicle-level context (vehicle class, market, driver population).
- Item definition is OEM because it sets system boundaries and interfaces.
- FSC & TSC approval authority is OEM because safety goals flow from HARA.
- OEM is "Accountable" (A) on most items — has final authority and takes the regulatory hit if ISO 26262 conformance is questioned.

### Tier-1 (Integrator / System Supplier)

**Owns** detailed design and implementation; responsible for translating OEM safety goals into subsystem architecture, design, and code.

- Tier-1 is "Responsible" (R) for FSC, TSC, HW/SW design, FMEDA, and all V&V.
- Tier-1 is "Accountable" (A) for the completeness and correctness of the design evidence.
- Tier-1 is "Consulted" (C) on HARA and Item Definition because feasibility and cost impact.

### IC Supplier (Chip / Core Provider)

**Owns** chip-level safety evidence: FMEDA (on-chip failure modes), safety datasheet, and chip-level safety case.

- IC supplier is "Responsible" (R) for on-chip FMEDA and chip safety case.
- IC supplier is "Consulted" (C) on system-level FMEDA and architecture because on-chip failure modes affect system design.
- IC supplier is "Informed" (I) of HARA, Item Definition, and FSC because they set the target ASIL and timing assumptions.

## Common Overrides

### Override 1: Tier-1 Owns HARA

Some programs push HARA responsibility to Tier-1 (e.g., if the OEM uses a third-party system integrator and wants them to lead hazard analysis).

| Work Product | OEM | Tier-1 | IC Supplier |
|---|---|---|---|
| HARA | I,C | A,R | I |
| Item Definition | I,C | A,R | I |

**Use when:** Tier-1 is the de-facto system architect and the OEM role is validation / integration only.

### Override 2: OEM Owns All Design

Some programs (especially smaller OEMs or newer suppliers) have OEM retain design authority; Tier-1 is essentially an implementation vendor.

| Work Product | OEM | Tier-1 | IC Supplier |
|---|---|---|---|
| FSC / TSC | A,R | C | I |
| HW/SW Safety Reqs | A,R | C | I |
| HW/SW Architecture | A,R | C | I |

**Use when:** OEM wants tight control; Tier-1 resources are less experienced or constrained in scope.

### Override 3: Joint Accountability

Some mature partnerships use joint (A,R) on core work products to emphasize shared ownership.

| Work Product | OEM | Tier-1 | IC Supplier |
|---|---|---|---|
| FSC | A,R | A,R | C |
| TSC | A,R | A,R | C |
| Safety Plan | A,R | A,R | C |

**Use when:** OEM and Tier-1 have deep trust and high collaboration; want to avoid finger-pointing.

## Work Product Definitions (Brief)

| Abbr. | Full Name | Owner | Output Format | Typical Size |
|---|---|---|---|---|
| HARA | Hazard Analysis & Risk Assessment | OEM | xlsx (14 tabs) | 500–2000 hazards |
| FSC | Functional Safety Concept | Tier-1 | pdf + xlsx (FTA) | 20–50 pages |
| TSC | Technical Safety Concept | Tier-1 | pdf + xlsx (FMEA) | 30–80 pages |
| HW SR | Hardware Safety Requirements | Tier-1 | xlsx or SysML | 100–500 reqs |
| HW Arch | Hardware Architecture | Tier-1 | pdf + draw.io | 10–30 diagrams |
| HSI | Hardware-Software Interface | Tier-1 | xlsx + C header | 20–100 pages |
| FMEDA | Failure Mode, Effects & Diagnostic Analysis | Tier-1 (Sys) + IC (Chip) | xlsx (FMEA style) | 500–5000 modes |
| SW SR | Software Safety Requirements | Tier-1 | xlsx or SysML | 100–1000 reqs |
| SW Arch | Software Architecture | Tier-1 | C/Ada + design doc | 20–100 pages |
| V&V Report | Verification & Validation Report | Tier-1 | pdf + test logs | 50–200 pages |
| Safety Plan | Safety Program Plan | OEM + Tier-1 | pdf | 30–50 pages |
| Safety Case | Formal Safety Case | OEM (Item) + Tier-1 (Sub) + IC (Chip) | pdf + assurance structure | 100–500 pages |

## When to Deviate from the Standard

Good reasons to override the default RACI:

1. **Tier-1 is the integrator, not OEM** — Tier-1 should be A,R on HARA & Item Def if they own the system architecture.
2. **IC supplier is critical to safety** — Make IC supplier A,R on FMEDA if the chip architecture is the primary safety barrier.
3. **OEM has limited engineering** — Simplify by making Tier-1 A,R on all design; OEM is A (approver) only.
4. **Multi-tier supply chain** — Introduce Tier-2 (e.g., sub-integrator) and adjust RACI accordingly.
5. **Outsourced verification** — If a third party (e.g., independent lab) verifies, they might be R on test reports and Tier-1/OEM are C/I.

**Bad reasons to override:**
- "We'll figure it out later" — Document now; ambiguity leads to disputes.
- "Everyone reviews everything" — Accountability is diluted; no clear owner.
- "Supplier can't be A" — If you don't trust them to be accountable, reconsider the contract.

## Example: ESC (Electronic Stability Control) at ASIL D

**Parties:**
- OEM: Phoenix Motors Inc. (HARA owner, approver)
- Tier-1: ChassisCorp Systems (FSC/TSC/HW/SW design)
- IC Supplier: Automotive Semiconductor AG (safety MCU)

**RACI:**

| Work Product | OEM | ChassisCorp | AutoSem |
|---|---|---|---|
| HARA | A,R | C | I |
| Item Definition | A,R | C | I |
| FSC | A | R | C |
| TSC | A | R | C |
| HW Safety Reqs | I | A,R | C |
| HW Architecture | I | A,R | C |
| HSI | I | A,R | C |
| FMEDA | I | A,R | R |
| SW Safety Reqs | I | A,R | — |
| SW Arch / Test | I | A,R | — |
| Safety Plan | A | A | C |
| Safety Case | A,R | R | R |

**Why this split:**
- OEM owns HARA because vehicle-level hazards are OEM's call.
- ChassisCorp is R on design work products; OEM approves.
- AutoSem is R on chip-level FMEDA and safety case; ChassisCorp integrates into system.
- Safety Plan is co-authored (A,A); Safety Case is distributed (OEM at top level, ChassisCorp on subsystem, AutoSem on chip).
