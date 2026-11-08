# Hardware-Software Interface (HSI) Specification

## Why the HSI matters

The HSI is the contract between hardware diagnostic features and software safety reactions. ISO 26262-4 §6.4.6 and §7 require it as the canonical artefact that binds HW and SW work together. Without a frozen HSI the HW team and SW team make contradictory assumptions about who owns each safety mechanism, and the resulting integration problems are usually discovered very late in the program when they are most expensive to fix.

## What the HSI captures (per safety mechanism)

For every safety mechanism that crosses the HW/SW boundary, the HSI records:

- **HSI signal name** — stable identifier, used in code, register documentation, test scripts.
- **Direction** — HW→SW (diagnostic flag, status, fault notification) or SW→HW (control, enable, reset).
- **Encoding** — bit width, polarity, units, reserved values.
- **Timing** — sample/update rate, maximum age the SW may consume, latency budget.
- **Integrity protection** — parity, CRC, redundant register, plausibility check.
- **Failure reaction** — what SW does on signal fault; what HW does on absence of SW response.
- **Validity / liveness signal** — companion bit or counter that indicates the producer is alive and the value is current.
- **Allocated FSR / TSR IDs** — traceability back to the safety requirement that needs this signal.

## HSI taxonomy

| Category                        | Examples                                                                |
|---------------------------------|-------------------------------------------------------------------------|
| HW diagnostic flags (HW→SW)     | Lockstep mismatch, ECC error, watchdog reset cause, supply OV/UV.       |
| HW status (HW→SW)               | ADC ready, DMA complete, CAN bus state, current/voltage measurement.    |
| SW commands (SW→HW)             | Actuator enable, set output PWM, reset diagnostic counter, mode change. |
| SW liveness (SW→HW)             | Watchdog refresh, heartbeat counter, deadline acknowledgement.          |
| Cross-CPU signals (when applicable) | Inter-core mailbox, shared memory mutex, lockstep compare bit.       |

## Signal-naming convention

Use a stable, dot-separated convention:

```
<subsystem>.<role>.<signal>
e.g.  esc.diag.lockstep_mismatch
      esc.cmd.modulator_enable
      esc.live.sw_heartbeat_500ms
      esc.status.adc_yaw_ready
```

The TSC generator pre-populates names using this convention based on the FSR's branch and node, but the analyst is expected to refine.

## Common HSI mistakes to avoid

1. **Implicit reaction times.** "SW reacts to lockstep mismatch" without a numeric latency budget is unverifiable. The TSC tab requires a worst-case reaction time in ms.
2. **Forgetting the inverse direction.** Most safety mechanisms need both an HW→SW flag AND an SW→HW acknowledge so the HW knows the SW saw the fault. The skill drafts both rows by default.
3. **Confusing initialization with steady state.** Power-on diagnostic sequencing has different timing constraints than runtime monitoring — record both rows when relevant.
4. **No validity bit.** A "0" in a status field means either "the reading is zero" or "the producer is dead". Add a companion validity bit so SW can tell the difference.
5. **HSI signals not mapped to FSRs.** Every HSI row must trace to at least one FSR or one HW-TSR/SW-TSR; orphan signals signal an incomplete safety analysis or a feature that is not actually safety-related.
