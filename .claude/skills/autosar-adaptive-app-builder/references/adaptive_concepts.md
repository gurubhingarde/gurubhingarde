# AUTOSAR Adaptive Platform Concepts

## ara:: Libraries

### ara::com (Communication)
- Service-oriented middleware
- Interface-based communication
- Request-response, event, field patterns
- Automatic serialization/deserialization

### ara::exec (Execution Management)
- Application lifecycle management
- State machine: Init -> Run -> Shutdown
- Deterministic state transitions
- Entry/exit hooks per state

### ara::log (Logging)
- Structured logging framework
- Log levels: verbose, debug, info, warn, error, fatal
- Async writing to avoid blocking

### ara::core (Core Libraries)
- Result type: error handling without exceptions
- String utilities: no std::string overhead
- Span: non-owning container view

## SOME/IP Discovery

### Service Definition
- Service ID: 16-bit unique identifier
- Instance ID: 16-bit per machine instance
- Version: major.minor for compatibility

### Endpoint Discovery
- UDP port for SD (Service Discovery)
- TCP/UDP ports for service communication
- Multicast groups for SD messages

## Deployment Topology

### Processes
- One or more applications per process
- POSIX process: fork/exec model
- User/group permissions
- CPU affinity specification

### Network Interfaces
- Ethernet primary (local, gateway)
- VLAN tagging if required
- IP routing configuration
- Time synchronization (PTP)

