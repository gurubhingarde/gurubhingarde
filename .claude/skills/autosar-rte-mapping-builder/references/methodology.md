# AUTOSAR RTE Mapping Methodology

## Overview
The RTE (Run-Time Environment) maps Software Component ports to BSW modules and OS tasks. RTE generation produces glue code for communication and scheduling.

## Key Mapping Concepts

### Data Mappings
- SWC sender-receiver ports map to Com signals
- Client-server ports map to Com service interfaces
- Mode-switch ports map to Com mode groups
- Signal attributes: type, length, byte order, conversion

### Runnable-to-Task Allocation
- Each runnable assigned to single OS task
- Runnables share task execution context
- Task period determines runnable period
- Priority-based scheduling via Os

### Exclusive Areas
- Critical sections protected by OS resources
- Mutex or spinlock implementation
- Prevent concurrent access to shared data
- Map to OS SpinLock or Resource

### Timing Constraints
- Task period (ms) from timing requirements
- Priority assigned per criticality
- Latency budgets: task dispatch + runnable WCET
- Stack allocation per task

## Validation Rules

1. Every SWC data port must map to Com signal
2. Every runnable must allocate to a task
3. No task priority inversion
4. Exclusive areas bind to OS resources
5. Memory regions allocated without overlap
6. Stack sizes sufficient for WCET + local vars

## References
- AUTOSAR R22-11 RTE specification
- SWC to RTE mapping requirements
- OS timing constraints document
