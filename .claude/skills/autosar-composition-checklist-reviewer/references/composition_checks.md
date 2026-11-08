# Composition SWC Checklist Checks Reference

## Check Summary (28 checks)

### Structural (C01-C03)
- C01: All 12 tabs present
- C02: Document ID populated and unique
- C03: Composition name defined and non-empty

### Instances (C04-C05)
- C04: All SWC instances documented
- C05: No orphaned instances (each wired to assembly or delegation)

### Assembly Connectors (C06-C09)
- C06: All intra-composition connections documented
- C07: Port-to-port compatibility (P-port to R-port, matching interfaces)
- C08: Source SWC and port references valid
- C09: Target SWC and port references valid

### Delegation Connectors (C10-C13)
- C10: All SWC-to-boundary delegations documented
- C11: SWC instance and port references valid
- C12: Boundary port targets are defined
- C13: Delegation direction matches boundary port type

### Boundary Ports (C14-C16)
- C14: All boundary ports listed
- C15: All boundary ports covered by delegations
- C16: No unreferenced orphaned boundary ports

### Naming & Traceability (C17-C20)
- C17: SWC instance naming follows convention
- C18: Connector IDs follow convention
- C19: Boundary port names unique
- C20: SWC instance names unique

### Interface & Compatibility (C21-C24)
- C21: Interface types consistent across connectors
- C22: Hierarchy tree populated
- C23: Port Compatibility Rules documented
- C24: Validation Rules present

### Documentation & Coherence (C25-C28)
- C25: Standards and references cited
- C26: Multiplicity specifications present
- C27: Document control tracked
- C28: All elements traceable to requirements
