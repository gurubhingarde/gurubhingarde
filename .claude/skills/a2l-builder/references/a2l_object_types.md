# A2L Object Types per ASAM MCD-2 MC v1.7

## CHARACTERISTIC Types

### VALUE
Single scalar calibration parameter.
- Physical range: min/max bounds
- Data type: signed/unsigned integer or floating-point
- Conversion: LINEAR or other method for raw->physical transformation
- Memory: single address, typically 1-8 bytes

### CURVE
1D lookup table: physical_value = f(axis_points).
- X-axis: must reference valid AXIS_PTS
- Values: array of output values
- Memory: contiguous block for axis + values
- Interpolation: LINEAR assumed between points

### MAP
2D lookup table: physical_value = f(x_axis, y_axis).
- X-axis: reference to valid AXIS_PTS
- Y-axis: reference to valid AXIS_PTS
- Values: 2D array (y_rows x x_cols)
- Memory: address for x-axis, y-axis, and value matrix
- Interpolation: bilinear or nearest-neighbor

### AXIS_PTS
Axis point vector (row or column of a lookup table).
- Type: monotonically increasing values
- Fixed or dynamic (runtime-modifiable)
- Data type: same as lookup table values
- Memory: contiguous array

### VAL_BLK
Block of values (array or composite structure).
- Multiple elements of same or mixed types
- Used for parameter sets, calibration blocks
- Memory: contiguous region

## MEASUREMENT Types

### MEASUREMENT (Signal)
Observable ECU parameter readable during calibration.
- Read-only from ECU perspective
- Source: sensor, computed, diagnostic
- Update rate: periodic, event-driven, or on-demand
- Resolution: raw bits, converted to physical

## CONVERSION_METHOD Types

### LINEAR
ax + b transformation.
- Parameters: a (slope), b (offset)
- Use: simplest, most common
- Example: Engine speed = 0.25 * raw_value

### RAT_FUNC
Rational function: (a0 + a1*x + a2*x^2 + ...) / (b0 + b1*x + b2*x^2 + ...)
- Parameters: numerator and denominator coefficients
- Use: complex nonlinear mappings

### TAB_INTP
Table lookup with linear interpolation.
- Parameters: table address, interpolation method
- Use: empirical curves from measurement data

### TAB_NOINTP
Table lookup without interpolation (nearest neighbor).
- Parameters: table address
- Use: categorical mappings, discrete ranges

### FORMULA
Custom algebraic expression.
- Parameters: formula string with variable references
- Use: complex inter-parameter relationships

## AXIS Types

### COM_AXIS
Common standardized axis (predefined in calibration community).
- Example: Engine speed (0-6000 RPM)
- Predefined points and units
- Used across multiple applications

### STD_AXIS
Standard axis with explicit point list.
- Points defined inline or by reference
- Custom ranges and resolutions
- Most common in practice

### RES_AXIS
Result axis (computed from formula).
- Derived from other parameters
- Read-only
- Updated when source parameters change

## GROUP Hierarchy

### FUNCTION
Named calibration function (parameter or measurement).
- Identifier: must be unique
- Group: parent in hierarchy
- Description: purpose and range

### GROUP
Named collection of related functions.
- Parent: reference to containing group (or root)
- Members: list of child FUNCTION and GROUP references
- Tree structure: root groups contain sub-groups and functions

## Validation Constraints

1. **Reference Integrity**: Every axis, conversion, function, group reference must be defined.
2. **Type Consistency**: CURVE must have 1 axis, MAP must have 2 axes.
3. **Memory Alignment**: Address and size must respect ECU memory layout.
4. **Unit Consistency**: Conversion method must match characteristic units.
5. **No Overlap**: Memory ranges must not intersect.
6. **Monotonic Axes**: All AXIS_PTS must be strictly increasing.
7. **Name Uniqueness**: All identifiers must be unique within their scope.
