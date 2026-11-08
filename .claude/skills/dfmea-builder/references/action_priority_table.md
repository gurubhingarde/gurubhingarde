# AIAG-VDA Action Priority (AP) Lookup Table

The Action Priority (AP) determines the urgency and resource allocation for addressing a failure mode. Unlike the classical Risk Priority Number (RPN), which is a simple multiplication (S × O × D), the AIAG-VDA method uses a **lookup table** that prioritizes severity while considering occurrence and detection holistically.

## Simplified AP Logic Rule

The AP is computed based on the following decision tree:

```
IF Severity >= 9
  THEN AP = High
ELSE IF (Severity >= 7 AND Occurrence >= 4)
  THEN AP = High
ELSE IF (Severity >= 4 AND Occurrence >= 7 AND Detection >= 7)
  THEN AP = High
ELSE IF (Severity >= 4 AND Occurrence >= 4)
  THEN AP = Medium
ELSE IF Severity >= 7
  THEN AP = Medium
ELSE IF (Occurrence >= 7 AND Detection >= 7)
  THEN AP = Medium
ELSE
  AP = Low
```

## Interpretation

| AP Level | Meaning | Action Required | Timeline |
|----------|---------|-----------------|----------|
| **High (H)** | Unacceptable risk; immediate action required | Must implement prevention control (design change) and/or detection control before production release. Risk cannot be accepted without escalation to engineering manager and customer. Document all actions and residual risk. | Immediate; target completion before Design Freeze or Design Release. No production parts without approval. |
| **Medium (M)** | Moderate risk; action plan required | Plan and execute controls (design change, testing, inspection). May be acceptable if: (1) prevention control is verified and reduces Occurrence, OR (2) detection control is robust and verified, OR (3) design margin is demonstrated. Review before production launch. | Within design phase or early production. Target completion 4–8 weeks. |
| **Low (L)** | Low risk; monitor and track | Include in FMEA for completeness and traceability. Design controls are in place or risk is inherently low. Verify controls during validation. No special action plan required unless failure mode is discovered in testing. | Standard design validation; no accelerated schedule needed. |

## Why AP Differs from RPN

**Classical RPN Example:**
- Failure Mode A: S=10, O=1, D=1 → RPN = 10 (appears low-risk!)
- Failure Mode B: S=3, O=5, D=5 → RPN = 75 (appears higher priority!)

**AIAG-VDA AP Result:**
- Failure Mode A: S=10, O=1, D=1 → AP = **High** (severity dominates; must address)
- Failure Mode B: S=3, O=5, D=5 → AP = **Low** (low severity; acceptable risk)

The AP method correctly recognizes that a catastrophic failure is unacceptable *even if rare and detectable*, whereas a minor inconvenience is tolerable *even if common*.

## AP Lookup Table (Full 10×10×10 Matrix)

Below is the AIAG-VDA table showing AP for all combinations of Severity (rows), Occurrence (columns), and Detection (layers). Three detection levels are shown for illustration; in practice, all D=1–10 can be derived from the rule above.

### Detection = 1 (Almost Certain Detection)

|   | O=1 | O=2 | O=3 | O=4 | O=5 | O=6 | O=7 | O=8 | O=9 | O=10 |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| **S=1** | L | L | L | L | L | L | L | L | L | L |
| **S=2** | L | L | L | L | L | L | L | L | L | L |
| **S=3** | L | L | L | L | L | L | L | L | L | L |
| **S=4** | L | L | L | M | M | M | M | M | M | M |
| **S=5** | L | L | L | M | M | M | M | M | M | M |
| **S=6** | L | L | L | M | M | M | M | M | M | M |
| **S=7** | M | M | M | H | H | H | H | H | H | H |
| **S=8** | M | M | M | H | H | H | H | H | H | H |
| **S=9** | H | H | H | H | H | H | H | H | H | H |
| **S=10** | H | H | H | H | H | H | H | H | H | H |

### Detection = 5 (Moderate Detection)

|   | O=1 | O=2 | O=3 | O=4 | O=5 | O=6 | O=7 | O=8 | O=9 | O=10 |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| **S=1** | L | L | L | L | L | L | L | L | L | L |
| **S=2** | L | L | L | L | L | L | L | L | L | L |
| **S=3** | L | L | L | L | L | L | L | L | L | L |
| **S=4** | L | L | L | M | M | M | M | M | M | M |
| **S=5** | L | L | L | M | M | M | M | M | M | M |
| **S=6** | L | L | L | M | M | M | M | M | M | M |
| **S=7** | M | M | M | H | H | H | H | H | H | H |
| **S=8** | M | M | M | H | H | H | H | H | H | H |
| **S=9** | H | H | H | H | H | H | H | H | H | H |
| **S=10** | H | H | H | H | H | H | H | H | H | H |

### Detection = 10 (Unlikely Detection)

