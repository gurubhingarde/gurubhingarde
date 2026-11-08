# K-Matrix Methodology

## Overview

The K-Matrix (communication matrix) is the authoritative specification of all bus traffic across a vehicle's communication networks. It serves as the single source of truth for cross-ECU signal coordination, message ownership, and gateway routing.

## Key Concepts

### Buses
- Classical CAN 2.0B (ISO 11898-1)
- CAN FD (ISO 11898-2)
- LIN (ISO 17987)
- FlexRay (ISO 17458)
- Automotive Ethernet (IEEE 802.3)

### ECUs
Electronic Control Units (ECUs) represent distinct compute nodes:
- Each ECU has defined bus memberships (primary and secondary)
- ECUs act as message senders, receivers, or gateways
- Gateway ECUs route messages across bus boundaries

### Messages
Messages encapsulate signals:
- Each message has a unique CAN ID or LIN frame ID
- Every message must have at least one sender and one receiver
- Message cycle times define communication frequency
- Message length is constrained by bus type (8 bytes CAN, 64 bytes CAN FD, 8 bytes LIN)

### Signals
Signals represent individual data items within messages:
- Each signal has a unique owner ECU
- Signals are located at specific bit positions within messages
- Signal definitions include type, length, endianness, and physical properties

### Gateway Routing
Gateways translate and forward messages across bus boundaries:
- Routing rules specify which messages cross which buses
- Gateways may filter, combine, or split signals
- Cross-bus timing must respect deadline constraints

## Structure

The K-Matrix workbook contains 12 tabs:

1. **Title**: Document metadata
2. **Document Control**: Version, status, author tracking
3. **Vehicle Network Topology**: Bus definitions and architecture
4. **ECU Inventory**: ECU list with bus memberships
5. **Message Catalog**: Complete message inventory
6. **Signal Catalog**: Signal ownership and locations
7. **Sender-Receiver Matrix**: Message distribution paths
8. **Bus Allocation**: Bandwidth utilization
9. **Gateway Routing Requirements**: Cross-bus rules
10. **Signal Timing Budget**: Cycle times and deadlines
11. **Validation Rules**: Audit checklist
12. **References**: Standards and documents

## Validation

All K-Matrices must satisfy:
- Every message has exactly one sender
- Every message has at least one receiver
- Every signal is owned by exactly one ECU
- Signal names are unique across all buses
- All gateway rules are defined and complete
- Bus utilization is within safe margins (typically 75-80%)
- Timing deadlines are achievable given network latencies
