# Composition SWC Review Methodology

## Scope

Composition SWC reviews focus on architectural coherence, hierarchical validity, and connector semantics per AUTOSAR R22-11.

## Check Categories

**Structural**: Tab presence, metadata completeness, document control.

**Instances**: SWC instance definition, multiplicity, uniqueness, orphan detection.

**Connectors**: Assembly validity (P-port to R-port), delegation completeness, port mapping.

**Boundary**: Port aggregation, port coverage (all boundary ports delegated), interface consistency.

**Naming**: Convention adherence, identifier uniqueness, traceability.

## Validation Rules

1. Every SWC instance must be wired.
2. Assembly connectors must link compatible port types.
3. All boundary ports must have delegation backing.
4. No circular composition references (non-recursive hierarchies only).

## Remediation Priorities

- MUST failures (fails, orphaned instances, broken references) block approval.
- SHOULD failures (naming, documentation) recommend conditional approval with corrective actions.
