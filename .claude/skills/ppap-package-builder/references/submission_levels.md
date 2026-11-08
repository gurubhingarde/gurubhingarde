# PPAP Submission Levels (1-5) — AIAG 4th Edition Matrix

## Quick Reference

| Level | Name | When Used | Elements Submitted | Elements Retained | Risk | OEM Audit |
|-------|------|-----------|-------------------|------------------|------|-----------|
| 1 | PSW Only | Low-risk, long-standing suppliers | PSW (E18) | E1-E17 | Highest | Can audit on-site |
| 2 | PSW + Samples + Limited | Moderate-risk, established suppliers | PSW, samples, dimensional, capability, material | Design/process FMEA, detailed controls | Medium | Can audit |
| 3 | PSW + Complete | NPI, design changes, supplier changes | All 18 elements | None | Lowest | Reviews all |
| 4 | Customer-Defined | Customer specifies unique requirements | Per customer specification | Per customer specification | Varies | Per customer |
| 5 | PSW + On-Site Review | High-risk, safety-critical, new suppliers | All 18 elements + OEM on-site | None | Lowest | Required |

---

## Detailed Breakdown by Level

### LEVEL 1: PSW Only

**Purpose:** Low-administrative-burden approval for parts with minimal risk and from highly-trusted, long-standing suppliers.

**When Selected:**
- Non-critical, non-safety-related parts
- Design and process are stable (no changes)
- Supplier has multi-year track record of zero defects
- Customer has strong existing PPAP history with supplier
- OEM cost/schedule priority is speed of approval

**What's Submitted to OEM:**
- PSW document (Element 18) — signed authorization only

**What Supplier Retains:**
- All 17 supporting elements (E1-E17): design records, ECNs, DFMEA, PFMEA, control plan, MSA, dimensional, capability studies, material certs, lab certs, sample parts, master sample, gages

**OEM Access to Data:**
- OEM can request on-site audit to review all retained data (supplier must make available within agreed timeframe)
- OEM typically does NOT review data unless quality issue occurs post-approval

**Timeline:**
- OEM approval typically within 1-2 weeks (minimal review)

**Risk Assessment:**
- **Highest risk** — OEM has no visibility to design/process data; relies entirely on supplier reputation
- Appropriate only for lowest-risk parts and highest-confidence suppliers
- If quality problem occurs, OEM has limited baseline data to investigate root cause

**Typical Usage:**
- Standard fasteners, purchased components with stable supply
- Plastic connectors from ISO 9001-certified supplier with 5+ year clean history
- Non-functional decorative parts

**Example Scenario:**
> "Phoenix Motors and Supplier ABC have 10-year relationship with zero defects. Plastic snap-fit bracket for door panel: no design change, no new tooling. OEM approves Level 1 PPAP submission; supplier mails signed PSW; approval granted in 1 week."

---

### LEVEL 2: PSW + Samples + Limited Data

**Purpose:** Moderate-administrative-burden approval for parts with moderate risk; OEM evaluates samples and selected capability data without reviewing detailed design/process FMEA.

**When Selected:**
- Design or process change to existing part (not full redesign)
- Established supplier with good history (but not "zero-defect" track record)
- Customer wants to evaluate producibility but doesn't need full design documentation review
- Component supplier (tier 2+) to primary supplier (tier 1)

**What's Submitted to OEM:**
- PSW (E18) — signed authorization
- Design Records (E1) — current drawing with revisions
- Sample Production Parts (E14) — typically 25 units
- Dimensional Results (E9) — first-piece inspection report
- Material/Performance Tests (E10) — certs, test reports
- Initial Process Studies (E11) — Cpk/Ppk capability data
- Checking Aids (E16) — gage calibration status (summary)

**What Supplier Retains:**
- Engineering Changes (E2) — unless customer specifically requests
- Engineering Approval (E3) — unless customer specifically requests
- Design FMEA (E4) — detailed DFMEA retained; summary may be in PSW
- Process Flow (E5) — detailed flow retained; summary provided
- Process FMEA (E6) — detailed PFMEA retained at supplier
- Control Plan (E7) — detailed control plan retained; summary referenced in PSW
- MSA (E8) — detailed MSA data retained
- Lab Documentation (E12) — lab certs summary provided; full accreditation files retained
- Appearance Approval (E13) — if applicable; customer notified of approval
- Master Sample (E15) — retained by supplier per requirement

**OEM Access to Data:**
- OEM reviews samples in-house (evaluation, testing, retention)
- OEM reviews dimensional and capability data
- OEM can request audit to review retained design/process FMEA if quality issue occurs

