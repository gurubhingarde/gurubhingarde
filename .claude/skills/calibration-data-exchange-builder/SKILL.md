---
name: calibration-data-exchange-builder
description: Generate an audit-ready calibration data exchange agreement workbook for OEM and Tier-1 calibration management covering parameter ownership matrix, baseline references, change protocols, exchange formats including DCM and CDFX, version control, signoffs, and acceptance criteria for cross-supplier calibration data delivery. Use this skill when the user mentions calibration data exchange builder.
---

# calibration-data-exchange-builder

Generate an audit-ready calibration data exchange agreement workbook for OEM and Tier-1 calibration management covering parameter ownership matrix, baseline references, change protocols, exchange formats including DCM and CDFX, version control, signoffs, and acceptance criteria for cross-supplier calibration data delivery.

Use this skill whenever the user mentions calibration data exchange, calibration ownership, calibration baseline, CDFX, PaCo, parameter handover, or OEM-supplier calibration agreement.

## Output

Generates 11-tab Excel workbook with:

- **Title** — Document control header, parties, agreement scope
- **Document Control** — Change log, versions, approvals
- **Parties** — OEM, Tier-1, Tier-2 identification and roles
- **Parameter Ownership Matrix** — Per characteristic: owner, change rights, baseline
- **Baseline References** — Approved baseline snapshot for each parameter
- **Exchange Format Specification** — DCM, CDFX, PaCo format rules and compatibility
- **Change Protocol** — Process for baseline modifications, approvals, traceability
- **Version Control** — Versioning scheme, baseline tags, change history
- **Acceptance Criteria** — Measurable acceptance conditions for deliverables
- **Signoff Block** — OEM and Tier-1 authorization signatures
- **References** — Standard cross-references and supporting documents

## Usage

```bash
python generate_caldex.py <input.json> <output.xlsx>
```

Input JSON contains parties, parameter ownership, baselines, formats, change protocol, and acceptance criteria.

## References

See `references/methodology.md` for design guidance and `references/exchange_formats.md` for format specifications.
