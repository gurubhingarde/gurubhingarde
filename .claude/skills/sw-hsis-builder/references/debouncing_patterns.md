# Debouncing Patterns — Comparison and Selection Guide

Every HSI signal handler needs debouncing protection against noise, transients, and jitter. This document compares four standard methods and guides parameter selection.

## 1. N-of-M Filter (Majority Voting)

**How it works:** Sample the signal M times at a fixed rate. If at least N consecutive samples agree, the debounced value transitions. If fewer than N samples agree, no state change.

**Example: 3-of-5 filter**
- Sample 5 times at task rate (e.g., every 50 ms → 250 ms window).
- If 3+ samples equal '1', output transitions to '1'.
- If fewer than 3 samples equal '1', output stays at '0'.

**Advantages:**
- Simple to implement (circular buffer of size M).
- Deterministic behavior (no state machine surprises).
- Symmetric latency (same delay for rising and falling edges).
- Well-understood by auditors; common in ISO 26262 practice.

**Disadvantages:**
- Latency: (N-1) × sample_period to detect signal change. For 3-of-5 at 50ms per sample, latency = 2 × 50 = 100 ms.
- Memory: O(M) per signal (small).
- Not optimal for analog signals with continuous noise (time-based better).

**False-positive risk:**
- Probability that N consecutive random samples match despite signal fault.
- For 3-of-5 with 50% noise: P(false positive) ≈ C(5,3) × (0.5)^5 ≈ 0.31.
- For high ASIL (D), use larger M or increase N (e.g., 7-of-9).

**Parameter selection:**
- **M:** Total number of samples. Larger M (e.g., 7, 9, 11) reduces false-positive risk but increases latency.
- **N:** Consensus threshold. Typically N = ceil(M/2) + 1 (2/3 majority). Can increase N for stricter requirements.
- **Sample rate:** Typically task period (e.g., 50 ms for a 50 ms diagnostic task).

**Validation approach:**
- Test with injected noise (single-bit faults in the window).
- Measure actual latency from signal change to debounced output.
- Validate against false-positive budget.

## 2. Time-Based Persistence (Temporal Filtering)

**How it works:** A signal must remain in the target state for a minimum duration T before the debounced output transitions.

**Example: 100 ms persistence**
- Signal must stay '1' for at least 100 ms before output transitions to '1'.
- If signal returns to '0' before 100 ms, the timer resets.

**Advantages:**
- Intuitive for continuous noise (e.g., electrical noise on analog lines).
- Suited to signals with time-domain characteristics (e.g., RC-filtered analog-to-digital conversion).
- Asymmetric delays can be tuned per rising/falling edge.

**Disadvantages:**
- Latency depends on T (typically T = multiple task periods).
- Requires a timer per signal (larger state overhead than N-of-M).
- State machine complexity (e.g., "waiting for rising edge", "debounced high", "waiting for falling edge").
- Edge-case: what if task period >> T? (T < 50 ms but task runs every 50 ms → missed edges).

**False-positive risk:**
- Probability that noise maintains target state for duration T.
- For Gaussian noise, depends on noise amplitude, sample rate, and T.
- For impulse noise (spikes), depends on spike width. If T > typical spike width, false-positive risk is low.

**Parameter selection:**
- **T (threshold time):** Chosen to exceed expected transient duration. For electrical noise with ~10 ms RC time constant, set T = 20–50 ms.
- **Rising/falling time:** Can differ. Example: 100 ms to assert fault (slow), 50 ms to clear (fast) → asymmetric behavior.
- **Sample rate:** Task period. If T < task period, risk of missed transitions. Ensure T >= 2 × task period.

**Validation approach:**
- Inject step input (signal held at '1' for increasing durations). Measure latency vs. duration.
- Inject noise bursts of varying width. Measure false-positive rate for burst widths below T.
- Test edge case: task preemption causes missed samples.

## 3. Hysteresis (Deadband with History)

