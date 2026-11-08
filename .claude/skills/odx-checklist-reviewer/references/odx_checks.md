# ODX Checklist — Check Definitions and Rationale

## Variant Definition Checks (V1-V8)

### V1: Base Variant ECU IDs Unique
**Obligation**: MUST | **Confidence**: High

Every base variant must have a unique, non-empty ECU ID. The ECU ID is the primary identifier for the ECU in the vehicle network.

**Check**: Iterate all base variants. Ensure all have distinct ECU IDs (no duplicates).

**Non-Compliance**: Two or more base variants share the same ECU ID → **Rating: NC**

---

### V2: Derived Variant Inheritance
**Obligation**: MUST | **Confidence**: High

Every derived variant must inherit from exactly one base variant. This ensures a clear inheritance hierarchy.

**Check**: For each derived variant, verify:
1. Has a parent_variant_id field (not empty)
2. Parent variant exists and is a base variant
3. No derived variant is a parent of another derived variant at the same level

**Non-Compliance**: Derived variant has no parent or parent does not exist → **Rating: NC**

---

### V3: No Circular Inheritance
**Obligation**: MUST | **Confidence**: High

Variant inheritance chains must form a forest (tree structure), not contain cycles.

**Check**: Perform a topological sort on the variant inheritance graph.
- If a cycle is detected, **Rating: NC**
- Otherwise, **Rating: FC**

**Example of violation**:
```
Variant A → Variant B → Variant C → Variant A (cycle!)
```

---

### V4: ODX Layer Hierarchy Complete
**Obligation**: SHOULD | **Confidence**: Medium

All four ODX layers (ODX-D, ODX-C, ODX-V, ODX-FD) should be represented in the workbook.

**Check**: Count unique layers in the "ODX Layer Hierarchy" sheet.
- 4 layers → **Rating: FC**
- 3 layers → **Rating: LC** (with note on missing layer)
- 2 or fewer → **Rating: PC** (significant gap)

---

### V5: Variant Naming Consistency
**Obligation**: SHOULD | **Confidence**: Medium

Variant IDs should follow a consistent naming convention (e.g., VAR_<market>_<config>).

**Check**: Examine all variant IDs for adherence to a pattern.
- Consistent naming → **Rating: FC**
- Mostly consistent with 1-2 exceptions → **Rating: LC**
- Mixed naming schemes → **Rating: PC**

---

### V6: ODX-D Services Coverage
**Obligation**: MUST | **Confidence**: Medium

All services defined in the Service Definitions sheet should be mapped to at least one variant (via inheritance).

**Check**: For each service, verify that at least one variant (base or derived) inherits it.
- All services mapped → **Rating: FC**
- 1-2 orphaned services → **Rating: LC**
- 3+ orphaned services → **Rating: PC**

---

### V7: ODX-C Communication Defined
**Obligation**: MUST | **Confidence**: High

Communication parameters must be specified for each physical channel.

**Check**: Verify that the "Communication Parameters (ODX-C)" sheet contains:
1. Bus speed (for CAN/LIN/Ethernet)
2. Timeout values
3. Flow control settings (if applicable)

**Non-Compliance**: Missing critical communication parameter → **Rating: NC**

---

### V8: ODX-V Vehicle Topology
**Obligation**: SHOULD | **Confidence**: Low

Vehicle topology and ECU mapping should be documented in the "Vehicle Information" sheet.

**Check**: Verify that at least a placeholder or basic topology is documented.
- Clear topology described → **Rating: FC**
- Partial topology → **Rating: LC**
- No topology documented → **Rating: PC**

---

## PDU and Service Checks (P1-P12)

### P1: PDU Library Complete
**Obligation**: MUST | **Confidence**: High

All PDUs referenced in service definitions must exist in the PDU Library sheet.

**Check**: Extract all PDU IDs from services (request_pdu_id, response_pdu_id). Verify each is defined in the PDU Library.
- All PDUs found → **Rating: FC**
- 1-2 missing PDUs → **Rating: LC**
- 3+ missing PDUs → **Rating: NC**

---

### P2: Service Request/Response Pairs
**Obligation**: MUST | **Confidence**: High

Every service must have both a request PDU and a response PDU.

**Check**: For each service, verify request_pdu_id and response_pdu_id are non-empty.
- All services have pairs → **Rating: FC**
- 1-2 incomplete services → **Rating: LC**
- 3+ incomplete services → **Rating: NC**

