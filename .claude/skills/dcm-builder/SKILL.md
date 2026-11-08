---
name: dcm-builder
description: Generate an audit-ready DCM (ETAS Data Conservation) calibration values workbook capturing characteristic values for A2L-defined parameters including scalars, curves, maps, axis points, and value blocks for cross-tool calibration data exchange used by INCA, CANape, ATI Vision, and other ASAM-compliant calibration tools. Use this skill when the user mentions dcm builder.
---

# dcm-builder

Generate an audit-ready DCM (ETAS Data Conservation) calibration values workbook capturing characteristic values for A2L-defined parameters including scalars, curves, maps, axis points, and value blocks for cross-tool calibration data exchange used by INCA, CANape, ATI Vision, and other ASAM-compliant calibration tools.

Use this skill whenever the user mentions DCM file, ETAS DCM, calibration values, parameter dataset, .dcm interchange, or calibration data export.

## Output

Generates 12-tab Excel workbook with:

- **Title** — Document control header, dataset identity, source A2L reference
- **Document Control** — Change log, baseline traceability, approvals
- **Source A2L Reference** — Link to originating A2L document, version compatibility
- **Dataset Identity** — Calibration variant, build date, equipment/vehicle identification
- **Scalar Values** — FUNKTIONEN (functions) and FESTWERT (fixed values) entries
- **Curve Values** — KENNLINIE (curve) data with X-axis interpolation
- **Map Values** — KENNFELD (map) 2D lookup table data
- **Axis Point Values** — STUETZSTELLENVERTEILUNG (axis points) for lookup dimensions
- **Value Block** — FESTWERTEBLOCK (composite blocks) for grouped parameters
- **Comment Block** — KOMMENTAR, UNIT, TEXT metadata
- **Validation Rules** — Physical range checks, monotonicity, consistency
- **References** — ETAS DCM format and ASAM cross-references

## Usage

```bash
python generate_dcm.py <input.json> <output.xlsx>
```

Input JSON contains dataset metadata, source A2L reference, scalar values, curve/map data, axis points, and composite blocks.

## References

See `references/methodology.md` for design guidance and `references/dcm_format.md` for ETAS DCM format specifications.
