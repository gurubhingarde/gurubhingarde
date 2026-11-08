# Functional Safety Requirement (FSR) Templates

Each basic event in the fault tree produces one FSR. Good FSRs are atomic, positively phrased, verifiable, and traceable. The templates below are starting points — the analyst refines them with item-specific specifics.

## Universal structure

> The item **shall** <verb the safety mechanism performs> <object: the fault, signal, or output> <within FTTI / under condition> **and** <transition to safe state | maintain function | warn driver>.

Two halves: the **detection** clause and the **reaction** clause. Both must be present, otherwise the FSR is incomplete from a safety-mechanism perspective.

## Templates by branch

### Input failure branch

Sensor signal plausibility:

> The item shall detect implausible, out-of-range, or stuck readings from <sensor name> within <detection time> ms and transition to the safe state within <FTTI> ms.

Sensor-pair cross-check:

> The item shall continuously cross-check <sensor A> against <sensor B> and detect deviations exceeding <threshold> for longer than <persistence time> ms, then transition to the safe state within <FTTI> ms.

Communication signal validity:

> The item shall detect missing, stale, or CRC-invalid messages on <bus / signal name> within <detection time> ms and substitute a defined default value or transition to the safe state within <FTTI> ms.

Sensor power / supply:

> The item shall detect sensor supply voltage outside the qualification range and disable the dependent function within <detection time> ms.

### Process failure branch

CPU integrity:

> The item shall detect CPU faults via <lockstep | dual-channel comparison | program-flow monitoring | online self-test> with diagnostic coverage ≥ <DC>%, and transition to the safe state within <FTTI> ms upon detection.

Memory integrity:

> The item shall detect single-bit memory faults using ECC and double-bit faults via SECDED (or dual-channel comparison), and transition to the safe state within <FTTI> ms.

Software timing / scheduling:

> The item shall detect missed deadlines of safety-critical tasks via a window watchdog and reset to the safe state within <FTTI> ms.

Configuration / calibration:

> The item shall verify the integrity of safety-relevant calibration data at startup using a CRC and inhibit the safety-related function on integrity failure.

State machine consistency:

> The item shall detect impossible state transitions in <state machine name> and transition to the safe state within <FTTI> ms.

### Output failure branch

Actuator driver feedback:

> The item shall continuously monitor the response of <actuator> to commands via <current sensing | position feedback | echo readback> and detect deviations exceeding <threshold> within <detection time> ms.

Actuator end-stage diagnosis:

> The item shall detect open-circuit, short-to-supply, and short-to-ground conditions on <actuator output> within <detection time> ms and transition to the safe state within <FTTI> ms.

Command rejection by downstream ECU:

> The item shall verify acknowledgement of <command name> by <downstream ECU> within <ack timeout> ms and transition to the safe state on absence of acknowledgement.

Disable command:

> The item shall be capable of disabling <actuator> independently of the primary control path, with the disable command authority preserved under any single-point fault.

## Driver warning and degraded operation

Whenever the safe state is "function disabled with driver retaining control", a paired FSR is required for warning:

> The item shall illuminate <indicator> and (optionally) emit <chime / haptic feedback> upon transitioning to the safe state, and shall maintain the indicator until the fault clears or the next ignition cycle, whichever is later per OEM convention.

If a degraded mode is permitted (rare in chassis safety, common in propulsion):

> The item may continue providing <degraded function> after detecting <fault class> provided the degraded function does not violate the safety goal.

The "may" here is intentional: degraded operation is permissive and must be paired with a positive verification that the degraded mode itself does not introduce hazards.

## Auto-generation behaviour of the skill

For each basic event, the script picks the template that matches the branch (Input/Process/Output) and the node type (sensor/processor/actuator/comm). It substitutes the node name and the safety goal's FTTI. It leaves the detection time, persistence threshold, and downstream ECU placeholders as `<TBD>` for the analyst to fill during the FSC review pass — these depend on the timing budget allocation that is part of the FSC narrative, not derivable from the HARA alone.

The FSR ID convention is `FSR-<SG_ID without prefix>-<NN>`. So safety goal SG-001 produces FSR-001-01, FSR-001-02, etc. This keeps the FSR ID stable even when FSRs are reordered during review, because the numeric suffix corresponds to the order in which the basic events appear in the fault tree.
