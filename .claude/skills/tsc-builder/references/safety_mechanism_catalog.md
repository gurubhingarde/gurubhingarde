# Safety Mechanism Catalog

A safety mechanism is the implementation that satisfies the detection-and-reaction obligation of one or more safety requirements. This reference is the catalog the TSC generator draws from when proposing a starting set of mechanisms based on each FSR's branch and node type.

## Catalog format

Each mechanism has:
- **ID** — short stable identifier
- **Name** — what engineers actually call it
- **Type** — Detection, Reaction, or Combined
- **Applies to** — node types this mechanism is appropriate for
- **Typical Diagnostic Coverage (DC)** — order-of-magnitude target
- **Typical detection time** — order-of-magnitude target
- **HSI footprint** — what HSI signals it produces or consumes
- **Notes** — common pitfalls

## Detection mechanisms (process / processor)

| ID  | Name                       | Type      | Applies to       | Typical DC | Typical detection | HSI footprint                                          |
|-----|----------------------------|-----------|------------------|-----------|-------------------|--------------------------------------------------------|
| SM01 | Dual-core lockstep         | Detection | processor        | ≥99%      | < 1 µs            | `diag.lockstep_mismatch` (HW→SW), `cmd.lockstep_reset` |
| SM02 | Triple modular redundancy  | Detection | processor        | ≥99%      | < 1 cycle         | `diag.tmr_voter_state`                                 |
| SM03 | Program-flow monitoring    | Detection | processor + SW   | 90–95%    | one task period    | `diag.pfm_violation`, `live.pfm_token`                 |
| SM04 | Window watchdog            | Detection | processor + SW   | 90–95%    | one window         | `diag.wdg_reset_cause`, `live.sw_heartbeat`            |
| SM05 | ECC (SECDED) on RAM/Flash  | Detection | memory           | 99%+      | one access         | `diag.ecc_correctable`, `diag.ecc_uncorrectable`       |
| SM06 | Memory test at startup     | Detection | memory           | 90%       | startup time       | `diag.bist_result`                                     |
| SM07 | CRC over calibration       | Detection | memory           | ≥99%      | startup or periodic| `diag.cal_crc_ok`                                      |
| SM08 | MPU/MMU partition          | Detection | software         | n/a       | one access         | `diag.mpu_violation`                                   |
| SM09 | Static analysis + MISRA C  | Avoidance | software         | n/a       | dev-time           | none                                                   |

## Detection mechanisms (input)

| ID  | Name                       | Type      | Applies to       | Typical DC | Typical detection | HSI footprint                                          |
|-----|----------------------------|-----------|------------------|-----------|-------------------|--------------------------------------------------------|
| SM10 | Range / out-of-range check | Detection | sensor           | 60–80%    | one sample         | none (SW-only)                                         |
| SM11 | Plausibility cross-check   | Detection | sensor pair      | 80–95%    | a few samples      | none (SW-only)                                         |
| SM12 | Sensor diagnostic register | Detection | sensor + driver  | 90–99%    | per spec           | `diag.<sensor>.fault`                                  |
| SM13 | CAN/FlexRay E2E protection | Detection | comm_in/out      | ≥99%      | one cycle          | `diag.<bus>.e2e_fail`, `live.<bus>.counter`            |
| SM14 | Supply voltage monitor     | Detection | power_in         | ≥99%      | < 1 ms             | `diag.supply.uv_ov`                                    |
| SM15 | Sensor signal CRC          | Detection | digital sensor   | ≥99%      | one frame          | `diag.<sensor>.crc_ok`                                 |

## Detection mechanisms (output)

| ID  | Name                          | Type      | Applies to | Typical DC | Typical detection | HSI footprint                                         |
|-----|-------------------------------|-----------|------------|-----------|-------------------|-------------------------------------------------------|
| SM16 | Current / voltage feedback    | Detection | actuator   | 80–95%    | < 10 ms           | `status.<actuator>.current`, `diag.<actuator>.fault`  |
| SM17 | Position / encoder feedback   | Detection | actuator   | 90–95%    | < 1 motor cycle   | `status.<actuator>.position`, `diag.<actuator>.delta` |
| SM18 | Driver IC self-test (open/short)| Detection | driver    | 90–99%    | < 10 ms           | `diag.<driver>.short`, `diag.<driver>.open`           |
| SM19 | Downstream ack timeout        | Detection | comm_out   | n/a       | ack timeout        | `live.<msg>.ack_counter`                              |
| SM20 | Disable-path independence test| Avoidance | actuator   | n/a       | startup            | `cmd.<actuator>.disable_test`                         |

## Reaction mechanisms

| ID  | Name                          | Type     | Applies to        | Notes                                                            |
|-----|-------------------------------|----------|-------------------|------------------------------------------------------------------|
| SM30 | Transition to safe state      | Reaction | system            | Must be reachable from any state within FTTI - FDTI.             |
| SM31 | Disable actuator output       | Reaction | actuator + driver | Independent of primary control path; tested at startup.          |
| SM32 | Driver warning lamp + chime   | Reaction | HMI               | Persists until ignition cycle.                                   |
| SM33 | Degraded mode (limp)          | Reaction | propulsion / HVAC | Only permitted if degraded mode itself does not violate any SG.  |
| SM34 | Ignition cycle reset request  | Reaction | system            | Rare; typically reserved for unrecoverable faults.               |
| SM35 | DTC log + freeze frame        | Reaction | diagnostic        | Required for service tooling; not a safety mechanism on its own. |

## How the TSC generator uses this catalog

For each FSR, the generator picks 1–3 candidate detection mechanisms based on the FSR's branch and the linked node's type, and pairs each with the appropriate reaction mechanism. The result is one row per (FSR × candidate detection mechanism) in the Safety Mechanism Catalog tab. The analyst confirms the chosen mechanism, removes the alternatives, and fills in the project-specific DC% target (which is the input to the FMEDA produced under ISO 26262-5).

## Common pitfalls

1. **Single mechanism for multi-fault classes.** A range check catches stuck readings but not slow drift. Pair detection mechanisms; don't claim one covers everything.
2. **Mechanism shares the same channel as the function.** A SW plausibility check on the SW that just produced the value is not independent. Move plausibility to the safety MCU or to a dedicated monitor.
3. **DC% claims without evidence.** Every DC% claim needs a fault injection result, a reasoned argument from a recognized library (IEC 61508 Annex A), or supplier data. The TSC tab leaves DC% as `<TBD>` for the analyst to fill from the FMEDA.
