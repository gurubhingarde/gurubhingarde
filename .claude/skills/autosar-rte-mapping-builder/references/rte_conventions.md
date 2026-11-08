# RTE Mapping Conventions

## Naming Standards
- Data mapping: <SWC>_<port>_to_<signal>
- Runnable-to-task: <SWC>_<runnable>_on_<task>
- Exclusive area: <SWC>_<area>_on_<resource>
- Task naming: Task_<period>ms_Prio<N>

## Timing Categories
- 10ms: Core control loops (100 Hz)
- 20ms: Secondary control (50 Hz)
- 100ms: Diagnostics, monitoring (10 Hz)
- Aperiodic: Event-triggered via interrupts

## Priority Assignment
- Real-time tasks: priority 1-10 (highest safety-critical)
- Normal tasks: priority 11-20
- Background: priority 21+ (lowest)
- Fixed priority: no dynamic priority changes

## Memory Regions
- Task stack: separate region per task
- Shared data: protected by exclusive areas
- DMA buffers: contiguous, cache-aligned
- Alignment: 4-byte minimum, 8-byte preferred

