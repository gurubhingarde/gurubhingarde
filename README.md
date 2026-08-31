# S32K144 Classic AUTOSAR BSW — POC

No-license path: NXP RTD (free MCAL) + S32 Design Studio + S32 Config Tool.
No RTE code-gen tool (tresos/DaVinci) — RTE layer is hand-written glue, not
AUTOSAR-certified. Fine for POC / non-safety prototype. Real ASIL cert later
needs NXP Safety RTD + a qualified config tool (separate license track).

## Layer map

```
App/              application SWCs (fault mgmt, vehicle logic)
Rte/              hand-written glue: SWC ports <-> Com API (stand-in for RTE gen)
Bsw/
  Services/
    EcuM/         ECU state manager (init/run/sleep)
    ComM/         communication manager (channel state)
    Os/           cooperative scheduler stand-in — see Bsw/Services/Os/README.md
  Communication/
    Can/          CAN driver — wraps MCAL FlexCAN (NXP RTD Can module)
    CanIf/        CAN interface — routes frames to/from Can driver
    PduR/         PDU router — Can <-> Com routing table
    Com/          signal layer — pack/unpack signals into PDUs
  EcuAbstraction/  ECU-specific wrapping of MCAL (pin map, clock, board cfg)
Mcal/              NXP RTD lives here (vendored separately, not committed — see Mcal/README.md)
Cfg/                S32 Config Tool output lands here (generated, not hand-edited)
```

Data flow (RX): `Mcal (FlexCAN ISR) -> Can -> CanIf -> PduR -> Com -> Rte -> App`
Data flow (TX): reverse.

## Status

Skeleton only — module folders + stub headers/APIs, no toolchain wired up yet,
NXP RTD not vendored. Existing `Fault.c` at repo root is pre-existing app-level
fault logic (not yet AUTOSAR-layered); migrate it into `App/` in a follow-up
once the SWC boundary is decided — not moved here to avoid touching code that
other work depends on.

## Next steps (toolchain)

1. Install S32 Design Studio for S32K1 (free, NXP site).
2. Download NXP RTD for S32K144, drop into `Mcal/` per `Mcal/README.md`.
3. Use S32 Config Tool to configure Dio/Port/Can/Adc/Wdg -> generates into `Cfg/`.
4. Wire `Bsw/Communication/Can` to call the generated `Can_*` MCAL APIs.
5. Build first milestone: CAN echo (RX frame -> TX frame, LED toggle).

## Phased plan (no-license path)

| Phase | Scope | Est. time |
|---|---|---|
| 1 | MCAL bring-up via S32 Config Tool (Dio/Port/Can) | 1–2 wk |
| 2 | Can/CanIf/PduR/Com stack, hand-written, basic CAN echo | 2–3 wk |
| 3 | Rte glue + App SWC (Fault module ported in) | 1–2 wk |
| 4 | EcuM/ComM basic states, cooperative scheduler | 1 wk |

~5–8 wk to a working layered POC on hardware. Not cert-ready — see
`Mcal/README.md` for the safety/cert gap.
