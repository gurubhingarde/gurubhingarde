# DCM Confirmation Review Checks (28 total)

## Confirmation Review (12)

### CR.01 Title
Document has clear dataset title. MUST.
- Title field populated
- Length 10-100 characters
- No placeholder text

### CR.02 Author/Approver
Author and approver documented. MUST.
- Author name present
- Approver name present
- Names are actual persons

### CR.03 Revision
Revision number recorded. MUST.
- Revision field populated
- Consistent format (v1.0, 1.0, A, date)
- Unique identifier

### CR.04 Variant
Calibration variant specified. SHOULD.
- Variant field populated (Euro5, EPA, etc.)
- Clear and descriptive

### CR.05 Build Date
Dataset build date recorded. SHOULD.
- Build date field populated
- Valid date format

### CR.06 Source A2L
Source A2L document documented. MUST.
- Source A2L Reference tab present
- A2L file name specified
- A2L version recorded

### CR.07 Document Control
Document Control tab present. SHOULD.
- Tab exists
- Revision history recorded
- Approver and date per revision

### CR.08 Dataset Identity
Dataset Identity tab present. SHOULD.
- Tab exists
- Variant, build date, equipment ID populated

### CR.09 Scalar Values
Scalar Values populated. SHOULD.
- Scalar Values tab exists
- Minimum 3 items if applicable

### CR.10 Curve Values
Curve Values present. SHOULD.
- Curve Values tab exists
- Entries if applicable

### CR.11 Map Values
Map Values present. SHOULD.
- Map Values tab exists
- Entries if applicable

### CR.12 Axis Points
Axis Point Values defined. MUST.
- Axis Point Values tab populated
- Minimum 1 axis defined

## Value Validation (10)

### VAL.01 Physical Range
All values within bounds. MUST.
- Every scalar within [min, max]
- Every curve value bounded
- No out-of-range values

### VAL.02 Curve Range
Curve values monotonic. MUST.
- Monotonically increasing or decreasing
- Curve values valid numbers

### VAL.03 Map Dimensions
Map dimensions match axes. MUST.
- Map array rows match Y-axis count
- Map array cols match X-axis count

### VAL.04 Axis Monotonic
Axis points strictly increasing. MUST.
- Every axis monotonically increasing
- No duplicate axis points

### VAL.05 Value Blocks
Value block members defined. SHOULD.
- All FESTWERTEBLOCK members present
- No orphaned references

### VAL.06 No NaN/Inf
No NaN or Inf values. MUST.
- All numeric values valid
- No NaN, Inf, or null in value columns

### VAL.07 Unit Consistency
Units consistent across dataset. MUST.
- Same parameter name uses same unit
- Units match source A2L
- No conflicting unit definitions

### VAL.08 Name Uniqueness
Parameter names unique. MUST.
- No duplicate names across tabs
- Identifiers unique

### VAL.09 Array Dimensions
Value counts match axis counts. MUST.
- Curve value count = axis point count
- Map dimensions correct
- Block member counts accurate

### VAL.10 Data Type
All numeric values valid. MUST.
- No text in numeric fields
- All values parseable as numbers

## Baseline & Traceability (6)

### BASE.01 Source A2L Version
Source A2L version specified. MUST.
- A2L file version recorded
- A2L date documented
- Version compatibility clear

### BASE.02 Baseline Link
Baseline reference documented. MUST.
- Baseline dataset identified
- Link traceable to approved baseline
- Previous version recorded if changed

### BASE.03 Change History
Change history recorded. SHOULD.
- Revision log present
- Change descriptions documented
- Why changed (if applicable)

### BASE.04 Approver
Approver documented. MUST.
- Approver name recorded
- Approval date present
- Authority clear

### BASE.05 Dataset Version
Dataset version unique. MUST.
- Version identifier unique
- No duplicate versions
- Version matches baseline record

### BASE.06 Equipment ID
Equipment/vehicle ID recorded. SHOULD.
- ECU or test bench identifier documented
- VIN or serial number if applicable
- Equipment identity traceable
