# Os/

No free OSEK-compliant AUTOSAR OS from NXP for the no-license path. For POC,
this is a cooperative scheduler (SysTick + task table), not an OSEK OS —
non-compliant, functionally equivalent for a single-core prototype. Real
classic AUTOSAR OS needs a vendor RTOS (Vector/EB) or FreeRTOS bridged through
an OSEK-shim (still non-cert, but closer) if isolation/priority preemption is
needed later.