---

### P3: Signal Definitions Complete
**Obligation**: SHOULD | **Confidence**: Medium

All signals in PDUs should define:
1. Physical unit (e.g., RPM, km/h)
2. Conversion formula or raw-to-physical mapping
3. Valid range (min/max physical value)

**Check**: Examine signal definitions in PDU Library and/or referenced data object sheets.
- All signals have unit, conversion, range → **Rating: FC**
- 80% coverage → **Rating: LC**
- <80% coverage → **Rating: PC**

---

### P4: DTC Enumeration
**Obligation**: MUST | **Confidence**: Medium

All diagnostic trouble codes (DTCs) should be enumerated with at least severity level.

**Check**: Look for a DTC list (may be in a separate sheet or embedded in services).
- All DTCs listed with severity → **Rating: FC**
- DTCs listed but severity incomplete → **Rating: LC**
- No DTC list or very incomplete → **Rating: NC**

---

### P5: Data Object Ranges
**Obligation**: SHOULD | **Confidence**: Medium

Data objects should define min/max physical value ranges.

**Check**: Examine data object definitions.
- All have min/max ranges → **Rating: FC**
- 80% have ranges → **Rating: LC**
- <80% have ranges → **Rating: PC**

---

### P6: Parameter Validation Rules
**Obligation**: SHOULD | **Confidence**: Medium

Input parameters should define valid value ranges and constraints.

**Check**: Examine service parameters for constraint definitions (e.g., "DID must be 0x00-0xFF").
- All parameters have constraints → **Rating: FC**
- 80% have constraints → **Rating: LC**
- <80% have constraints → **Rating: PC**

---

### P7: Service Completeness
**Obligation**: MUST | **Confidence**: High

No orphaned services (every service must have a request/response and be reachable from at least one variant).

**Check**: Verify P2 (request/response pairs) + V6 (variant mapping).
- All services complete and mapped → **Rating: FC**
- Otherwise → depends on severity

---

### P8: Negative Response Coverage
**Obligation**: SHOULD | **Confidence**: Medium

All negative responses should include an error code and brief description.

**Check**: For each service, examine negative response definitions.
- All negative responses have codes + descriptions → **Rating: FC**
- 80% coverage → **Rating: LC**
- <80% coverage → **Rating: PC**

---

### P9: Multiplexing Consistency
**Obligation**: MUST | **Confidence**: High

Multiplexing rules in PDUs should be internally consistent (e.g., multiplex selector values must be unique).

**Check**: For each multiplexed PDU, verify multiplex selector values don't overlap.
- All PDUs consistent → **Rating: FC**
- 1 PDU with issues → **Rating: LC**
- 2+ PDUs with issues → **Rating: NC**

---

### P10: Signal Bit Mapping
**Obligation**: MUST | **Confidence**: High

No signal should overlap in bit position within the same PDU variant.

**Check**: For each PDU, compute bit ranges for all signals. Check for overlaps.
- No overlaps → **Rating: FC**
- 1 overlap detected → **Rating: LC**
- 2+ overlaps → **Rating: NC**

---

### P11: Safety-Relevant Marking
**Obligation**: SHOULD | **Confidence**: Low

Services affecting ASIL functions should be explicitly marked as safety-relevant.

**Check**: Review service definitions for a "safety_relevant" or similar field.
- All ASIL-related services marked → **Rating: FC**
- Partial marking → **Rating: LC**
- No marking → **Rating: PC**

---

### P12: Service Versioning
**Obligation**: MAY | **Confidence**: Low

Legacy or deprecated services should be explicitly marked (optional).

**Check**: Look for version info or deprecation markers.
- Present and clear → **Rating: FC**
- Not present (okay, as this is optional) → **Rating: NA**

---

## Communication and Flash Checks (C1-C10)

### C1: Bus Speed Definition
**Obligation**: MUST | **Confidence**: High

Physical bus speed must be defined for the transport protocol (CAN/LIN/Ethernet).

**Check**: Verify the Communication Parameters sheet specifies bus speed.
- Bus speed defined and valid → **Rating: FC**
- Bus speed missing or invalid → **Rating: NC**

---

### C2: Timing Parameters
**Obligation**: MUST | **Confidence**: High

P2 timeout, inter-frame delay, and response timing must be specified.

**Check**: Verify Communication Parameters sheet includes:
1. P2 timeout (UDS standard: 50-1000 ms typical)
2. Inter-frame delay (minimum gap between requests)
3. Response delay (maximum latency for response)

