# Mcal/

NXP RTD (Real-Time Drivers) for S32K144 goes here — not vendored in this repo.
Download from NXP S32 site, drop the `Dio`, `Port`, `Can`, `Adc`, `Mcu`, `Wdg`
modules under this folder (structure follows RTD's own layout, e.g.
`Mcal/Can_43_FLEXCAN/`, `Mcal/Dio/`, ...).

Config: use S32 Config Tool (free), output goes to `../Cfg/`. Do not hand-edit
generated config headers.

## Cert gap

This is the free RTD tier — no safety manual, no FMEA, no ISO 26262 tool
qualification evidence. Fine for POC/QM. For ASIL-B/D cert, swap to NXP's
paid "Safety RTD" package (same API surface, adds safety case docs) and a
qualified config/RTE-gen tool (Vector DaVinci / EB tresos).
