# DCM Authoring Methodology

## Overview

DCM (Data Conservation format) by ETAS is the de-facto interchange format for calibration parameter values across A2L tools. Distinct from AUTOSAR DCM module — this is the file format. DCM files contain just the values for characteristics defined in A2L, enabling parameter hand-off between development teams and suppliers.

## Key Concepts

### Dataset Identity
Every DCM dataset must be uniquely identified:
- **Variant**: Calibration variant (e.g., "Euro5", "EPA Tier2")
- **Build Date**: When dataset was created
- **Equipment/Vehicle ID**: Vehicle or test bench identifier
- **Baseline Reference**: Link to approved baseline dataset

### Value Types

#### Scalars (FUNKTIONEN/FESTWERT)
Single numeric values (fixed constants).
- Unit: Physical unit (RPM, C, A, etc.)
- Range: Physical min/max bounds
- Data type: typically float or int32

#### Curves (KENNLINIE)
1D lookup table: result = f(axis_points).
- X-axis: reference to axis points vector
- Values: array of output values (same length as axis)
- Interpolation: LINEAR between points
- Range: physical min/max for output

#### Maps (KENNFELD)
2D lookup table: result = f(x_axis, y_axis).
- X-axis, Y-axis: references to axis point vectors
- Values: 2D array (y_rows x x_cols)
- Interpolation: bilinear between points
- Range: physical min/max for output

#### Axis Points (STUETZSTELLENVERTEILUNG)
Vector of monotonically increasing axis values.
- Unit: Physical unit for axis dimension
- Monotonicity: strictly increasing
- Range: physical min/max
- Typically shared across multiple curves/maps

#### Value Blocks (FESTWERTEBLOCK)
Composite structures: grouped related scalars.
- Members: list of scalar parameter names
- Used for organized parameter sets
- All members same data type

### Baseline & Change Protocol

Every DCM dataset references a **baseline** — an approved, controlled version. Changes are tracked via:
- **Revision number**: Unique identifier
- **Change date**: When modified
- **Change description**: What was modified and why
- **Approver**: Authority sign-off

### Units & Physical Ranges

All values must be in physical (engineering) units, not raw ECU values:
- Physical value = raw_value * conversion_factor
- Physical range: [min_physical, max_physical]
- Units must match A2L characteristic units
- Out-of-range values rejected

## Workbook Structure

1. **Title** — Dataset name, variant, author, build date
2. **Document Control** — Revision history, baseline traceability, approvals
3. **Source A2L Reference** — A2L document version, file name, date
4. **Dataset Identity** — Variant, build date, equipment/vehicle ID
5. **Scalar Values** — FUNKTIONEN and FESTWERT entries
6. **Curve Values** — KENNLINIE data (name, axis ref, value array)
7. **Map Values** — KENNFELD data (2D lookup tables)
8. **Axis Point Values** — STUETZSTELLENVERTEILUNG (axis points)
9. **Value Block** — FESTWERTEBLOCK (composite structures)
10. **Comment Block** — KOMMENTAR, UNIT, TEXT metadata
11. **Validation Rules** — Range, monotonicity, consistency checks
12. **References** — ETAS DCM and ASAM standards

## Best Practices

### Naming
- Use same names as source A2L document
- Avoid special characters
- Keep names under 64 characters
- Group related values in blocks

### Consistency
- Verify all axis references exist in source A2L
- Check all values within physical ranges
- Ensure units match A2L definitions
- Maintain baseline traceability

### Validation
- Verify axis points are monotonic
- Check map dimensions match axes
- Validate all numeric values parseable
- Confirm dataset identity recorded

### Documentation
- Record source A2L file and version
- Document baseline and change history
- Include comments for non-obvious values
- Track approvals and authorization
