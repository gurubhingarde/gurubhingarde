# PPAP Methodology and Submission Levels

## Overview

The Production Part Approval Process (PPAP) is the AIAG-defined procedure that authorizes a supplier to begin serial production of a part for an original equipment manufacturer (OEM). PPAP serves as the formal handoff from the engineering and launch phase into full production.

PPAP is required:
- At initial production approval (NPI)
- After any design change
- After any manufacturing process change
- After a change in supplier
- After a significant time gap (per customer requirements, typically 2 years)

## The Part Submission Warrant (PSW)

The PSW is the key document in PPAP. It is:
- A signed authorization by the supplier that all data is accurate and complete
- The formal approval mechanism — OEM marks PSW as "Accepted" or "Rejected"
- A contractual commitment to the production part specifications, drawings, and processes
- Required at all submission levels (1-5)

The PSW includes:
- Part identification (number, name, supplier code, customer code)
- Drawing revision and date
- Engineering change documentation
- Weight (mass) of the part
- Reason for submission (initial production, design change, process change, etc.)
- Submission level (1-5)
- Supplier declaration affirming accuracy of all submitted data
- Authorized signature block (supplier organization, signatory, title, email, phone, date)

## The 18 PPAP Elements (AIAG 4th Edition)

Every PPAP submission package consists of 18 defined elements:

1. **Design Records** — Engineering drawings with all revisions, approval signatures, and change history. Includes design change documentation (ECNs/ECOs).

2. **Authorized Engineering Change Documents** — Complete ECN/ECO record with approval dates, affected drawings, implementation status, and customer notification evidence.

3. **Engineering Approval** — Customer sign-off on the design (if required by contract or if customer-specific requirements apply).

4. **Design FMEA** — Design failure mode and effects analysis identifying design risks, severity/occurrence/detection ratings, and design control strategies. Demonstrates design robustness.

5. **Process Flow Diagrams** — Detailed flow of all manufacturing and assembly steps, equipment used, operator skill requirements, and process control points.

6. **Process FMEA** — Process failure mode and effects analysis identifying process risks, control strategies, and detection methods. Demonstrates process robustness.

7. **Control Plan** — Document specifying control strategy per characteristic: monitoring method (100% inspection vs sampling), gages, acceptance criteria, reaction plan, and frequency.

8. **Measurement System Analysis (MSA)** — Gage R&R studies demonstrating that all measurement systems are fit for purpose (typically R&R < 10% acceptable variation).

9. **Dimensional Results** — First-piece dimensional inspection report showing spec/tolerance for every critical characteristic, measured values, and in/out-of-spec status. Confirms design intent is achievable.

10. **Records of Material and Performance Test Results** — Material certifications (RoHS, REACH, IMDS submission), environmental tests (thermal, vibration, humidity), EMC testing, reliability testing. Demonstrates material and design performance.

11. **Initial Process Studies** — Process capability studies (Cpk and Ppk) for all controlled characteristics. Must meet customer minimum (typically Cpk >= 1.67 for critical/special characteristics).

12. **Qualified Laboratory Documentation** — List of all labs used for testing with accreditation numbers (A2LA, ISO 17025) and scope of accreditation.

13. **Appearance Approval Report (AAR)** — If the part has appearance, color, or surface-finish requirements, documented AAR from customer or customer-approved standard (IPC-A-610).

14. **Sample Production Parts** — Physical sample parts produced using production tooling and process, shipped to OEM for evaluation and retention. Minimum quantity typically 25 units.

15. **Master Sample** — A retained sample part stored at supplier as the reference standard for all future production comparisons. Retained for the life of the part.

16. **Checking Aids** — Any custom gages, fixtures, or inspection aids unique to the part. Includes calibration status and certification.

17. **Customer-Specific Requirements** — Any additional requirements mandated by the specific OEM beyond AIAG baseline (e.g., IMDS submission timeline, specific lab requirements, additional testing, supply agreements).

18. **Part Submission Warrant (PSW)** — The signed authorization document.

## Submission Levels (1-5)

PPAP submission levels define which elements are submitted to the OEM vs retained at the supplier.

### Level 1: PSW Only (Suppler Retains Supporting Data)

- **When used:** Low-risk design changes, non-critical parts, or per customer agreement
- **Submitted to OEM:** PSW only
- **Retained by supplier:** All 17 supporting elements (design records through checking aids)
- **OEM can audit:** Yes (on-site audit at supplier discretion)
- **Timeline:** OEM approves PSW without reviewing supporting data
- **Risk:** Highest — OEM blind trust in supplier; typically used only for long-standing suppliers with excellent track record

### Level 2: PSW + Samples + Limited Data

