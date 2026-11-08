# RTE Mapping Checks

## C001: SWC Port to Com Signal Mapping
Requirement: All SWC sender-receiver ports must map to Com signals.
Check: Verify Data Mappings tab covers all ports.
Rating: FC if complete, PC if partial, NO if missing.

## C002: Runnable to Task Allocation
Requirement: Every runnable must be allocated to an OS task.
Check: Scan Runnable-to-Task tab for unallocated runnables.
Rating: FC if all allocated, NO if missing.

## C003: Task Period Consistency
Requirement: Task periods must align with timing constraints.
Check: Compare Schedulable Period against timing requirements document.
Rating: FC if consistent, PC if questionable, NO if conflicts.

## C004: Exclusive Area to OS Resource
Requirement: All exclusive areas must bind to OS resources.
Check: Verify Exclusive Areas tab has OS Resource populated.
Rating: FC if all mapped, PC if partial, NO if missing.

## C005: Priority Inversion Detection
Requirement: No priority inversion between dependent tasks.
Check: Analyze task dependencies and priority order.
Rating: FC if no inversion, PC if marginal, NO if detected.

## C006: Mode-Switch Mapping
Requirement: Mode switches must be properly mapped.
Check: Verify Mode-Switch Mapping tab completeness.
Rating: FC if complete, LC if partial, NA if none required.

## C007: Trigger Latency Documentation
Requirement: Trigger latencies should be within budget.
Check: Review latency columns in Trigger Source Mappings.
Rating: LC if documented, NA if not applicable.

## C008: Stack Size Allocation
Requirement: Stack sizes must be allocated for all tasks.
Check: Verify Stack Sizing tab populated.
Rating: FC if allocated, LC if estimated, NO if missing.