|   | O=1 | O=2 | O=3 | O=4 | O=5 | O=6 | O=7 | O=8 | O=9 | O=10 |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|
| **S=1** | L | L | L | L | L | L | L | L | L | L |
| **S=2** | L | L | L | L | L | L | L | L | L | L |
| **S=3** | L | L | L | L | L | L | L | L | L | L |
| **S=4** | L | L | L | M | M | M | M | M | M | M |
| **S=5** | L | L | L | M | M | M | M | M | M | M |
| **S=6** | L | L | L | M | M | M | M | M | M | M |
| **S=7** | M | M | M | H | H | H | H | H | H | H |
| **S=8** | M | M | M | H | H | H | H | H | H | H |
| **S=9** | H | H | H | H | H | H | H | H | H | H |
| **S=10** | H | H | H | H | H | H | H | H | H | H |

**Note:** The table is *independent* of Detection for most cells because Severity drives the decision. Detection only affects the boundary cases (S=4, O=7–10 with low Detection would push from M to H).

## Example AP Calculations

### Example 1: Wheel Speed Sensor Signal Loss

- **Severity**: 9 (loss of vehicle speed feedback → loss of ESC → safety-critical)
- **Occurrence**: 4 (sealed connector, good design margin → O=4)
- **Detection**: 8 (design review, testing, CAN diagnostics, manufacturing potting → D=8)

**AP Logic**:
- S=9 ≥ 9? **YES** → AP = **H (High)**

**Interpretation**: This is High priority regardless of O and D because severity is catastrophic. Must implement robust design controls (connector sealing validation, redundancy if necessary) and production verification (100% inspection).

---

### Example 2: Loose Panel Gap (Cosmetic)

- **Severity**: 3 (visible gap, no functional impact)
- **Occurrence**: 6 (assembly tolerance stack-up, manufacturing process capability Cpk ~1.3)
- **Detection**: 5 (100% visual inspection in assembly, sampling in QA)

**AP Logic**:
- S=3 ≥ 9? NO
- S=3 ≥ 7 AND O=6 ≥ 4? NO
- S=3 ≥ 4 AND O=6 ≥ 7 AND D=5 ≥ 7? NO
- S=3 ≥ 4 AND O=6 ≥ 4? NO
- S=3 ≥ 7? NO
- O=6 ≥ 7 AND D=5 ≥ 7? NO
- **AP = L (Low)**

**Interpretation**: Low priority. The defect is cosmetic, so even though it occurs occasionally, it is not worth aggressive controls. Include in FMEA for traceability; standard manufacturing inspection is sufficient.

---

### Example 3: Software Timeout Not Implemented

- **Severity**: 8 (system hangs → loss of function)
- **Occurrence**: 7 (complex code path, inadequate testing → O=7)
- **Detection**: 9 (no real-time watchdog, error only discovered in customer field testing)

**AP Logic**:
- S=8 ≥ 9? NO
- S=8 ≥ 7 AND O=7 ≥ 4? **YES** → AP = **H (High)**

**Interpretation**: High priority. Severity is major system malfunction, Occurrence is moderate-to-high, and Detection is weak (hidden until field). **Required action**: Implement watchdog timer + timeout handling, validate with integration testing before production.

---

### Example 4: Packaging Tape Residue

- **Severity**: 2 (hidden, non-functional)
- **Occurrence**: 5 (occasional process issue)
- **Detection**: 3 (internal visual inspection catches most, but some escape)

**AP Logic**:
- S=2 ≥ 9? NO
- S=2 ≥ 7 AND O=5 ≥ 4? NO
- S=2 ≥ 4 AND O=5 ≥ 7 AND D=3 ≥ 7? NO
- S=2 ≥ 4 AND O=5 ≥ 4? NO
- S=2 ≥ 7? NO
- O=5 ≥ 7 AND D=3 ≥ 7? NO
- **AP = L (Low)**

**Interpretation**: Low priority. Severity is negligible (cosmetic, not functional), so AP is Low regardless of Occurrence. Standard QA inspection is adequate.

## Action Plan Tracking by AP

| AP | Action Status | DFMEA Tracking | Closure Criteria |
|----|---|---|---|
| **H** | Open | Action Plan Tracker; updates DFMEA worksheet with "Action Taken" | Verification test passes; residual risk documented; sign-off by engineering lead |
| **M** | Open | Action Plan Tracker; may include in Control Plan | Action completed and verified; residual AP ≤ M confirmed |
| **L** | Monitor | Included in FMEA for audit trail; no Action Plan entry unless discovered in testing | Standard validation controls are sufficient; closure rate not tracked |

## Key Principle: Severity First

The AIAG-VDA AP method enforces a design philosophy: **never accept high-severity failures, regardless of how rare or easy to detect**. This aligns with safety standards like ISO 26262, which require that hazardous failures be either prevented (high design integrity) or detected with high coverage (diagnostic mechanisms). A "detectable-but-latent" high-severity failure is still a liability.