**Timeline:**
- OEM approval typically 3-4 weeks (samples must be received, evaluated, tested)

**Risk Assessment:**
- **Medium risk** — OEM has visibility to producibility (samples, capability) but limited insight to design robustness
- Appropriate for established suppliers with moderate design/process change risk

**Typical Usage:**
- Purchased component with supplier source change (e.g., moving from Supplier A to Supplier B)
- Design revision (cosmetic, minor dimensional change) with minor process impact
- New part from supplier with established relationship

**Example Scenario:**
> "Supplier has produced capacitors for Phoenix Motors for 5 years, zero defects. New capacitor variant: 100 µF instead of 47 µF (same footprint). Design change = minor; manufacturing process = no change (same oven, same BOM structure). OEM approves Level 2 PPAP. Supplier ships 25 sample units + dimensional report + material cert + capability study (Cpk 2.1). OEM evaluates samples in lab, approves in 3 weeks."

---

### LEVEL 3: PSW + Complete Submission (MOST COMMON)

**Purpose:** Full-oversight approval for new parts, significant design/process changes, or customer default requirement; OEM reviews all 18 elements before approval.

**When Selected:**
- Initial production approval (NPI)
- Design change with functional or performance impact
- Process change affecting critical characteristics
- Supplier change (new tier 1 supplier)
- Customer PPAP policy default (many OEMs: "All new parts require Level 3 PPAP")
- Long gap since last PPAP (e.g., 2+ years; design/process "stale")

**What's Submitted to OEM:**
- **ALL 18 PPAP Elements submitted; nothing retained at supplier**
  - Design Records (E1)
  - Engineering Changes (E2)
  - Engineering Approval (E3)
  - Design FMEA (E4)
  - Process Flow (E5)
  - Process FMEA (E6)
  - Control Plan (E7)
  - MSA Results (E8)
  - Dimensional Results (E9)
  - Material/Performance Tests (E10)
  - Initial Process Studies (E11)
  - Lab Documentation (E12)
  - Appearance Approval (E13) — if applicable
  - Sample Parts (E14) — typically 25 units
  - Master Sample (E15) — supplier retains for reference; customer provided sample on delivery
  - Checking Aids (E16) — gage list and calibration status
  - Customer Requirements (E17)
  - PSW (E18)

**OEM Access to Data:**
- OEM reviews all design/process documentation in-house
- OEM evaluates samples
- OEM validates design and process robustness
- OEM may conduct supplier audit if desired (optional)

**Timeline:**
- OEM approval typically 4-8 weeks (comprehensive design/process review; possible customer/supplier Q&A)
- If conditional approval: additional 2-4 weeks to resolve open items

**Risk Assessment:**
- **Lowest risk** — OEM has complete visibility to design intent and process controls
- Appropriate for all significant changes and new supplier relationships
- Sets strong baseline for ongoing production control

**Typical Usage:**
- New electronic control unit (ECU) design for vehicle platform
- Major supplier transition (e.g., moving interior trim from Supplier A to Supplier B)
- Design change affecting customer-perceived attributes (performance, reliability, appearance)
- First production from new supplier (even if part design unchanged)

**Example Scenario:**
> "Phoenix Motors introduces new Electronic Stability Control (ESC) module. New design from Tier 1 supplier ABC Electronics. Level 3 PPAP required per customer policy. Supplier submits 22-tab PPAP workbook: design drawings, DFMEA (15 high-RPN items with controls), PFMEA (18 process steps, controls verified), control plan (12 critical characteristics), MSA (Gage R&R < 10% for all gages), dimensional report (all 28 dimensions within tolerance), Cpk studies (all >= 1.85), RoHS + thermal + vibration test reports, qualified lab certs, 25 sample units + master sample, custom PCB placement fixture with calibration. OEM reviews for 6 weeks; identifies 3 open items (IMDS submission timeline, appearance standard clarification, supplier audit scheduling); supplier closes in 2 weeks; Level 3 PPAP approved."

---

### LEVEL 4: Customer-Defined Level

**Purpose:** Customer-specified level not covered by standard Levels 1-3; OEM defines unique requirements for the specific part or program.

**When Selected:**
- Customer has unique risk profile (e.g., aerospace quality, safety-critical automotive, medical)
- Customer specifies specific elements and data required beyond AIAG baseline
- Hybrid of Level 2 and 3 (e.g., "PSW + DFMEA + Capability Studies + Samples")
- Program-specific requirements (e.g., "First 10 parts produced on locked-down process; full traceability")

