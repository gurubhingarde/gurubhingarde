# CS Architecture Assessment Methodology

## Scoring Conventions

- **FC (Fully Compliant)**: Requirement met with high confidence; evidence directly verified in xlsx.
- **LC (Largely Compliant)**: Requirement substantially met; minor gaps acceptable or evidence inferred.
- **PC (Partially Compliant)**: Requirement partially met; significant corrective action needed.
- **NO (Not Compliant)**: Requirement not met; blocking issue.
- **NA (Not Applicable)**: Requirement does not apply; explicitly marked.
- **PENDING (blank Assessment)**: Subjective or requires external artifact; reviewer must judge.

## Confidence Levels

- **High**: Directly verified from xlsx content (e.g., "Element catalog populated").
- **Medium**: Inferred from xlsx with caveat (e.g., "Crypto inventory present; reviewer to confirm approved algorithms").
- **Low**: Subjective or requires external artifact (e.g., "Key lifecycle justified in specification").

## Obligation

- **Shall**: Mandatory per AUTOSAR Security or ISO 26262. Failure = major non-conformance.
- **Should**: Recommended. Failure = minor non-conformance or improvement opportunity.

## Check Categories

### Confirmation Review (CR) — 14 Document Quality Checks
- Document structure, title, author/approver, revision, status, doc ID, TOC, references, assumptions, hyperlinks, searchability, terminology, compliance matrix, review/approval signatures.

### Functional Safety Assessment (FSA) — 14 Substantive CS Architecture Checks
- CS Element catalog populated; supplier + certification for ASIL/CAL-relevant elements; approved cryptographic algorithms (no MD5/SHA1/DES/RC4); minimum key lengths (AES>=128, RSA>=2048, ECC>=P-256); key lifecycle defined; secure boot with root-of-trust and anti-rollback; secure communication channels with auth/enc/integrity/replay; access control roles/privileges/auth factors; CSR-to-element allocation matrix complete; defense-in-depth layers; debug interfaces disabled in production; crypto certificate expiry/renewal plan; HSM/Secure Element usage; standards references.

### Verification Assessment (VA) — 14 Verification Checks
- Alignment with CS Concept; requirements verifiability; test case specification; test environment; test execution; verification report; coverage metrics; anomaly handling; regression testing; traceability matrix; verification independence; AUTOSAR/ISO 26262 compliance; review and approval; quality metrics and KPIs.
