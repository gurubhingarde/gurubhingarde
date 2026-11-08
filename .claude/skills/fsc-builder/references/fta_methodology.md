# Fault Tree Analysis (FTA) Methodology for FSC Derivation

## Why FTA for the FSC

The Functional Safety Concept (FSC) translates safety goals into functional safety requirements (FSRs) that, when satisfied, prevent violation of the safety goals. Fault tree analysis is the most widely adopted deductive technique for this translation because it forces analysts to ask "what could cause this top-level event?" recursively, leaving an auditable derivation trail behind every requirement.

ISO 26262-9, Clause 8 (Safety Analyses) recognises FTA as a valid deductive analysis at both the system and hardware levels. ISO 26262-3, Clause 7.4 then requires that the FSC define functional safety requirements **with sufficient rigor that safety goals are met under all foreseeable single-point and multi-point fault conditions**. The FTA is how that rigor is demonstrated.

## Top-level event convention

For each safety goal SG-XXX produced by the HARA, build one fault tree whose **top-level event** is the violation of that safety goal. State it in active voice with the SG ID for traceability:

> Violation of SG-001: Unintended single-wheel brake application at highway speed (i.e., the underlying hazardous event occurs).

Equivalent phrasing using the original hazardous event from the HARA worksheet is acceptable and sometimes clearer for reviewers.

## The standard three-branch decomposition

Beneath the top-level event, place a single **OR gate** connecting three standard intermediate events that exhaustively partition the failure space for any controllable function:

1. **Input failure** — A signal entering the item is wrong, missing, late, stuck, or out of specification. This includes sensor faults, upstream ECU communication errors, sensor power/grounding faults, and signal-conditioning errors.
2. **Process failure** — The item's internal computation, state machine, arbitration, plausibility check, or stored configuration is wrong. This includes CPU faults, memory faults, software defects, timing faults, and resource contention.
3. **Output failure** — The actuator command produced by the item is wrong, missing, late, or rejected. This includes actuator driver faults, end-stage shorts/opens, harness faults, mechanical jamming of the actuated element, and downstream-ECU rejection.

The three-branch OR gate is intentionally complete: every basic event the analyst will discover later belongs to exactly one of these three branches. This completeness is what makes the FTA reproducible across analysts.

## Expanding each branch against the block diagram

Each of the three intermediate events expands into an OR gate connecting one **basic event per ASIL-relevant node** in the block diagram that contributes to that branch:

- **Input failure** branch → one basic event per sensor or upstream ECU node.
- **Process failure** branch → one basic event per processor / SW partition / arbitration node.
- **Output failure** branch → one basic event per actuator driver / actuator / downstream ECU node.

A node that appears in more than one branch (e.g., a microcontroller that performs both input plausibility checking AND output command computation) is decomposed into separate basic events per role; this prevents understating its impact during ASIL allocation.

## Where AND gates appear

ISO 26262 functional safety concepts predominantly produce OR-gated trees because the FSC must address single-point faults exhaustively. AND gates only appear when:

1. Two genuinely independent items must both fail to violate the safety goal — e.g., a primary controller AND its lockstep companion. This is the construction that justifies ASIL decomposition (covered in `asil_decomposition.md`).
2. A latent safety mechanism failure must coincide with a primary fault — used to model multi-point fault scenarios required by ISO 26262-5 hardware metrics.

The `fsc-builder` skill never auto-inserts AND gates. The analyst introduces them explicitly during decomposition review, and the skill records the independence claim in the ASIL Allocation tab so reviewers can challenge it.

## Basic event → FSR mapping

Each basic event is rephrased into a positive-form requirement statement using this template:

> The item shall detect <basic event> and transition to the safe state within <FTTI> ms.

For an FSR derived from a sensor input failure, the canonical wording is:

> The item shall detect implausible, missing, or stuck readings from <sensor name> and transition to the safe state within <FTTI> ms.

This wording keeps the FSR atomic, verifiable, and traceable both upward to the safety goal and downward to the technical safety requirements that will be developed in the TSC.

## Common pitfalls

1. **Skipping the three-branch decomposition.** Going directly from the top event to per-node basic events looks faster but produces uneven trees that miss whole failure classes (especially output rejection by downstream ECUs).
2. **Treating FTA as a probability calculation.** Functional-level FTA is structural; quantitative FTA with FIT rates belongs to the hardware safety analysis (FMEDA) downstream. The FSC tree is qualitative.
3. **Omitting nodes the analyst "knows are safe".** Every ASIL-relevant node MUST appear as a basic event. Excluding nodes pre-emptively requires a documented justification that the FSC reviewer will demand.
4. **Allowing implicit AND gates.** "These two will never fail together" is a claim that requires evidence (independence analysis, common-cause review). The skill records this claim explicitly under ASIL decomposition.
