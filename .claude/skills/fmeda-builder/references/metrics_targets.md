# FMEDA Metrics & ASIL Targets — ISO 26262-5 §8

## Metric Definitions

### SPFM (Single-Point Failure Metric)

**Formula:**
```
SPFM = 1 - (Σ λ_SPF + Σ λ_RF) / Σ λ_safety_related
```

**Interpretation:** The fraction of hardware failures that are EITHER:
- **Safe** (do not violate any safety goal, e.g., a redundant signal line fails but the primary is unaffected), OR
- **Detected** by a safety mechanism (DC close to 100%)

**Units:** Dimensionless percentage (0–100%)

**Numerator (undetected + residual):**
- Σ λ_SPF = failure rates with NO allocated detection or DC = 0%
- Σ λ_RF = failure rates with detection allocated but DC < 100%; residual = λ × (1 - DC/100)

**Denominator (safety-related total):**
- Σ λ_safety_related = all failure rates for elements marked "safety_related": true in the HW BOM

**Example:**
- Total safety-related failure rate: 1000 FIT
- Undetected SPF: 5 FIT (lockstep detected all others)
- Residual RF (DC=95%): 5 FIT (5% of 100 FIT memory element with ECC)
- SPFM = 1 - (5 + 5) / 1000 = 1 - 0.01 = **99.0%**
- Target for ASIL D: ≥ 99% ✓ PASS

### LFM (Latent Fault Metric)

**Formula:**
```
LFM = 1 - Σ λ_MPF_L / (Σ λ_safety_related - Σ λ_SPF - Σ λ_RF)
```

**Interpretation:** The fraction of LATENT two-point faults that are detected by a secondary mechanism (e.g., periodic self-test, cross-check on next boot).

**Units:** Dimensionless percentage (0–100%)

**Numerator (latent two-point):**
- Σ λ_MPF_L = failure rates classified as latent multipoint faults. These are failures detected by the primary mechanism AFTER a latency window but not in real-time.
  - Example: A single-bit memory error that survives until the next memory test (periodic ECC scan, CRC boot check, or firmware self-test)
  - λ_MPF_L = λ × (1 - DC/100) for faults where the primary detection is periodic (not real-time)

**Denominator (safe latency window):**
- = Σ λ_safety_related - (Σ λ_SPF + Σ λ_RF)
- = Failures that are ALREADY safe or detected. These cannot combine with a second fault to violate a safety goal.
- **Interpretation:** The denominator shrinks as SPFM improves. A perfect SPFM = 100% means denominator = 0, and LFM is undefined (or treated as N/A).

**Example:**
- Total safety-related: 1000 FIT
- SPF + RF (already covered by primary detection): 100 FIT
- Remaining safe window for latent faults: 900 FIT
- Latent faults (failures detected but with 100 ms latency): 20 FIT
- LFM = 1 - 20 / 900 = 1 - 0.022 = **97.8%**
- Target for ASIL C: ≥ 80% ✓ PASS

**Design implication:** If SPFM is very high (e.g., 99.9%), the denominator becomes small, making it hard to achieve a high LFM. This is expected; the architecture is already so robust that latent two-point faults are rare. However, if SPFM is moderate (e.g., 90%), a poor LFM means that latent faults are a significant risk and require periodic diagnostics (e.g., BIST, CRC checks).

### PMHF (Probabilistic Metric for Hardware Failures)

**Formula:**
```
PMHF = Σ λ_SPF + Σ λ_RF  [FIT]
```

**Interpretation:** The raw failure rate of undetected + residual single-point faults.

**Units:** FIT (Failures In Time = failures per 10^9 operating hours)

**Relationship to SPFM:** PMHF is the "numerator" of SPFM before dividing by total FIT. It's a direct measure of risk, not a percentage.

**Example:**
- SPF failures: 5 FIT (no detection)
- RF failures: 5 FIT (95% detected, 5% slip through)
- PMHF = 5 + 5 = **10 FIT**
- Target for ASIL D: < 10 FIT ✗ FAIL (boundary case)

**PMHF is the most stringent metric for ASIL D.** A 10 FIT budget is only achievable with:
- Redundant detection paths (dual-core lockstep, E2E + CRC)
- Very low base FIT rates (mature, well-qualified components)
- Significant architectural margin (3σ over nominal stress)

---

## ASIL-Specific Targets

| Metric | ASIL A | ASIL B | ASIL C | ASIL D |
|--------|--------|--------|--------|--------|
| **SPFM** | 90% | 90% | 97% | 99% |
| **LFM** | 60% | 60% | 80% | 90% |
| **PMHF** | 100 FIT | 100 FIT | 100 FIT | 10 FIT |

### ASIL B (Safety-Critical)

- **SPFM ≥ 90%**: 10% of failures are undetected or residual. Achievable with single-layer detection (watchdog, CRC, basic parity).
- **LFM ≥ 60%**: 40% of latent two-point faults are undetected. Requires periodic diagnostics but not real-time verification.
- **PMHF < 100 FIT**: Total undetected failure rate must be < 100 FIT. For a 1000 FIT element, DC must be > 90% on average.

**Example architecture:**
- Watchdog timer + CRC over calibration
- ECC on safety-critical RAM
- Range checks on sensor inputs

### ASIL C (Highly Safety-Critical)

