# BSW Config Checklist Methodology

Validation approach for AUTOSAR Classic Basic Software configuration workbooks.

## Check Categories

### MCAL Configuration (Mandatory)
- Target microcontroller fully configured
- All MCAL interfaces match target capabilities
- Port definitions for GPIO, CAN, LIN, SPI, UART

### Module Completeness (Mandatory)
- ECU Abstraction layer modules present
- Service Layer modules cover communication needs
- Complex Drivers defined for special functionality

### Scheduling and Timing (Mandatory)
- OS tasks allocated with period and priority
- No priority inversions
- Task periods align with timing requirements

### Memory and Allocation (Mandatory)
- RAM/ROM regions allocated per module
- NvM blocks aligned with application storage
- Stack sizes sufficient for WCET

### Parameter Consistency (Mandatory)
- No duplicate parameter names within module
- Parameter values within valid ranges
- Post-build variants properly identified

### Dependencies (Advisory)
- Inter-module dependencies documented
- Dependent modules properly ordered
- No circular dependencies

