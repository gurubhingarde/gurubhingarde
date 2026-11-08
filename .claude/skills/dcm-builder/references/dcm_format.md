# ETAS DCM Format Specification

## File Format Overview

DCM (Data Conservation) is a text-based (or binary) format for storing calibration parameter values. It pairs with A2L (ASAM MCD-2 MC) calibration descriptions.

## DCM Objects

### FUNKTIONEN (Functions)
Named scalar value entries.
- Identifier: unique name
- Value: numeric (integer or float)
- Physical unit: engineering unit string
- Range bounds: min and max physical values
- Optional comment

Example:
```
FUNKTIONEN = {
  NAME = "Idle_RPM"
  VALUE = 800
  UNIT = "rpm"
  PHYS_MIN = 500
  PHYS_MAX = 1500
  COMMENT = "Target idle engine speed"
}
```

### FESTWERT (Fixed Values)
Alias for FUNKTIONEN (scalar constant).

### KENNLINIE (Curve)
1D lookup table with axis interpolation.
- Identifier: unique name
- Axis reference: link to STUETZSTELLENVERTEILUNG
- Values: array of output values
- Physical range: min/max for output
- Interpolation method: LINEAR assumed

Example:
```
KENNLINIE = {
  NAME = "Fuel_Pressure_Map"
  AXIS_REF = "Engine_Speed_Points"
  VALUES = [45.0, 50.0, 55.0, 60.0, ...]
  PHYS_MIN = 40.0
  PHYS_MAX = 70.0
}
```

### KENNFELD (Map)
2D lookup table with two-axis interpolation.
- Identifier: unique name
- X-axis reference: link to STUETZSTELLENVERTEILUNG
- Y-axis reference: link to STUETZSTELLENVERTEILUNG
- Values: 2D array [y_rows][x_cols]
- Physical range: min/max for output
- Interpolation method: bilinear assumed

Example:
```
KENNFELD = {
  NAME = "Ignition_Timing_Map"
  X_AXIS_REF = "Engine_Speed_Points"
  Y_AXIS_REF = "Load_Points"
  VALUES = [
    [5.0, 8.0, 10.0, ...],
    [6.0, 9.0, 11.0, ...],
    ...
  ]
  PHYS_MIN = 0.0
  PHYS_MAX = 25.0
}
```

### STUETZSTELLENVERTEILUNG (Axis Points)
Monotonically increasing vector of axis values.
- Identifier: unique name
- Points: array of increasing values
- Physical unit: engineering unit
- Range bounds: min and max values

Example:
```
STUETZSTELLENVERTEILUNG = {
  NAME = "Engine_Speed_Points"
  POINTS = [0, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000]
  UNIT = "rpm"
  PHYS_MIN = 0
  PHYS_MAX = 6000
}
```

### FESTWERTEBLOCK (Value Block)
Composite structure: group of related scalars.
- Block name: identifier
- Members: list of FUNKTIONEN references
- Used for organized parameter sets

Example:
```
FESTWERTEBLOCK = {
  NAME = "Idle_Control_Block"
  MEMBERS = ["Idle_RPM", "Idle_Timeout", "Min_Idle_TPS"]
}
```

### KOMMENTAR (Comment)
Metadata commentary for parameters.
- Parameter reference: which object this comments
- Text: documentation string

### UNIT (Unit Metadata)
Physical unit specification for a parameter.
- Parameter reference
- Unit string (e.g., "rpm", "C", "A", "mA", "bar")

### TEXT (Text Metadata)
Human-readable description.
- Parameter reference
- Description text

## Baseline & Version Control

Every DCM dataset includes:
- **DATASET_VERSION**: Version identifier
- **BASELINE_REFERENCE**: Link to approved baseline
- **MODIFICATION_DATE**: When last modified
- **MODIFICATION_AUTHOR**: Who made changes
- **MODIFICATION_REASON**: Why changed

## Data Type Mapping

| A2L Type | DCM Representation | Physical Unit |
|----------|-------------------|---------------|
| VALUE (signed 8-bit) | int8 | physical unit |
| VALUE (signed 16-bit) | int16 | physical unit |
| VALUE (signed 32-bit) | int32 | physical unit |
| VALUE (float) | float | physical unit |
| CURVE | array of values | physical unit |
| MAP | 2D array | physical unit |
| AXIS_PTS | array (monotonic) | physical unit |

## Physical Value Transformation

DCM values are ALWAYS in physical (engineering) units. Conversion from ECU raw values:
```
physical_value = (raw_value - offset) * scale
```

Example: Engine speed calibration
- Raw ECU values: 0-16000 (resolution 0.25 RPM/count)
- Physical range: 0-4000 RPM
- DCM entry: 1500 (RPM, physical units)

## Validation Constraints

1. **Range Checks**: Every value within [PHYS_MIN, PHYS_MAX]
2. **Axis Monotonicity**: STUETZSTELLENVERTEILUNG strictly increasing
3. **Dimension Matching**: KENNFELD array rows match Y-axis size, columns match X-axis size
4. **Unit Consistency**: All FUNKTIONEN with same parameter name share identical units
5. **Reference Integrity**: All axis references must be defined
6. **No NaN/Inf**: Numeric values must be valid numbers
7. **Baseline Traceability**: Every dataset linked to approved baseline

## Example DCM Dataset

```
DATASET_INFO = {
  NAME = "Engine_Calibration_v2.3"
  VARIANT = "Euro5"
  BUILD_DATE = "2024-05-01"
  BASELINE = "Engine_Calibration_v2.2_approved"
  AUTHOR = "Calibration_Team"
}

STUETZSTELLENVERTEILUNG = {
  NAME = "RPM_Points"
  POINTS = [0, 500, 1000, 1500, 2000, 3000, 4000, 6000]
  UNIT = "rpm"
  PHYS_MIN = 0
  PHYS_MAX = 6000
}

FUNKTIONEN = {
  NAME = "Target_Idle_RPM"
  VALUE = 800
  UNIT = "rpm"
  PHYS_MIN = 500
  PHYS_MAX = 1200
  COMMENT = "Idle speed setpoint"
}

KENNLINIE = {
  NAME = "Fuel_Pressure_vs_Speed"
  AXIS_REF = "RPM_Points"
  VALUES = [40, 45, 50, 55, 60, 65, 70, 75]
  UNIT = "bar"
  PHYS_MIN = 30
  PHYS_MAX = 80
}
```
