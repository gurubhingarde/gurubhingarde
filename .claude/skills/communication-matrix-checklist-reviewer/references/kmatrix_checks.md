# K-Matrix Validation Checks Reference

## Critical Checks (Must Pass)

### Message Integrity
- All messages have exactly one sender ECU
- All messages have at least one receiver ECU
- Message IDs are unique per bus
- Message names are globally unique
- Message lengths comply with bus type (8 bytes CAN, 64 bytes CAN FD)

### Signal Ownership
- Each signal owned by exactly one ECU
- Signal names unique across all buses
- All signals reference existing messages
- Signals fit within message boundaries (bit position + length <= message length * 8)

### ECU and Routing
- All message senders are members of the message bus
- All receivers exist in ECU inventory
- Sender-receiver matrix matches message catalog
- No ECU is isolated (member of at least one bus)

## Warning Checks (Should Pass)

### Formatting and Standards
- Message IDs follow 0xHHH format
- ECU IDs follow ECU[NNN][Letter] convention
- Signal types are recognized (uint8, uint16, int16, int32, uint32, float, bool)
- Bus types are standard (CAN 2.0B, CAN FD, LIN, FlexRay, Ethernet)
- Baudrates are standard (500 kbps, 1 Mbps, 5 Mbps, 19.2 kbps, 33.3 kbps)

### Performance and Capacity
- Message cycle times reasonable (1-10000 ms)
- Bus utilization within safe margins (typically 75-80%)
- Signal lengths between 1-64 bits
- Gateway routing rules defined for cross-bus signals
- No circular message routes

### Architecture
- All defined buses utilized by at least one message
- ECU message load reasonably distributed (no single ECU handles >2x average)
- Timing deadlines achievable
- Cross-bus signals have explicit routing rules

## Check Severity Levels

### FAIL (Red)
Issues preventing message transmission or causing routing conflicts. Must be fixed before deployment.

### WARNING (Yellow)
Non-standard patterns requiring review. May need update to conform to conventions or performance targets.

### PASS (Green)
Check satisfied. No action required.

## Common Issues and Fixes

### Missing Receivers
**Issue**: Message defined but no receivers assigned
**Fix**: Add receiver ECUs in Sender-Receiver Matrix sheet

### Signal Out of Bounds
**Issue**: Signal start bit + length exceeds message capacity
**Fix**: Reduce signal length or split across multiple messages

### Sender Not on Bus
**Issue**: Message sender not member of message bus
**Fix**: Add bus membership in ECU Inventory or reassign message to sender's bus

### Duplicate Signal Names
**Issue**: Same signal name used in multiple messages
**Fix**: Prefix signals with system abbreviation (e.g., PT_EngineSpeed)

### Missing Gateway Rules
**Issue**: Message crosses buses without routing rule
**Fix**: Add entry in Gateway Routing sheet

### Bus Over-Capacity
**Issue**: Total message load exceeds bus bandwidth
**Fix**: Increase cycle times, reduce message sizes, or split to additional bus