- **SPFM ≥ 97%**: Only 3% of failures slip through. Requires high-DC mechanisms or dual detection paths.
- **LFM ≥ 80%**: 80% of latent faults are detected by periodic checks. Demands frequent BIST or CRC cycles.
- **PMHF < 100 FIT**: Same as ASIL B; tighter average DC required.

**Example architecture:**
- Lockstep comparison on processor + independent watchdog
- SECDED on RAM (not just ECC)
- Dual-sensor voting with cross-checks
- Periodic CRC on all calibration + config

### ASIL D (Most Safety-Critical — Catastrophic Risk)

- **SPFM ≥ 99%**: Only 1% of failures are undetected. Requires dual-redundant detection or architectural tolerance.
- **LFM ≥ 90%**: Only 10% of latent two-point faults slip through. Demands continuous or very frequent diagnostics.
- **PMHF < 10 FIT**: Extremely stringent. A 100 FIT element can only contribute 0.1 FIT of undetected + residual failures.

**Example architecture:**
- Dual-core lockstep (99.9% SPF detection) + independent watchdog (catches lockstep failures)
- SECDED + periodic full-memory scan (99.9% RF + MPF_L coverage)
- E2E protection (CRC + counter + timeout) on all safety-critical messages
- Redundant sensors with plausibility cross-checks
- Architectural dual-channel design with periodic diagnostic switchover

**ASIL D rule of thumb:** If a single element contributes > 1 FIT undetected + residual, the entire architecture fails PMHF. Designers typically:
1. Choose the lowest-FIT components available
2. Allocate redundancy (dual-core, dual-sensor, dual-power path)
3. Implement overlapping detection mechanisms
4. Accept harsh cost/power penalties

---

## Derivation & Rationale

### Why SPFM ≥ 90% for ASIL B?

ISO 26262-5:2018, §8.3.3, sets SPFM thresholds based on the principle of "no single point of failure." An ASIL B requirement means that **any single detected failure must not violate the safety goal.** SPFM ≥ 90% provides a margin such that even with a few percent of failures slipping past detection, the aggregate risk remains acceptable.

Derivation (simplified):
- Random hardware failure rate per year: ~0.1% of installed base (1 in 1000 vehicles)
- Acceptable hazard frequency per safety goal: 10^-7 per operating hour (very rare)
- Operating hours per vehicle lifetime: ~15,000 hours
- Target failure rate for a single-point element: <10 FIT
- For a 100 FIT element, SPFM must be > 99% to stay below 1 FIT residual

### Why LFM ≥ 60% for ASIL B?

LFM guards against latent two-point faults. A latent fault is one that:
1. Has been detected by the primary mechanism (so it's not an SPF)
2. But is not yet fixed / acted upon by the system
3. Remains "live" in the system until the next diagnostic cycle

LFM ≥ 60% means that if a second failure occurs while the first is latent, there's a 60% chance the secondary mechanism (e.g., periodic BIST, periodic CRC) will catch it.

**Why lower than SPFM?** Because the window for latent faults is typically much smaller (e.g., once per hour, once per day). The probability of a second fault occurring during this window is rare. An LFM of 60% is considered adequate because:
- Probability of first fault: 1 in 100 hours (nominal 100 FIT element over 1000 hours/year ≈ 0.01% occurrence/operating hour)
- Probability of second fault during latency: 1 in 10,000 hours (much rarer)
- Combined probability of undetected two-point: ~10^-8, acceptable for ASIL B

### Why PMHF < 10 FIT for ASIL D?

PMHF is the "raw material" from which all undetected failures arise. For ASIL D (catastrophic consequences), even 100 FIT of residual failures is considered too high. The 10 FIT threshold is derived from:

- **Functional safety target:** ASIL D corresponds to a Functional Safety Integrity Level (FSIL) of 3 out of 4
- **Random Hardware Failure Rate (RHFR):** ISO 26262-5 Annex D provides a formula relating PMHF to ASIL. Simplified: PMHF_target ≤ 10 FIT
- **System-level risk budget:** If multiple subsystems (brake, steering, powertrain) are all ASIL D, the sum of PMHF across all safety goals must be < 10 FIT per goal

**Example:** An ESC (Electronic Stability Control) system with 3 safety goals (yaw stability, traction control, roll-over prevention):
- Each goal allocated ASIL D
- Each goal can have PMHF < 10 FIT
- Total system PMHF budget: < 30 FIT

---

## Excel Implementation (generate_fmeda.py)

The generator creates:

1. **`06_FMEDA_Worksheet`** tab with formulas for λ, λ_SPF, λ_RF, λ_MPF_L per row
2. **`07_SPFM_Calculation`** tab with SUMIF aggregations:
   ```
   =SUMIF('06_FMEDA_Worksheet'!SG_ID, SG_ID, '06_FMEDA_Worksheet'!lambda_SPF)
     / SUMIF('06_FMEDA_Worksheet'!SG_ID, SG_ID, '06_FMEDA_Worksheet'!lambda_total)
   ```
3. **`08_LFM_Calculation`** tab with similar SUMIFs for latent faults
4. **`09_PMHF_Calculation`** tab summing λ_SPF + λ_RF in FIT

Each tab includes a **Target column** (per ASIL) and a **Status column** (green = pass, yellow = caution, red = fail).

When the analyst updates a DC% in the FMEDA worksheet, all downstream formulas auto-recalculate. This enables rapid iteration and "what-if" analysis.

