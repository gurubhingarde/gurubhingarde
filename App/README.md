# App/

Application SWCs go here — talk only to `Rte/`, never touch `Bsw/` or `Mcal/`
directly. Empty for now: root-level `Fault.c` (existing fault-management
logic) is the first candidate to port in as `App/Fault/`, once its signal
list is mapped to `Rte/Rte.h` ports and `Bsw/Communication/Com` signal table
(Phase 3 in top-level README.md). Not moved yet — avoid disturbing code other
work depends on until that mapping is decided.