**Non-Compliance**: Any missing parameter → **Rating: NC**

---

### C3: Flow Control Mechanism
**Obligation**: SHOULD | **Confidence**: Medium

Flow control (CTS, WAIT) should be defined if applicable (especially for CAN with large data transfers).

**Check**: Verify flow control is specified where needed.
- Flow control defined and reasonable → **Rating: FC**
- Not applicable (short messages only) → **Rating: NA**
- Missing where expected → **Rating: PC**

---

### C4: Protocol-Specific Headers
**Obligation**: MUST | **Confidence**: High

Protocol-specific addressing must be defined:
- CAN: Frame IDs (standard or extended), data length code (DLC)
- LIN: Frame byte positions, LIN checksum variant
- Ethernet: IP addresses, ports, DoIP routing

**Check**: Verify at least the primary protocol has correct headers.
- Protocol headers defined correctly → **Rating: FC**
- Missing or incorrect → **Rating: NC**

---

### C5: Memory Segment Definition
**Obligation**: MUST | **Confidence**: High

Flash memory must be partitioned into at least Boot, Application, and Calibration segments.

**Check**: Verify Flash Data sheet defines memory layout.
- All segments defined with addresses → **Rating: FC**
- Some segments missing → **Rating: LC**
- No memory layout → **Rating: NC**

---

### C6: Programming Algorithm
**Obligation**: SHOULD | **Confidence**: Medium

Flash programming sequence (erase, write, verify) and procedures should be documented.

**Check**: Verify Flash Data sheet describes:
1. Erase procedure (sector erase vs. bulk erase)
2. Write procedure (block size, streaming)
3. Verify procedure (CRC check, data compare)

**Assessment**:
- All procedures described → **Rating: FC**
- Partial description → **Rating: LC**
- No description → **Rating: PC**

---

### C7: CRC Algorithm Specification
**Obligation**: MUST | **Confidence**: High

CRC/checksum algorithm, polynomial, and protected regions must be specified.

**Check**: Verify Flash Data sheet includes:
1. Algorithm name (CRC-32, CRC-16, SHA-256)
2. Polynomial (if CRC-based)
3. Protected regions (Boot + App, Calib, etc.)

**Non-Compliance**: Algorithm missing or polynomial undefined → **Rating: NC**

---

### C8: Security Unlock Procedure
**Obligation**: SHOULD | **Confidence**: Low

Authentication and security access timing should be documented.

**Check**: Verify Flash Data sheet describes:
1. Unlock method (PIN, certificate, challenge-response)
2. Timing (immediate, after delay, after power cycle)
3. Retry limits (brute-force protection)

**Assessment**:
- Full security procedure described → **Rating: FC**
- Partial description → **Rating: LC**
- No security procedure → **Rating: PC** (or NA if vehicle doesn't need security)

---

### C9: Non-Volatile Data Layout
**Obligation**: MUST | **Confidence**: High

Persistent data regions (NV data, calibration) must be mapped to specific memory addresses.

**Check**: Verify Flash Data sheet maps:
1. Calibration data address range
2. NV user data address range (if applicable)
3. Backup regions (if applicable)

**Non-Compliance**: Critical NV region unmapped → **Rating: NC**

---

### C10: Rollback / Recovery Strategy
**Obligation**: MAY | **Confidence**: Low

Mechanism for rollback on failed flash or recovery should be documented (optional but recommended for production ECUs).

**Check**: Verify Flash Data sheet describes recovery mechanism.
- Rollback procedure defined → **Rating: FC**
- Not applicable or intentionally not supported → **Rating: NA**
- Missing but would be helpful → **Rating: LC**

---

## End-to-End Compliance Checklist

For an ODX to be audit-ready, at minimum:
- [ ] V1 (unique base ECU IDs): FC
- [ ] V2 (derived variant inheritance): FC
- [ ] V3 (no circular inheritance): FC
- [ ] V6 (ODX-D coverage): FC or LC
- [ ] V7 (ODX-C communication): FC
- [ ] P1 (PDU library complete): FC
- [ ] P2 (service request/response): FC
- [ ] P4 (DTC enumeration): FC or LC
- [ ] C1 (bus speed): FC
- [ ] C2 (timing parameters): FC
- [ ] C5 (memory segments): FC
- [ ] C7 (CRC algorithm): FC
- [ ] C9 (NV data layout): FC
