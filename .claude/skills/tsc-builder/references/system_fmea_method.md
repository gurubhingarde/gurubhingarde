# System-Level FMEA Method (per ISO 26262-9 §8 and AIAG-VDA FMEA Handbook)

The TSC includes a system-level FMEA as a **structured complement** to the FTA. Where the FTA is deductive (top-down, starting from a hazard), the FMEA is inductive (bottom-up, starting from each component / interface). Together they cross-check each other — every basic event in the FTA should appear as an effect path in the FMEA, and every high-severity FMEA effect should be traceable to a basic event in the FTA.

## Structure

For each architectural element (block-diagram node), enumerate failure modes and their effects through the chain to the vehicle level:

| Column           | Purpose                                                                              |
|------------------|--------------------------------------------------------------------------------------|
| Element / Node   | Block-diagram node ID and name.                                                      |
| Failure Mode     | The way the element can fail (stuck, drift, omit, commit, etc.).                     |
| Local Effect     | Effect at the element's output.                                                      |
| Subsystem Effect | Effect at the subsystem boundary.                                                    |
| Vehicle Effect   | Effect on vehicle behavior.                                                          |
| Linked SG / FSR  | Which safety goal and FSR address this failure.                                      |
| Existing Mechanism | The detection/reaction mechanism (from the Safety Mechanism Catalog).             |
| DC%              | Diagnostic coverage of the existing mechanism (from FMEDA, fault injection, or Annex A). |
| Residual Risk    | What remains after the mechanism — the input to the safety case argument.            |

## Failure mode taxonomy (auto-suggested per node type)

| Node type   | Default failure modes                                                                     |
|-------------|-------------------------------------------------------------------------------------------|
| sensor      | No output, stuck output, drifted output, noisy output, out-of-range output.               |
| comm_in     | Lost message, late message, repeated message, corrupted message, masquerade.              |
| power_in    | Loss of supply, undervoltage, overvoltage, supply transient.                              |
| processor   | Stuck-at fault, transient bit flip, lockstep mismatch, watchdog timeout, illegal opcode.  |
| software    | Missed deadline, illegal state, stack overflow, mutex deadlock, division by zero.         |
| memory      | Single-bit flip, multi-bit flip, write through, read disturb, address decoder fault.      |
| driver      | Open output, short to supply, short to ground, gate driver fault, thermal shutdown.       |
| actuator    | Stuck open, stuck closed, slow response, partial response, mechanical jam, pressure leak. |
| comm_out    | Message not sent, late, wrong content, sender ID spoof, ack absent.                       |

The TSC generator pre-populates one FMEA row per (element × failure mode) pair using these defaults. The analyst trims, refines, and adds project-specific failure modes.

## Cross-check with the FTA

Every FTA basic event → matching FMEA row exists.
Every FMEA Vehicle Effect rated as a hazard → matching FTA basic event exists.
Either direction missing is a flag for the analyst to investigate.

## Common pitfalls

1. **Failure modes restricted to "the function fails".** Use the taxonomy — stuck, drift, intermittent, partial — these are different fault classes that may be handled by different mechanisms.
2. **Vehicle effect language too vague.** "Loss of stability" is unhelpful; "vehicle yaws unintentionally during cornering at >80 km/h" is useful because it ties back to a specific HARA hazardous event.
3. **Skipping the DC% column.** Without DC% the FMEA cannot inform the FMEDA, and the safety case has nothing to cite. `<TBD>` is acceptable as a placeholder, "n/a" is not.