**What's Submitted to OEM:**
- **Per customer specification** — varies by part and customer policy
- Typical Level 4 examples:
  - Example A: "PSW + DFMEA + Control Plan + Dimensional Results + Material Certs"
  - Example B: "PSW + DFMEA + PFMEA + Capability Studies + MSA + Samples"
  - Example C: "PSW + everything except detailed DFMEA (summary acceptable)"

**What Supplier Retains:**
- **Per customer specification** — elements not required in submission level

**OEM Access to Data:**
- Per customer specification; usually includes audit rights for all retained data

**Timeline:**
- Varies; typically 2-6 weeks depending on complexity

**Risk Assessment:**
- **Varies** — tailored to specific part risk profile

**Typical Usage:**
- Aerospace supplier programs (AS9100 compliance; enhanced traceability)
- Medical device suppliers (FDA-regulated; enhanced documentation)
- Tier 1 supplier internal PPAP (OEM to Tier 2) with customer-specified baseline
- Program-specific launch phase (e.g., "New vehicle platform launch requires Level 4 PPAP with additional 6-month production control verification")

**Example Scenario:**
> "Aerospace supplier delivering avionics component. Customer specifies Level 4 PPAP: PSW + DFMEA + PFMEA + Control Plan + Dimensional Results + MSA + Supplier Audit. Supplier submits 8 elements per specification; customer conducts on-site audit in week 3; PPAP approved conditional on supplier implementing 5 quality improvement action items; supplier completes in 60 days; approval finalized."

---

### LEVEL 5: PSW + On-Site Supplier Review

**Purpose:** Maximum-oversight approval; OEM team visits supplier facility to observe process, interview engineers, validate data, and assess supplier capability.