**How it works:** Output transitions on signal crossing thresholds V_high and V_low, not on a single threshold. Memory of previous state prevents oscillation near threshold.

**Example: Temperature sensor with hysteresis**
- Output "high" if signal > 80°C.
- Output "low" if signal < 75°C.
- In the 75–80°C band, output retains previous state (hysteresis).
- Prevents oscillation if signal dithers near 77.5°C.

**Advantages:**
- Suited to analog signals with noisy thresholds (e.g., voltage, temperature, pressure).
- Very low false-positive risk once established (output sticks until threshold clearly crossed).
- Minimal state overhead (one boolean: previous output state).
- Low latency for clean transitions (no waiting for samples or timer).

**Disadvantages:**
- Asymmetric thresholds add complexity. Must tune V_high and V_low independently.
- Non-deterministic latency (depends on signal proximity to thresholds).
- Risk of "sticking" state if hysteresis band is too large (signal never crosses back).
- Less suitable for digital signals (which don't have natural threshold ranges).

**False-positive risk:**
- Once hysteresis established, very low. Requires signal to cross V_high (or V_low) by >band_width.
- Initial transition risk (before history established): depends on signal noise and threshold proximity.

**Parameter selection:**
- **V_high, V_low:** Thresholds. Typically V_high - V_low = 2 × expected_noise_amplitude.
- **Example:** Nominal 5 V, noise amplitude ±0.5 V → V_high = 5.5 V, V_low = 4.5 V.
- **Initialization:** Set initial output state based on HSI register value (e.g., signal between V_low and V_high → output = 0).

**Validation approach:**
- Ramp signal through V_low and V_high. Verify transitions at correct thresholds.
- Dither signal in hysteresis band. Verify output remains stable.
- Measure false-positive rate vs. noise amplitude (should scale as noise >> hysteresis band).

## 4. Leaky-Bucket Filter (Probabilistic Counter)

**How it works:** Maintain a counter. Increment on signal '1', decrement on signal '0' (or vice versa). Output transitions when counter exceeds threshold. Counter "leaks" (resets gradually) if signal is stable.

**Example: Leaky bucket with threshold 3**
- Counter increments on signal '1', decrements on signal '0'.
- Output transitions to '1' when counter >= 3.
- Output transitions to '0' when counter <= 0.
- Counter can "leak" (slowly decrement) to prevent sticking if signal is marginally '1'.

**Advantages:**
- Graceful degradation under intermittent faults. Repeated faults increase counter more than random noise.
- Effective for signals with rare glitches in heavy noise.
- Memory: O(1) (one counter per signal).
- Can be tuned to favor fault detection over false-positive avoidance.

**Disadvantages:**
- Non-deterministic latency (depends on signal burst pattern, not just duration).
- Tuning is complex (increment rate, decrement rate, leak rate, threshold).
- Less common in ISO 26262 practice; requires detailed validation.
- Can "stick" if leak is too slow (counter does not reset even if signal is stable).

**False-positive risk:**
- Depends on increment/decrement/leak rates and threshold. Requires statistical analysis or simulation.
- For persistent noise bursts (duration > threshold / increment_rate), false-positive risk is significant.

**Parameter selection:**
- **increment_rate, decrement_rate:** How many counts per sample on signal '1' vs. '0'. Often 1.
- **leak_rate:** How fast counter decays (e.g., -1 per task period when no signal transition). Set to zero if no leak desired.
- **threshold:** Counter value to trigger transition. Higher threshold → lower false-positive risk, higher latency.

**Validation approach:**
- Inject repeating fault patterns (fault for 1 sample, then gap). Measure detection latency.
- Inject random noise. Measure false-positive rate vs. noise amplitude.
- Simulate or measure worst-case latency (longest time to reach threshold from rest).

## Comparison Table

| Aspect | N-of-M | Time-Based | Hysteresis | Leaky-Bucket |
|--------|--------|------------|------------|--------------|
| **Latency** | (N-1) × Ts | T | ≈0 (clean) | variable |
| **Memory** | O(M) | O(1) | O(1) | O(1) |
| **Noise immunity** | Good (majority) | Excellent (time domain) | Excellent (threshold) | Good (gradual) |
| **False-positive risk** | Binomial(M, N, p) | Time-dependent | Low (once established) | Configurable |
| **Suitable for** | Digital signals | Analog signals, continuous noise | Analog threshold decisions | Rare glitches in noise |
| **Auditor familiarity** | High (ISO 26262 standard) | Medium | Medium | Low |
| **Tuning complexity** | Low (M, N) | Low (T) | Medium (V_high, V_low) | High (multiple rates) |

## Selection Decision Tree

1. **Is the signal digital or analog?**
   - **Digital:** → N-of-M or Hysteresis (if thresholds well-defined).
   - **Analog:** → Time-based, Hysteresis, or Leaky-Bucket.

2. **Is noise Gaussian (continuous) or impulse (spikes)?**
   - **Gaussian:** → Time-based (persistent filtering) or Leaky-Bucket.
   - **Impulse:** → N-of-M (majority voting) or Hysteresis (deadband).

3. **What is the FTTI budget?**
   - **Tight (< 100 ms):** → Hysteresis (low latency) or N-of-M with small M.
   - **Loose (> 200 ms):** → N-of-M with larger M, Time-based with longer T, or Leaky-Bucket.

4. **Do you need deterministic latency?**
   - **Yes:** → N-of-M (deterministic) or Time-based (deterministic but longer).
   - **No:** → Hysteresis or Leaky-Bucket (variable latency, lower overhead).

5. **False-positive risk budget?**
   - **Very tight (ASIL D, < 0.1%):** → N-of-M with large M (e.g., 7-of-9) or strict Hysteresis.
   - **Moderate (ASIL B-C, < 1%):** → N-of-M (3-of-5 or 5-of-7) or Time-based with T = 2–3 × Ts.
   - **Loose (ASIL QM-A, < 5%):** → Hysteresis or simple Time-based.

## Example Allocations (ESC Domain)

**esc.diag.lockstep_mismatch (ASIL C, HW->SW diagnostic, digital)**
- **Method:** 3-of-5 N-of-M
- **Rationale:** Digital fault indication, auditor-familiar, moderate latency.
- **Sample rate:** 50 ms (T02_Diag task period).
- **Latency:** 2 × 50 = 100 ms.
- **False-positive risk:** ≈0.31 for random noise.

**esc.live.liveness_counter (ASIL B, HW->SW liveness, digital)**
- **Method:** Time-based, 1 × 50 ms persistence
- **Rationale:** Liveness counter increments every period; time-based detects missing increments.
- **Detection time:** If counter stuck for 50 ms → 50 ms latency to detect timeout.
- **False-positive risk:** Low (only if HW liveness truly stops).

**esc.status.pressure (ASIL A, SW->HW analog setpoint, 0–5 V)**
- **Method:** Hysteresis, V_high = 2.6 V, V_low = 2.4 V (nominal 2.5 V ±0.1 V)
- **Rationale:** Analog value, low criticality, low false-positive risk near nominal.
- **Latency:** ~0 (clean transitions), variable if dithering near threshold.
- **False-positive risk:** Very low if signal noise < hysteresis band.

## Testing Debouncing

Every debounce implementation must be tested for:

1. **Nominal operation:** Signal transitions cleanly; output follows at expected latency.
2. **Noise immunity:** Random bit flips in sampled value; output remains stable if fault not persistent.
3. **Fault injection:** Sustained signal in fault state; output transitions at expected latency.
4. **Boundary condition:** Signal oscillates at hysteresis threshold or debounce boundary.
5. **Timing edge case:** Task preemption causes missed samples; verify graceful degradation.

Test evidence goes into **Tab 08 — Test Cases** of the SW-HSI workbook.
