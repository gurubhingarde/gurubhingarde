# Adaptive App Checklist Methodology

Validation approach for AUTOSAR Adaptive Application specification workbooks.

## Check Categories

### Application Manifest (Mandatory)
- Manifest elements complete and consistent
- Service requirements identified
- Lifecycle hooks defined

### Service Manifest (Mandatory)
- All services in service manifest have definitions
- ara::com interface types correct
- Instance counts match deployment

### Machine Manifest (Mandatory)
- Machine manifest covers all deployed services
- Processor and network interface defined
- Sufficient for service deployment

### ara::com Interfaces (Mandatory)
- Service interfaces properly defined
- Communication types consistent
- Data types and queues specified

### ara::exec Lifecycle (Mandatory)
- Lifecycle states transition consistently
- Entry/exit actions defined
- No orphaned states

### SOME/IP Configuration (Mandatory)
- Service IDs unique system-wide
- Instance IDs unique per machine
- Port numbers non-overlapping

### Resource Constraints (Advisory)
- CPU and memory budget allocation
- Resource feasibility analysis
- Safety margin documentation

## References
- AUTOSAR Adaptive Platform R22-11 / R23-11 specification
- ara:: API reference
- SOME/IP configuration guide

