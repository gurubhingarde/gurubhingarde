# Composition SWC Naming and Conventions

## Naming Conventions

**Composition Names**: PascalCase suffix with "_Composition" or "_Comp"
- Example: PowerTrainControl_Comp, SuspensionManager_Composition

**SWC Instance Names**: Follow pattern {SWCType}_{Role}_{Index}
- Example: BrakeSWC_Master_01, ClimateControl_Slave_02

**Assembly Connector IDs**: AC_{SourceSWC}_{TargetSWC}_{Index}
- Example: AC_Brake_Actuator_01

**Delegation Connector IDs**: DC_{SWCInstance}_{Direction}_{Index}
- Example: DC_BrakeMaster_Out_01, DC_ClimateControl_In_02

**Boundary Port Names**: Compound {InterfaceType}_{Role}
- Example: BrakeCommand_Out, SensorData_In

## Port Compatibility Matrix

Provided (P) ports from SWC A must connect via Assembly to Required (R) ports on SWC B.

| Source | Target | Valid |
|--------|--------|-------|
| P-port | R-port | Yes   |
| P-port | P-port | No    |
| R-port | R-port | No    |
| R-port | P-port | No    |

## Multiplicity Rules

- 1:1 — Single producer to single consumer
- 1:N — Single producer to multiple consumers (e.g., broadcast)
- N:1 — Multiple producers to single consumer (requires arbitration)
- N:M — Complex patterns (use with caution; consider decomposition)
