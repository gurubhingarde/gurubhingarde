# DIA Methodology — ISO 26262-8 Section 5

## What is a Development Interface Agreement (DIA)?

A Development Interface Agreement is a **contractual instrument** that governs the allocation of functional safety work products, responsibilities, communication cadence, tool sharing, and intellectual property ownership among the OEM (Original Equipment Manufacturer) and its suppliers (e.g., Tier-1 integrators, IC suppliers, tooling vendors) during the development of a safety-critical automotive item.

The DIA operationalizes ISO 26262-8 Section 5's guidance on **organizational interfaces** by making explicit:
- **Who owns each work product** (HARA, FSC, TSC, HW/SW architecture, safety plan, safety case)
- **Who must review and approve it**
- **When and how parties communicate** about safety issues
- **What evidence must be delivered** and in what format
- **How changes to safety requirements or design are managed** across party boundaries
- **Tool and design asset sharing** (including license terms and qualification responsibility)
- **IP ownership** (pre-existing, joint, residual)
- **Confidentiality and publication scope**

## OEM–Tier-1 Dynamics

### Typical responsibility split

| Phase | OEM Role | Tier-1 Role |
|-------|----------|-------------|
| **Concept** | Own HARA; define safety goals + item definition | Provide input on feasibility; consulted on architecture |
| **System Design (FSC/TSC)** | Approve FSC & TSC; own safety case structure | Design & author FSC & TSC; execute decomposition |
| **HW Design** | Monitor; approve safety reqs; review architecture | Author HW safety reqs & architecture; own HW design decisions |
| **SW Design** | Monitor; approve safety reqs; review architecture | Author SW safety reqs & architecture; own implementation |
| **Verification & Test** | Oversee test plans; audit evidence; approve test reports | Execute all HW/SW unit and integration tests; author V&V reports |
| **Validation & Integration** | Author OEM-level safety case; own production acceptance | Contribute sub-cases; provide qualification evidence |

### Key contractual levers in the DIA

1. **Scope boundary** — What aspects of the item is the Tier-1 responsible for? (e.g., "ESC ECU firmware and safety-critical algorithms, excluding vehicle-level safety goals or OEM system integration")
2. **RACI for each work product** — Who is R (does the work), A (is accountable), C (must be consulted), I (kept informed)?
3. **Deliverable format & acceptance** — "We accept FSC as an Excel workbook with calculated ASIL, rationale columns filled in, and zero open FTA nodes."
4. **Review gates** — Which reviews are joint (OEM + Tier-1 + IC) vs. unilateral (Tier-1 lead with OEM observation)?
5. **Communication cadence** — Weekly safety coordination calls + monthly summary reports = structured escalation path.
6. **Change authority** — "Any safety-goal change requires OEM approval; cost/schedule change requires Tier-1 lead + OEM concurrence."

## IC Supplier Integration

When the design includes a safety-critical semiconductor (e.g., automotive MCU, safety SoC):

- **IC supplier owns** chip-level FMEDA (failure modes of on-chip logic, memories, clocks), chip-level safety case (diagnostics, self-test coverage), and design documentation (datasheet, safety manual).
- **Tier-1 owns** system-level FMEDA (integrating IC failures into system architecture), system-level safety case (subsystem integration), and HW architecture (how IC is used in the context of the full item).
- **OEM owns** HARA, safety goals, item-level safety case (how subsystem fits into vehicle).
- **DIA must clarify**: What evidence does IC supplier provide? What formats? What level of disclosure of internal IP? Who qualifies the IC for the target ASIL?

### Typical IC supplier deliverables

1. Chip-level FMEDA (failure mode → diagnostic coverage table)
2. Chip-level safety datasheet (safe states, diagnostic timing, architectural faults)
3. Functional safety manual (how to use the IC safely; what application must do)
4. Qualification kit (test reports, design-for-test coverage, production acceptance evidence)

## Common DIA Failure Modes

1. **Vague scope** — "Tier-1 is responsible for safety" is not a scope. Be specific: "ESC firmware on ASIL D; excludes vehicle-level coordination, OEM supply-chain integration, production monitoring."

2. **No RACI** — "Everyone reviews everything" or "We'll figure it out as we go" leads to disputes when a safety issue arises. Commit to a RACI matrix at kickoff.

3. **Deliverable ambiguity** — "Tier-1 will provide FSC" without specifying format, review depth, or acceptance criteria leads to rework. Use the template in this skill.

4. **Silent tool assumptions** — "We'll use our FMEA tool for FMEDA analysis" without saying who owns the license, who trains, who maintains the model. Document tool ownership and qualification responsibility.

5. **IP limbo** — "Pre-existing IP is yours, DIA work product is ours" without clarifying what happens if Tier-1 leaves a residual algorithm or trade secret in the work product.

6. **No escalation path** — When a safety finding disagrees (e.g., OEM rates a severity higher than Tier-1), the DIA must say how it gets resolved (OEM final decision? Joint CCB?).

7. **Infrequent communication** — Monthly reviews on a safety-critical program is too slow. DIA should default to weekly or bi-weekly safety coordination.

## Reference: ISO 26262-8 Section 5 Requirements

ISO 26262-8:2018 Section 5 mandates that organizations identify and document interfaces between:
- Parties responsible for different phases (OEM, Tier-1, suppliers)
- Parties responsible for different subsystems (HW, SW, system integration)
- Development team and operations/manufacturing

The DIA satisfies this by:
- **Listing all parties** (02_Parties tab)
- **Allocating work products per party** (04_RACI_Matrix tab)
- **Establishing review gates and approval authorities** (06_Joint_Reviews tab)
- **Defining communication protocol** (05_Communication_Protocol tab)
- **Specifying deliverable evidence** (07_Supplier_Deliverables tab)
- **Managing changes across interfaces** (08_Change_Management tab)

## DIA Structure — How to Read and Use

The DIA is organized into 12 tabs:

- **00_Title_Page**: Metadata (item, doc ID, revision, signatory organizations)
- **01_Document_Control**: Version history and distribution
- **02_Parties**: Organizations, roles (OEM / Tier-1 / IC), contact points
- **03_Item_Scope**: What is in / out of scope
- **04_RACI_Matrix**: Per-work-product responsibility allocation
- **05_Communication_Protocol**: Meeting cadence, escalation paths
- **06_Joint_Reviews**: Review milestones, attendees, acceptance criteria
- **07_Supplier_Deliverables**: What Tier-1 delivers, when, in what format
- **08_Change_Management**: How safety or design changes are approved
- **09_Tool_Sharing**: Tool licenses, qualification responsibility
- **10_Confidentiality_IP**: IP ownership, publication rules
- **11_References**: Pointers to item definition, master contract, applicable standards

When reviewing a DIA:
1. **Check scope boundaries** (Tab 03) — is there agreement on what is in/out?
2. **Verify RACI** (Tab 04) — is responsibility allocated per work product? Are "—" (not applicable) cells correct, or is there ambiguity?
3. **Review communication cadence** (Tab 05) — do the parties agree to meet frequently enough to catch safety issues early?
4. **Confirm deliverables & dates** (Tab 07) — can Tier-1 deliver on schedule? Are acceptance criteria objective?
5. **Understand change authority** (Tab 08) — who approves safety-related changes? Cost-related changes?

## When to Generate a New DIA

Generate a DIA at the start of a new safety program (concept phase) or when:
- The OEM brings on a new Tier-1 or IC supplier
- Scope changes significantly (e.g., moving from ASIL B to ASIL D)
- Organizational structure changes (e.g., multi-supplier integration)
- Regulatory or contractual requirements change
