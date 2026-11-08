# BSW Configuration Checks

## C001: MCAL Module Configuration
Requirement: All MCAL modules must be configured for the target microcontroller.
Check: Verify each MCAL module (Port, Dio, Adc, etc.) has target configuration present.
Rating: FC (fully compliant) if all modules configured, PC if partial, NO if missing.

## C002: ECU Abstraction Completeness
Requirement: ECU Abstraction layer must provide core services.
Check: Verify EcuM, FeeM, or MemIf modules present per architecture.
Rating: FC if present, NA if not required.

## C003: Service Layer Critical Modules
Requirement: Critical Service Layer modules must be identified.
Check: Verify Com, PduR, NvM marked as critical where needed.
Rating: FC if marked, LC if unmarked, NO if missing.

## C004: OS Task Scheduling
Requirement: All OS tasks must have period and priority.
Check: Verify Task Period (ms), Priority fields populated.
Rating: FC if all tasks have schedules, NO if missing.

## C005: Memory Allocation
Requirement: Memory regions must be allocated.
Check: Verify Memory Map tab with RAM/ROM regions.
Rating: FC if allocated, NA if not applicable.

## C006: NvM Block Alignment
Requirement: NvM blocks must align with module parameters.
Check: Cross-reference NvM parameters with storage requirements.
Rating: FC if aligned, PC if partial, NO if misaligned.

## C007: Parameter Conflict Detection
Requirement: No duplicate parameter names within a module.
Check: Scan Module Parameters tab for duplicate names per module.
Rating: FC if no conflicts, NO if duplicates found.

## C008: Inter-Module Dependencies
Requirement: Module dependencies should be documented.
Check: Review Inter-Module Dependencies tab.
Rating: LC if documented, NA if none exist.

## C009: Post-Build Variants
Requirement: Post-build variant parameters identified.
Check: Count Post-Build Variant column in Module Parameters.
Rating: LC if variants defined, NA if not needed.

