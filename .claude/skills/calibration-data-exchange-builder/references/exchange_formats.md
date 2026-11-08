# Calibration Data Exchange Formats

## DCM (ETAS Data Conservation)

**File Extension:** .dcm  
**Usage:** INCA, CANape, ATI Vision  
**Scope:** Single calibration dataset  

### Structure
- Header: dataset identity, baseline reference, approvals
- Sections: FUNKTIONEN, KENNLINIE, KENNFELD, STUETZSTELLENVERTEILUNG, FESTWERTEBLOCK
- Footer: validation summary, checksums

### Compatibility
- INCA → DCM → CANape: Full round-trip supported
- INCA → DCM → ATI Vision: Read-only
- Best for: Multi-supplier workflows with common tools

### Strengths
- Standard format, widely recognized
- Built-in validation and checksums
- Parameter traceability clear
- Small file size

### Limitations
- Single variant per file
- Limited metadata capacity
- No embedded change history
- ASCII format may have encoding issues

## CDFX (Calibration Data Format eXchange)

**File Extension:** .cdfx  
**Usage:** OEM-specific (often OEM proprietary)  
**Scope:** Multi-variant, complete calibration package  

### Structure
- XML-based or binary wrapper
- Metadata: vehicle/variant, hardware, software versions
- Calibration section: parameter values organized by function
- Baseline section: approved baseline snapshot
- Change section: modification history, approvals
- Validation section: range checks, unit consistency

### Compatibility
- OEM-to-Tier-1 handoff primary use
- Tool-agnostic (can be imported to any calibration tool)
- Version compatibility matrix embedded

### Strengths
- Flexible structure, supports variants
- Comprehensive metadata
- Change history included
- Baseline traceability built-in

### Limitations
- Format often proprietary, custom parsing
- Larger file size (XML or binary)
- Requires OEM validation schema
- Limited external tool support

## PaCo (Parameter Control)

**File Extension:** .paco  
**Usage:** Vector tools (CANape, CANoe)  
**Scope:** Single dataset with Vector-specific features  

### Structure
- Parameter records: values, units, physical ranges
- Metadata: project, variant, creator, date
- Version info: baseline, change log
- Tool-specific extensions: import/export rules

### Compatibility
- CANape: Native read/write
- CANoe: Diagnostic support
- Other tools: Limited (Vector proprietary)

### Strengths
- Native support in Vector tools
- Detailed metadata per parameter
- Version control integrated
- Baseline snapshots supported

### Limitations
- Vector tool dependency
- Not suitable for multi-supplier workflows
- Limited adoption outside Vector ecosystem

## Format Selection Matrix

| Criterion | DCM | CDFX | PaCo |
|-----------|-----|------|------|
| Multi-supplier | Yes | Yes | No |
| Multi-variant | No | Yes | No |
| Change history | No | Yes | Yes |
| Baseline tracing | Yes | Yes | Yes |
| Wide tool support | Yes | No | No |
| File size | Small | Large | Medium |
| Validation rules | Built-in | Embedded | Tool-dependent |
| Metadata richness | Low | High | Medium |

## Implementation Guidelines

### DCM Handoff
1. Create DCM from A2L-defined parameters
2. Verify all values within physical ranges
3. Validate axis monotonicity, map dimensions
4. Baseline snapshot created (date-tagged)
5. Archive DCM with approval signatures
6. Exchange DCM file between OEM and Tier-1

### CDFX Handoff
1. Create CDFX package with OEM schema
2. Include baseline snapshot (complete dataset)
3. Embed change protocol and approvals
4. Document variant coverage (e.g., Euro5, EPA)
5. Validate format against OEM schema
6. Archive CDFX with audit trail

### PaCo Handoff
1. Export parameters to PaCo from CANape
2. Set up version control (baseline tag)
3. Include change notes and approvals
4. Validate against CANoe diagnostic definitions
5. Archive PaCo with full metadata

## Baseline Snapshot Rules

Every exchange includes baseline snapshot:
- **Baseline version**: Unique ID (date-tagged)
- **Approved by**: OEM and Tier-1 signatures
- **Change description**: Why this baseline
- **Parameter values**: Complete dataset at this version
- **A2L reference**: Original A2L document version
- **Metadata**: Creation date, tools, environment

Baseline snapshot is immutable:
- Previous baselines retained 12+ months
- Rollback to previous baseline always possible
- All changes traced against baseline
- Audit trail complete and signed

## Validation at Exchange Boundary

Every format exchange validates:
1. **Completeness**: All required parameters present
2. **Ranges**: All values within physical bounds
3. **Types**: Data types match A2L definitions
4. **Units**: Units consistent with A2L
5. **References**: Axis references resolvable
6. **Checksums**: File integrity verified
7. **Approvals**: Baseline signatures present
8. **Traceability**: Baseline reference documented