- **When used:** Moderate-risk changes; established suppliers
- **Submitted to OEM:** PSW, product samples (typically 25 units), dimensional results, material test data, process capability studies
- **Retained by supplier:** Design records, DFMEA, PFMEA, detailed control plan, MSA raw data, appearance approval
- **OEM can audit:** Yes; can review submitted elements on-site if desired
- **Timeline:** OEM evaluates samples; approves dimensional/capability data
- **Risk:** Medium — OEM evaluates producibility but doesn't review detailed design/process FMEA

### Level 3: PSW + Complete Submission (Most Common)

- **When used:** NPI (new product introduction), design changes, supplier changes, or customer default requirement
- **Submitted to OEM:** All 18 elements (complete package)
- **Retained by supplier:** None — OEM receives full documentation
- **OEM can audit:** Yes; reviews all design/process data
- **Timeline:** OEM conducts full review; may request additional data or retest
- **Risk:** Lowest — OEM visibility into design and process robustness; most common default submission level
- **Typical customer requirement:** "All new parts require Level 3 PPAP"

### Level 4: Customer-Defined Level

- **When used:** Customer specifies unique submission requirements not covered by Levels 1-3
- **Submitted to OEM:** Customer-specified subset (e.g., "PSW + DFMEA + Control Plan + dimensional results")
- **Retained by supplier:** Elements not specified by customer
- **OEM can audit:** Typically yes
- **Timeline:** Per customer definition
- **Risk:** Varies; typically medium (customer-tailored compromise)

### Level 5: PSW + On-Site Supplier Review

- **When used:** High-risk parts (safety-critical, highly complex), new suppliers, or per customer requirement
- **Submitted to OEM:** PSW + all supporting elements; OEM team conducts on-site evaluation at supplier
- **Retained by supplier:** None — OEM retains right to review everything on-site
- **OEM can audit:** Required; on-site review is mandatory
- **Timeline:** Extended; includes supplier facility tour, process observation, Q&A with engineers
- **Risk:** Lowest — OEM validates supplier capability through direct observation and questioning

## When Elements Are Submitted vs Retained

| Element | Level 1 | Level 2 | Level 3 | Level 4 | Level 5 |
|---------|---------|---------|---------|---------|---------|
| 1. Design Records | R | R | S | Varies | S |
| 2. Engineering Changes | R | R | S | Varies | S |
| 3. Engineering Approval | R | R | S | Varies | S |
| 4. DFMEA | R | R | S | Varies | S |
| 5. Process Flow | R | R | S | Varies | S |
| 6. PFMEA | R | R | S | Varies | S |
| 7. Control Plan | R | R | S | Varies | S |
| 8. MSA | R | R | S | Varies | S |
| 9. Dimensional | R | S | S | Varies | S |
| 10. Material Performance | R | S | S | Varies | S |
| 11. Process Studies | R | S | S | Varies | S |
| 12. Lab Documentation | R | R | S | Varies | S |
| 13. Appearance Approval | R | R | S | Varies | S |
| 14. Sample Parts | R | S | S | Varies | S |
| 15. Master Sample | R | R | S | Varies | S |
| 16. Checking Aids | R | R | S | Varies | S |
| 17. Customer Requirements | R | R | S | Varies | S |
| 18. PSW | S | S | S | S | S |

Legend: **S** = Submitted to OEM; **R** = Retained at supplier

## Typical PPAP Flow

1. **Design Phase Complete** → Design FMEA complete, drawings finalized, engineering approved
2. **Process Design Complete** → Process FMEA complete, control plan defined, measurements defined
3. **Process Capability Demonstration** → Run production equipment, generate Cpk/Ppk for all critical characteristics (target Cpk >= 1.67)
4. **First-Piece Inspection** → Dimension and test first production parts against all specs; record results
5. **Material & Lab Certification** → Obtain material certs (RoHS, IMDS), run required environmental/EMC tests at qualified labs
6. **Assemble PPAP Package** → Gather all 18 elements, compute file hashes, populate PSW form
7. **Supplier Sign-Off** → Authorized supplier representative signs PSW declaration
8. **Submit to OEM** → Deliver PPAP package (Level 1: PSW only; Level 2-3: full package)
9. **OEM Review & Audit** → OEM engineering reviews data, may conduct on-site audit (Level 5), requests clarifications
10. **Conditional Approval or Rejection** → OEM marks PSW as Approved, Conditional (w/ open items), or Rejected
11. **Resolve Open Items** (if Conditional) → Supplier addresses feedback, submits supplemental data
12. **Final Approval** → OEM marks PSW as Approved; supplier authorized to begin serial production

## Document References

- **AIAG PPAP Manual, 4th Edition** — Authoritative baseline for all 18 elements and submission levels
- **IATF 16949:2016** — Automotive quality standard; references PPAP as foundational to production control
- **Customer-Specific PPAP Supplements** — Each OEM (Toyota, Ford, GM, Volkswagen, etc.) defines supplemental requirements beyond AIAG baseline (e.g., specific lab requirements, IMDS timeline, appearance standards)
