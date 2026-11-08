# ISO 26262-5 Metric Targets — Complete Reference

## SPFM (Single Point Failure Metric)

The **Single Point Failure Metric (SPFM)** measures the percentage of detected single failures relative to total single failures.

**Formula:** SPFM = (λ_SPF) / (λ_SPFM_target) × 100%

Where λ_SPF is the rate of detected single failures with sufficient DC.

### SPFM Targets per ASIL:

| ASIL | SPFM Minimum |
|------|-------------|
| QM | — |
| A | — |
| B | 90% |
| C | 97% |
| D | 99% |

**Rationale (ISO 26262-5 Table 3):** Higher ASIL requires better detection of single failures to ensure safety mechanisms catch faults before reaching the driver.

---

## LFM (Latent Fault Metric)

The **Latent Fault Metric (LFM)** measures the percentage of failures that are detected within a safe operational window (e.g., power cycle, diagnostics).

**Formula:** LFM = (λ_LF_detected) / (λ_LF_total) × 100%

Where λ_LF includes dormant faults that could combine with other failures.

### LFM Targets per ASIL:

| ASIL | LFM Minimum |
|------|------------|
| QM | — |
| A | — |
| B | 60% |
| C | 80% |
| D | 90% |

**Rationale (ISO 26262-5 Table 4):** Higher ASIL requires faster detection of latent faults to prevent dual-point failures (single fault + latent fault).

---

## PMHF (Probabilistic Metric for Hardware Failures)

The **Probabilistic Metric for Hardware Failures (PMHF)** is the probability of a hardware failure causing a hazardous event, expressed in **Failures In Time (FIT)**.

1 FIT = 1 failure per 10^9 hours

**Formula:** PMHF = Σ λ_dangerous_undetected (in FIT)

Includes:
- λ_RF (residual failures after safety mechanisms)
- λ_MPF_L (latent Multiple Point Failures not detected within operational window)
- λ_S (Safe failures — excluded)

### PMHF Targets per ASIL:

| ASIL | PMHF Maximum |
|------|-------------|
| QM | — |
| A | — |
| B | < 100 FIT |
| C | < 100 FIT |
| D | < 10 FIT |

**Rationale (ISO 26262-5 Section 7):** PMHF directly bounds the probability of hardware causing hazard. Lower ASIL tolerates higher PMHF; ASIL D (critical functions) requires < 10 FIT.

---

## Diagnostic Coverage (DC)

**Diagnostic Coverage** is the percentage of failures detected by a safety mechanism within the required time window.

DC % = (detected failures) / (total failures) × 100%

- **0% DC**: No detection; residual failure = total failure
- **100% DC**: All failures detected; residual failure approaches zero

### DC grades per ISO 26262-5 Table 5:

| DC Range | Grade |
|----------|-------|
| 0% < DC < 60% | Low |
| 60% <= DC < 90% | Medium |
| 90% <= DC < 99% | High |
| 99% <= DC <= 100% | Very High |

Higher DC reduces λ_residual and improves SPFM/LFM metrics.

---

## Example Calculation Chain

### Scenario: ASIL D Electronic Control Unit (ECU)

**Input:**
- λ_total = 150 FIT (total failure rate from IEC 62380)
- Target ASIL = D
- Safety mechanisms: Watchdog (DC=95%), CRC (DC=90%)

**Distribution across HW elements:**
- Processor: 80 FIT (60 FIT SPF + 20 FIT RF)
- Memory: 40 FIT (30 FIT SPF + 10 FIT RF)
- Comms: 30 FIT (all SPF, detected by watchdog)

**SPFM Calculation:**
- SPF with DC >= 90% = 60 (watchdog) + 30 (watchdog) + 30 (watchdog) = 120 FIT
- Total SPF = 120 FIT
- SPFM = (120 / 120) × 100% = **100%** ✓ (ASIL D target: >= 99%)

**LFM Calculation:**
- Latent failures not detected in 1 month = 15 FIT
- Total latent = 15 FIT
- LFM = (0 / 15) × 100% = **0%** ✗ (ASIL D target: >= 90%)
- **Action**: Add periodic self-test or increase diagnostic window

**PMHF Calculation:**
- λ_RF (residual) = 20 + 10 = 30 FIT
- λ_MPF_L (latent) = 15 FIT
- PMHF = 30 + 15 = **45 FIT** ✓ (ASIL D target: < 10 FIT)
- **Action**: Increase DC or add redundancy to reduce undetected failures

---

## References

1. **ISO 26262-5:2018**, Section 8 — Hardware Safety Metrics
2. **ISO 26262-5:2018**, Annex A — Detailed ASIL Determination Tables
3. **IEC 62380:2020** — Reliability data for electronic components for use in telecommunications equipment
4. **FIDES 2022** — Failure rates and reliability prediction model (alternative to IEC 62380)

---

## Conformance Checklist

✓ SPFM target met for target ASIL  
✓ LFM target met for target ASIL  
✓ PMHF target met for target ASIL  
✓ All failure modes classified  
✓ All safety mechanisms have DC specified  
✓ FIT source (IEC 62380 / FIDES / datasheet) justified  

**If all three checks pass, hardware safety case is APPROVED.**
