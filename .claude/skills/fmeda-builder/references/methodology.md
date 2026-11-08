# FMEDA Methodology — ISO 26262-5 §8

## Overview

The FMEDA is a systematic enumeration of hardware failure modes, their effects on safety goals, and the diagnostic mechanisms designed to detect them. The analysis yields three mandatory metrics: SPFM, LFM, and PMHF.

## Process

### 1. Enumerate Failure Modes

For each hardware element (MCU, sensor, memory, power supply, driver IC, etc.), list all credible failure modes. Use IEC 62380 or IEC 61709 catalogs as a starting point; refine based on element type, technology, and operational environment.

**Example: MCU**
- Stuck-at (instruction or data bit permanently 0 or 1)
- Transient bit flip (single-event upset, alpha particle, cosmic ray)
- IO fault (output stuck high/low, input unresponsive)
- Oscillator fault (clock drift, loss of oscillation)

Assign each a **failure mode distribution %** representing its fraction of the element's total failure rate. E.g., MCU: stuck-at 30%, transient 40%, IO 20%, oscillator 10% = 100%.

### 2. Calculate Per-Mode Failure Rate

For each failure mode:

**λ_mode = FIT_total × (distribution % / 100)**

Example: MCU with FIT = 100, stuck-at at 30%:
- λ_stuck_at = 100 × 0.30 = 30 FIT

### 3. Allocate Safety Mechanisms

From the TSC, select a **detection mechanism** (e.g., lockstep comparison, ECC, watchdog, plausibility check) that detects this failure mode in-service. For each mechanism, assign a **Diagnostic Coverage (DC) percentage** representing the fraction of failures that will be detected before violating a safety goal.

DC is NOT 100% by default. It must be justified by:
- **Test data** (burn-in, HALT, stress testing)
- **Analytical coverage** (e.g., parity covers 1 bit flip but not 2; ECC covers single-bit but not double-bit without SECDED)
- **Design review** (e.g., watchdog can miss faults that occur during the watchdog period)
- **Operational experience** (e.g., CRC over calibration catches 99.6% of bit flips in production)

### 4. Classify Each Failure Mode

For each (element, failure mode) pair with an allocated mechanism:

- **Safe (S)**: Failure does not affect any safety goal. (No detection needed; λ_S = λ)
- **Single-Point Fault (SPF)**: Failure violates a safety goal, NO detection. (λ_SPF = λ)
- **Residual Fault (RF)**: Detection allocated but DC < 100%. Some failures slip through. (λ_RF = λ × (1 - DC/100))
- **Multi-Point Fault Detected (MPF_D)**: Second fault detected before combining with first. (λ_MPF_D = λ; counts toward LFM denominator, not numerator)
- **Multi-Point Fault Latent (MPF_L)**: Second fault undetected if first is still latent. (λ_MPF_L = λ × (1 - DC/100); worst-case latent risk)

### 5. Aggregate Metrics

Roll up per **safety goal** (SG), summing across all elements and failure modes:

#### SPFM (Single-Point Failure Metric)

Measures the fraction of safety-related failures that are either safe or detected.

**SPFM = 1 − (Σ λ_SPF + Σ λ_RF) / Σ λ_safety_related**

Equivalently: **SPFM = 1 − (Σ undetected failures) / (Σ safety-related failures)**

**Targets (per ASIL):**
- ASIL B: ≥ 90%
- ASIL C: ≥ 97%
- ASIL D: ≥ 99%

#### LFM (Latent Fault Metric)

Measures the fraction of latent two-point faults that are detected by a secondary mechanism (e.g., periodic self-test, secondary watchdog, cross-check on power-up).

**LFM = 1 − Σ λ_MPF_L / (Σ λ_safety_related − Σ λ_SPF − Σ λ_RF)**

The denominator is the "safe window" for latent faults — failures that are already detected or safe cannot become part of a two-point combination.

**Targets (per ASIL):**
- ASIL B: ≥ 60%
- ASIL C: ≥ 80%
- ASIL D: ≥ 90%

#### PMHF (Probabilistic Metric for Hardware Failures)

Raw failure rate of undetected + residual single-point faults, in FIT.

**PMHF = Σ λ_SPF + Σ λ_RF  [FIT]**

**Targets (per ASIL):**
- ASIL B: < 100 FIT
- ASIL C: < 100 FIT
- ASIL D: < 10 FIT

The ASIL D target is extremely stringent: a 10 FIT element can tolerate only ~0.001% residual failure rate if it's the sole contributor to a safety goal. This motivates heavy use of redundancy and high-DC mechanisms.

## Common Patterns

### Pattern 1: Dual-Core Lockstep (ASIL D workhorse)

Two cores execute the same instruction stream in lockstep. A hardware comparator detects any divergence in ~1 clock cycle.

- **DC**: 99.9% (misses only faults that diverge but escape lock-step comparison, e.g., uncommitted speculative state)
- **Residual**: ~0.1% of failures slip past
- **Preferred for**: Processor, memory-access controller
- **Cost**: 2× area, power, leakage current

### Pattern 2: Single-Bit Error Correcting Code (SECDED)

ECC on RAM/Flash detects up to 2-bit errors, corrects 1-bit errors on read.

- **DC**: ~97% (cannot recover from 3+ bit simultaneous flips; limited by error density in a single access window)
- **Residual**: ~3% multi-bit flips
- **Preferred for**: Embedded RAM, calibration/config storage
- **Cost**: ~8–10% memory overhead (parity bits)

### Pattern 3: CRC over Calibration

Periodic or boot-time CRC check of calibration constants.

- **DC**: 99.6% (CRC polynomial covers bit flips; unlikely to miss errors post-factory)
- **Update rate**: Boot or periodic (e.g., daily)
- **Risk**: Latent faults from boot until next check
- **Preferred for**: Read-only calibration, config registers
- **Cost**: Negligible (a few instructions per check interval)

### Pattern 4: Watchdog Timer

Independent timer asserts a safe-state transition if the main processor misses a periodic "I'm alive" kick.

- **DC**: 90–95% (sensitive to watchdog period; a fault that occurs just after the kick message has 1 watchdog period to propagate before detection)
- **Latency**: 1 watchdog period (typically 10–100 ms)
- **Preferred for**: SW deadlock, runaway loops, erratic behavior
- **Cost**: Minimal (a simple counter + RESET logic)

## FMEDA vs. System FMEA

- **FMEDA** (this analysis): Hardware-centric, failure-rate driven, metric-focused. Answers: "What is the undetected failure rate and how does it compare to ASIL targets?"
- **System FMEA** (TSC tab): Multi-layer (HW + SW + sensing + actuation), effect-centric, qualitative cross-check. Answers: "For each failure, what is the vehicle-level consequence and who detects it?"

The FMEDA feeds the System FMEA. For each failure mode in the System FMEA, there should be a corresponding row in the FMEDA with quantified DC and residual rates. If not, the failure is either non-detectable (DC = 0, λ_SPF = λ) or unimplemented (open item).

## Traceability

- **TSC → FMEDA**: Safety mechanisms + baseline DC% from TSC populate the FMEDA mechanism column
- **FMEDA → Verification Plan**: High residual-rate failures drive intensive verification (e.g., hardware test coverage, fault injection, burn-in)
- **FMEDA → Audit**: Metrics compared against ASIL targets. Any red = additional mitigation required

