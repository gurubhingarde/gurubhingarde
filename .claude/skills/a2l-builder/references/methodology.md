# A2L Authoring Methodology

## Overview

A2L (ASAM MCD-2 MC) is the standard description format for ECU calibration objects used by major calibration tools: INCA, CANape, ATI Vision, and others. This workbook guides creation of audit-ready A2L definitions per ASAM MCD-2 MC v1.7.

## Key Concepts

### Characteristics
Calibration parameters (ECU tuning values) defined by type:
- **VALUE**: Single scalar parameter
- **CURVE**: 1D lookup table (function of one axis)
- **MAP**: 2D lookup table (function of two axes)
- **AXIS_PTS**: Axis point vector (can be static or dynamic)
- **VAL_BLK**: Block of values (composite structure)

### Measurements
Observable signals from the ECU:
- Real-time readable parameters
- Diagnostic data
- Sensor inputs
- Calculated values

### Conversion Methods
Transformations between physical units and ECU raw values:
- **LINEAR**: ax + b
- **RAT_FUNC**: Rational function (polynomial ratio)
- **TAB_INTP**: Table with interpolation
- **TAB_NOINTP**: Table without interpolation
- **FORMULA**: Custom algebraic expression

### Axes
Point vectors defining lookup table rows/columns:
- **COM_AXIS**: Common standardized axis
- **RES_AXIS**: Result axis (derived from computation)
- **STD_AXIS**: Standard axis (explicit point list)

### Memory Mapping
Address assignment for each characteristic or structure:
- Segment assignment (RAM, FLASH, EEPROM)
- Address range validation
- Overlap detection
- Memory layout consistency

## Workbook Structure

1. **Title** — Item identity, revision, author, approver
2. **Document Control** — Change log and approval chain
3. **ECU Identity** — Hardware/software version, memory footprint
4. **Characteristic Catalog** — All VALUE, CURVE, MAP, AXIS_PTS, VAL_BLK definitions
5. **Measurement Catalog** — All measurement signals
6. **Conversion Methods** — LINEAR, RAT_FUNC, TAB_INTP, TAB_NOINTP, FORMULA definitions
7. **Axis Descriptions** — All axis point vectors
8. **Record Layouts** — STRUCTURE definitions for composite objects
9. **Function Hierarchy** — GROUP and FUNCTION organization
10. **Group Hierarchy** — Logical grouping tree
11. **Memory Address Mapping** — Segment layout and address assignment
12. **Validation Rules** — Consistency checks and requirements
13. **References** — Bibliography and standard cross-references

## Best Practices

### Naming
- Use clear, descriptive names following ECU conventions
- Include units and ranges in documentation
- Avoid special characters in A2L identifiers
- Keep names under 64 characters

### Consistency
- Every characteristic must have a valid conversion method
- Every CURVE/MAP must reference valid axes
- Axes must be monotonically increasing
- All references must be defined before use

### Validation
- Check memory layout for overlaps
- Verify unit consistency across related parameters
- Validate conversion method parameters
- Confirm all references are resolvable

### Documentation
- Record rationale for each calibration parameter
- Document assumptions about ECU behavior
- Track baseline values and change history
- Include cross-references to related documents