**When Selected:**
- High-risk part (safety-critical, complex, customer's first production from supplier)
- Supplier new to OEM (new relationship; need to assess capability firsthand)
- Quality issue escalation (supplier had previous defect history; OEM wants to validate corrective actions)
- Complex manufacturing process (high-precision, specialized equipment, rare failure modes)
- Program-critical component (supply chain risk if supplier fails; OEM wants direct visibility)

**What's Submitted to OEM:**
- **ALL 18 elements** (same as Level 3)
- Plus: supplier facility tour, process observation, engineer Q&A, document review on-site

**OEM On-Site Activities:**
- Manufacturing floor tour (observe process firsthand, equipment, material handling)
- Process capability demonstration (live production run, real-time SPC, dimensional checks)
- Design/process FMEA walkthrough with supplier FMEA team
- Control plan verification (confirm controls match actual shop floor practice)
- Quality system audit (ERP traceability, corrective action process, training records)
- MSA validation (observe gage usage, calibration practices)
- Q&A with supplier engineering, quality, manufacturing management
- Physical inspection of master sample, gages, fixtures, lab facilities

**Timeline:**
- PPAP submission + 2-4 weeks for on-site audit preparation
- On-site visit: typically 1-3 days
- Post-audit: 2-4 weeks for follow-up questions and closeout
- Total cycle: 6-10 weeks (longest of all levels)

**Risk Assessment:**
- **Lowest risk** — OEM has direct visibility to supplier capability, facilities, and personnel
- Highest confidence in part quality and supply chain reliability

**Typical Usage:**
- New automotive tier 1 supplier (e.g., first production from new PCB assembly house)
- Safety-critical part (brake system, steering, airbag control, battery management)
- Single-source component (no alternate supplier; supply chain risk if supplier fails)
- High-complexity electronic assembly with 100+ components
- Supplier with history of quality escapes; recovery validation

**Example Scenario:**
> "Phoenix Motors qualifies new PCB assembly supplier for Electronic Brake Module (critical safety function). Supplier ABC Electronics submits Level 5 PPAP: all 18 elements per specification, plus 22-tab workbook with embedded FMEA analyses, control plan, SPC charts. OEM scheduling on-site audit. Audit week: Phoenix Motors Quality Manager, Design Engineering, Manufacturing Engineering visit supplier facility for 2 days. Observe PCB placement (vision system 0.5mm accuracy), reflow soldering (profile verification), 100% electrical test, visual inspection per IPC-A-610. FMEA walkthrough with supplier FMEA team identifies 2 design concerns; supplier implements design review notes. OEM approves Level 5 PPAP with 2 conditional items; supplier closes in 30 days. Production authorized."

---

## Selection Decision Tree

Use this flowchart to select appropriate submission level:

```
START: New part or change?

├─ NEW PART (NPI)
│  ├─ Existing trusted supplier (5+ years, zero defects)
│  │  └─ Level 2 or 3 (customer default typically Level 3)
│  ├─ New supplier
│  │  └─ Level 3 or 5 (safety-critical or complex → Level 5)
│  └─ Unknown supplier, sole source
│     └─ Level 5 (mandatory on-site)
│
├─ DESIGN CHANGE
│  ├─ Cosmetic or minor non-functional change
│  │  └─ Level 2 (if trusted supplier) or Level 3 (if default)
│  ├─ Functional change (performance, reliability impact)
│  │  └─ Level 3 (standard) or Level 5 (if safety-critical)
│  └─ Safety-critical change (brake, steering, airbag, etc.)
│     └─ Level 5 (mandatory)
│
├─ PROCESS CHANGE
│  ├─ Non-critical characteristic; minor impact (e.g., different fixture)
│  │  └─ Level 2 (trusted) or Level 3 (default)
│  ├─ Critical process change (new equipment, new operator qualification, new oven)
│  │  └─ Level 3 (standard) or Level 5 (if safety-critical)
│  └─ Change to sole-source supplier's process
│     └─ Level 5 (mandatory)
│
├─ SUPPLIER CHANGE (same part number, different supplier)
│  ├─ Supplier-to-supplier; part design unchanged
│  │  └─ Level 2 (if design stability proven) or Level 3 (standard)
│  └─ New supplier with unknown history
│     └─ Level 3 or 5 (new supplier defaults to Level 3 minimum)
│
├─ LONG GAP (2+ years since last PPAP)
│  ├─ Design/process confirmed unchanged; supplier stable
│  │  └─ Level 1 or 2 (minimal review to confirm stability)
│  └─ Any change or supplier turnover
│     └─ Level 3 (revalidate design/process)
│
└─ END: Confirm selection with customer requirement
```

---

## Customer Requirements Typical by OEM

| OEM | Default | Notes |
|-----|---------|-------|
| Toyota | Level 3 | All NPI; supplier change = Level 3; design change = Level 3 unless approved for Level 2 |
| Ford | Level 3 | All critical parts; Level 2 acceptable for commodity parts with approval |
| General Motors | Level 3 | Standard default; supplier audit required for Level 5 if safety-critical |
| Volkswagen/Audi | Level 3-5 | Safety-critical parts often Level 5; electronics = Level 3; mechanical = Level 2 if low-risk |
| BMW | Level 3 | NPI and supplier change = Level 3; process change = Level 2-3 depending on criticality |
| Tier 1 Suppliers (to OEM) | Level 2-3 | Typically Level 3 for new programs; Level 2 for minor changes after supplier qualification |
| Small OEMs / Startups | Level 2-3 | Level 3 most common; Level 2 acceptable for low-complexity parts |

---

## OEM Conditional Approval & Open Items

Even after successful PPAP review, OEM may issue **Conditional Approval** — meaning:
- PPAP approved but supplier must close 1-5 open items within 30-90 days
- Common open items:
  - "Submit IMDS by 2026-05-15" (material data system submission delay)
  - "Complete supplier audit by 2026-06-30"
  - "Provide updated capability study after 1000-part production run"
  - "RoHS certificate from third-party lab (not supplier cert)"
  - "Implement SPC monitoring for 6 months; submit monthly reports"

Once open items are closed, OEM issues **Final Approval** — production authorized to begin.

---

## PPAP Approval Statuses

After OEM review, PSW is marked with one of these status stamps:

1. **APPROVED** — No issues; production authorized immediately
2. **APPROVED WITH CONDITIONS** — Approval granted but supplier must close open items within specified timeline before full production release
3. **REJECTED** — Does not meet minimum requirements; supplier must resubmit complete revised PPAP addressing all issues
4. **PENDING AUDIT** — PPAP technically complete but OEM audit required before approval (typically Level 4-5)

---

## Summary Guidance

- **Default: Level 3** — If unsure or if customer hasn't specified, assume Level 3
- **Level 1** — Only for trusted suppliers with decade-long track records on non-critical parts
- **Level 2** — Established suppliers, moderate changes, cost/schedule-driven approvals
- **Level 3** — Standard for NPI, design changes, supplier changes, safety-critical parts
- **Level 4** — Customer-tailored per specific program or risk profile
- **Level 5** — High-risk, safety-critical, new suppliers, or OEM direct capability validation required
