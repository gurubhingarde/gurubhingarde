# Secure Coding Guidelines Checklist Methodology

## Rating System

### Rating Definitions

| Rating | Definition | Color | Confidence |
|--------|-----------|-------|-----------|
| FC | Full Compliance — Requirement fully met with complete evidence | GREEN_OK | High |
| LC | Low Compliance — Requirement partially met, minor gaps exist | GREEN_OK | Medium |
| PC | Partial Compliance — Requirement substantially incomplete | ORANGE_PARTIAL | Medium |
| NO | Non-Compliance — Requirement not met or no evidence | RED_BAD | High |
| NA | Not Applicable — Requirement out of scope or not relevant | LIGHT_BLUE | N/A |
| PENDING | Assessment pending external evidence or verification | LIGHT_BLUE | Low |

## Check Categories

### Confirmation Review (CR)
Document-quality checks verifying structure, metadata, and maintainability per ISO/SAE 21434 Clause 8.2.

### Secure Coding Guidelines Assessment (SCG)
Substantive checks verifying scope definition, coding rules catalog (>= 30), CERT C/MISRA coverage, CWE Top 25 mapping, memory/integer/string/cryptography/authentication/logging safety rules, and tool configurations per AUTOSAR AP and CERT C standards.

### Verification Assessment (VA)
Checks verifying alignment with external V&V Plan and assessment report per ISO/SAE 21434 Clause 8.

## TOMCO Mapping

| Aspect | Coverage |
|--------|----------|
| **T**echnical | Memory, integer, string, crypto rules; tool configs; CERT/MISRA/CWE coverage |
| **O**rganizational | Scope definition; rule ownership; deviation process |
| **M**anagement | Rule catalog version; update frequency; compliance tracking |
| **C**ompliance | CERT C, MISRA Amendment 1, AUTOSAR C++14, CWE Top 25 |
| **O**perational | Tool integration (Coverity, CodeSonar, Polyspace); deviation handling |
