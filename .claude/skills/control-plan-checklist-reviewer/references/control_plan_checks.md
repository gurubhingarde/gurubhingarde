# Control Plan Checklist — Check Definitions

## Confirmation Review (16 checks)

Document quality and structure per IATF 16949 §8.1.

| # | Requirement | Obligation | Verifies | Auto-Fill |
|---|-------------|-----------|----------|-----------|
| 1 | Is document structured (multiple tabs, clear sections)? | Shall | Tab count ≥ 8 | High |
| 2 | Was latest AIAG/OEM template used? | Should | control-plan-builder signature | Medium |
| 3 | Does structure facilitate search (Title, TOC, References)? | Should | Title tab + tab navigation | High |
| 4a | Does title cover scope? | Shall | Title field populated | High |
| 4b | Are Key Contact and Core Team listed? | Shall | Header Block team fields | High |
| 4c | Are Customer/Supplier approvals documented? | Shall | Approval date fields | High |
| 5 | Is Plan Type specified (Prototype/Pre-launch/Production)? | Shall | Plan Type field | High |
| 6 | Is revision history maintained? | Should | Document Control tab entries | Medium |
| 7 | Are headers/footers updated? | Should | Manual verification required | Low |
| 8 | Are references to PFMEA/procedures listed? | Should | References tab present | Medium |
| 9 | Have all sections been completed? | Should | Tab presence + row count | High |
| 10 | Is MSA Plan tab populated? | Should | ≥1 MSA entry | High |
| 11 | Is Reaction Plan Library populated? | Should | ≥1 reaction plan | High |
| 12 | Is Poka-Yoke Catalog populated (where applicable)? | Should | Poka-Yoke entries (NA if none) | High |
| 13 | Is SPC Method Allocation documented? | Should | SPC entries | High |
| 14 | Is there linkage to PFMEA failure modes? | Should | Manual verification | Low |

## Control Plan Assessment (14 checks)

Core AIAG Control Plan requirements per IATF 16949:2016.

| # | Requirement | Obligation | Verifies | Auto-Fill |
|---|-------------|-----------|----------|-----------|
| 1 | Header block complete (plan#, contact, team, approvals)? | Shall | 5/5 header fields | High |
| 2 | Plan Type specified (Prototype/Pre-launch/Production)? | Shall | Recognized plan type value | High |
| 3 | Each row linked to process step? | Shall | Process step field populated | High |
| 4 | Each characteristic has spec/tolerance? | Shall | Spec lower AND/OR spec upper | High |
| 5 | Each characteristic has evaluation technique (gage)? | Shall | Gage field populated | High |
| 6 | Each characteristic has sample size + frequency? | Shall | Both fields populated | High |
| 7 | Each characteristic has control method? | Shall | Control method field populated | High |
| 8 | Each characteristic references Reaction Plan? | Shall | Reaction plan ID field | High |
| 9 | Special Characteristics from PFMEA echoed? | Shall | ≥1 entry in Special Characteristics tab | High |
| 10 | Every gage has MSA Plan with R&R target? | Shall | MSA entry count ≥ unique gage count; R&R targets | High |
| 11 | SPC method allocation documented? | Shall | ≥1 SPC entry | High |
| 12 | Poka-Yoke devices have verification method? | Should | Poka-Yoke entry count; verification method field | High |
| 13 | All referenced Reaction Plans exist in library? | Shall | Referenced plan IDs ⊆ available plan IDs | High |
| 14 | Each high-AP PFMEA failure mode in Control Plan? | Shall | Manual verification against PFMEA | Low |

## Verification Assessment (8 checks)

Testing adequacy per IATF 16949 §8.2.3.

| # | Requirement | Obligation | Verifies | Auto-Fill |
|---|-------------|-----------|----------|-----------|
| 1 | Verification Plan addresses all characteristics? | Shall | External verification plan document | Low |
| 2 | Verification methods defined (test/inspect/audit)? | Shall | External verification plan document | Low |
| 3 | Verification Report documents pass/fail? | Shall | External verification report document | Low |
| 4 | Control effectiveness (SPC performance) verified? | Should | External verification report | Low |
| 5 | Gage adequacy verified by MSA/GR&R? | Shall | ≥1 MSA entry; R&R study | High |
| 6 | Reaction Plans tested and effective? | Should | External verification report | Low |
| 7 | Special Characteristic controls verified? | Should | External verification report + control plan entry | High |
| 8 | Poka-Yoke devices functionally tested? | Should | External verification report + poka-yoke entry | High |

## Check Logic Summary

### Auto-Fill Strategy

**High-confidence auto-fill** (FC/LC/PC/NO):
- Header block completeness
- Worksheet row structure (all characteristic fields populated or absent)
- MSA, SPC, poka-yoke, reaction plan library presence

**Medium-confidence auto-fill** (FC/LC/PC):
- Tab counts and structure
- Template signature detection

**Low-confidence / Pending** (drafted for reviewer):
- Scope verification (does title really cover scope?)
- Configuration management (organizational practice)
- External verification plan/report adequacy
- PFMEA linkage (requires cross-document tracing)
- Control effectiveness judgment

### Rating Decision Rules

**FC (Fully Compliant)**:
- 100% of worksheet rows have all required fields
- All referenced reaction plans exist in library
- Header block complete (5/5 fields)
- MSA/SPC/poka-yoke entries present where applicable

**LC (Largely Compliant)**:
- 90–99% of rows have required fields
- Some MSA/SPC/poka-yoke entries present but incomplete

**PC (Partially Compliant)**:
- 70–89% of rows have required fields
- OR: Reaction plan library incomplete but most plans exist
- OR: Special Characteristics not echoed (may not exist)
- OR: MSA entries incomplete (missing R&R targets)

**NO (Not Compliant)**:
- <70% of rows complete
- OR: Critical field (header block, plan type) missing
- OR: Referenced reaction plans do not exist in library

**NA (Not Applicable)**:
- Poka-yoke: no devices used (legitimate for some processes)
- SPC: prototype/pre-launch phase (may not require SPC yet)
- Special Characteristics: no high-AP failure modes in PFMEA

### Obligation vs. Rating

| Rating | Shall Obligation | Should Obligation |
|--------|------------------|------------------|
| FC | ✓ Proceed | ✓ Proceed |
| LC | ✓ Proceed (minor gaps) | ✓ Proceed |
| PC | ⚠ Conditional approval (gaps must be resolved) | ✓ Proceed (document gaps) |
| NO | ✗ Reject (must resolve) | ⚠ Conditional (note gaps) |
| NA | ✓ N/A | ✓ N/A |
| Pending | — (awaits judgment) | — (awaits judgment) |

**Release criteria**:
- All Shall items: ≤ LC (FC + LC only)
- All Should items: ≤ PC (FC + LC + PC)
- Zero critical Pending rows
