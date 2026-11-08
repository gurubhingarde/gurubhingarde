# SysML Requirement Relationships

## Satisfy

Definition: Indicates that a system/component element satisfies a requirement.

Usage: Link a requirement to the system function or component that fulfills it.

Example: Requirement "System shall detect obstacles within 50m" satisfied by "Perception Subsystem".

## Derive

Definition: Indicates that a lower-level requirement is derived from a higher-level requirement.

Usage: Decompose system requirements into sub-system and component requirements.

Example: System requirement "detect obstacles" derives component requirement "process camera feed".

## Verify

Definition: Indicates the method used to verify requirement satisfaction.

Usage: Test, analysis, inspection, or demonstration that confirms requirement met.

Example: Requirement verified by "integration test suite", "HARA analysis", "design review".

## Refine

Definition: Clarifies, constrains, or elaborates a parent requirement.

Usage: Add detail to a general requirement without changing its fundamental meaning.

Example: Refines "low latency" to "latency < 100ms per the SOTIF analysis".

## Trace

Definition: Generic relationship indicating a link (often transitive) from requirement through design to implementation.

Used in coverage analysis to identify gaps.
