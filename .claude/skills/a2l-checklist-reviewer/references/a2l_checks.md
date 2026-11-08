# A2L Confirmation Review Checks (30 total)

## Confirmation Review Checks (14)

### CR.01 Document Structure
**Requirement:** Document structured into logical tabs
**Obligation:** SHOULD (3-4 points if missing)
**Acceptance Criteria:**
- Minimum 10 tabs present
- Tabs cover: Title, Document Control, ECU Identity, Catalogs, Mappings, Validation

### CR.02 Title & Metadata — Title
**Requirement:** Document has clear title
**Obligation:** MUST
**Acceptance Criteria:**
- Title field populated on Title sheet
- Title length 10-100 characters
- No placeholder text like "Template" or "Unnamed"

### CR.03 Title & Metadata — Author/Approver
**Requirement:** Author and approver documented
**Obligation:** MUST
**Acceptance Criteria:**
- Author name present
- Approver name present
- Names are actual persons (not "TBD")

### CR.04 Title & Metadata — Revision
**Requirement:** Revision number recorded
**Obligation:** MUST
**Acceptance Criteria:**
- Revision field populated (e.g., "1.0", "A", "2024-05-02")
- Follows consistent format
- Unique and traceable

### CR.05 Document Control
**Requirement:** Change log and approval chain present
**Obligation:** SHOULD
**Acceptance Criteria:**
- Document Control tab exists
- Contains revision history (at least 1 entry)
- Includes approver and date for each revision

### CR.06 Characteristic Catalog
**Requirement:** Characteristic Catalog populated
**Obligation:** MUST
**Acceptance Criteria:**
- Characteristic Catalog tab populated
- Minimum 5 characteristics defined
- All required columns present (ID, Name, Type, Unit, Range)

### CR.07 Measurement Catalog
**Requirement:** Measurement Catalog present
**Obligation:** SHOULD
**Acceptance Criteria:**
- Measurement Catalog tab exists and populated
- Minimum 3 measurements if applicable
- Measurement sources documented

### CR.08 Conversion Methods
**Requirement:** Conversion Methods defined
**Obligation:** MUST
**Acceptance Criteria:**
- Conversion Methods tab populated
- At least 1 method defined
- Methods match characteristic types (LINEAR for VALUE, RAT_FUNC, etc.)

### CR.09 Axis Definitions
**Requirement:** Axes defined for lookups
**Obligation:** SHOULD
**Acceptance Criteria:**
- Axis Descriptions tab exists
- Contains axes for all CURVE and MAP characteristics
- Each axis lists points and units

### CR.10 Record Layouts
**Requirement:** Record structures defined
**Obligation:** SHOULD
**Acceptance Criteria:**
- Record Layouts tab exists
- Matches VAL_BLK characteristic definitions
- Member structures documented

### CR.11 Function Hierarchy
**Requirement:** Functions organized
**Obligation:** MUST
**Acceptance Criteria:**
- Function Hierarchy tab populated
- Minimum 5 functions defined
- Functions assigned to groups

### CR.12 Group Hierarchy
**Requirement:** Groups organized
**Obligation:** SHOULD
**Acceptance Criteria:**
- Group Hierarchy tab exists
- Minimum 2 top-level groups defined
- Logical organization (e.g., Engine, Transmission, Emissions)

### CR.13 Memory Mapping
**Requirement:** Memory addresses assigned
**Obligation:** MUST
**Acceptance Criteria:**
- Memory Address Mapping tab populated
- All characteristics assigned addresses
- Address format consistent (hex or decimal)

### CR.14 Validation Rules
**Requirement:** Validation rules present
**Obligation:** SHOULD
**Acceptance Criteria:**
- Validation Rules tab exists
- Minimum 8 rules documented
- Rules cover consistency, integrity, naming

## A2L Object Completeness Checks (8)

### OBJ.01 Characteristic Types
**Requirement:** Multiple characteristic types present
**Obligation:** SHOULD
**Acceptance Criteria:**
- Mix of VALUE, CURVE, MAP types present
- At least 3 different types

### OBJ.02 Conversion Method Match
**Requirement:** Every characteristic has conversion method
**Obligation:** MUST
**Acceptance Criteria:**
- Ratio of conversion methods to characteristics >= 0.5
- Each VALUE/CURVE/MAP references valid method

### OBJ.03 Axis Coverage
**Requirement:** Axes defined for CURVE and MAP
**Obligation:** MUST
**Acceptance Criteria:**
- Every CURVE has 1 axis
- Every MAP has 2 axes
- Axes match expected dimensions

### OBJ.04 Record Completeness
**Requirement:** Records match VAL_BLK definitions
**Obligation:** SHOULD
**Acceptance Criteria:**
- Record count >= VAL_BLK count
- Each record has named members
- Member types documented

### OBJ.05 Memory Allocation
**Requirement:** Memory allocated to all characteristics
**Obligation:** MUST
**Acceptance Criteria:**
- All characteristics have addresses
- Total memory footprint calculated
- Address ranges valid

### OBJ.06 Function Coverage
**Requirement:** Functions defined
**Obligation:** MUST
**Acceptance Criteria:**
- All characteristics assigned to functions
- Function count >= 5

### OBJ.07 Group Structure
**Requirement:** Group hierarchy defined
**Obligation:** SHOULD
**Acceptance Criteria:**
- Group count >= 2
- Logical organization evident
- Parent-child relationships documented

### OBJ.08 ECU Identity
**Requirement:** ECU part number recorded
**Obligation:** SHOULD
**Acceptance Criteria:**
- ECU Identity tab populated
- Part number, serial format, hardware/software versions present

## Memory & Address Validation Checks (5)

### MEM.01 Address Bounds
**Requirement:** All addresses within ECU memory
**Obligation:** MUST
**Acceptance Criteria:**
- All addresses < ECU total memory size
- Address format matches ECU specification
- Segment assignments valid

### MEM.02 Address Overlap
**Requirement:** No overlapping address ranges
**Obligation:** MUST
**Acceptance Criteria:**
- Calculate ranges for each characteristic
- Verify no intersections
- Document segment allocation

### MEM.03 Alignment
**Requirement:** Addresses properly aligned
**Obligation:** MUST
**Acceptance Criteria:**
- 8-bit data: any alignment OK
- 16-bit data: even address
- 32-bit data: 4-byte aligned
- 64-bit data: 8-byte aligned

### MEM.04 Size Consistency
**Requirement:** Size calculations match definitions
**Obligation:** MUST
**Acceptance Criteria:**
- VAL_BLK size = sum of member sizes
- CURVE size = axis_points * element_size
- MAP size = x_points * y_points * element_size

### MEM.05 Memory Footprint
**Requirement:** Total memory footprint calculated
**Obligation:** SHOULD
**Acceptance Criteria:**
- Sum of all size columns computed
- Total documented in summary
- Compared against available memory

## Conversion Method Validation Checks (3)

### CONV.01 Linear Parameters
**Requirement:** LINEAR method parameters valid
**Obligation:** MUST
**Acceptance Criteria:**
- Both a (slope) and b (offset) defined
- Parameters are numbers (not text)
- Range check: a != 0 (unless identity)

### CONV.02 Formula Syntax
**Requirement:** FORMULA expressions well-formed
**Obligation:** SHOULD
**Acceptance Criteria:**
- Algebraic expressions parseable
- Variable references resolvable
- No undefined operators

### CONV.03 Unit Consistency
**Requirement:** Units consistent across methods
**Obligation:** MUST
**Acceptance Criteria:**
- Characteristic unit matches conversion input unit
- Output unit matches measurement unit
- No unit mismatches (e.g., RPM vs rad/s)
