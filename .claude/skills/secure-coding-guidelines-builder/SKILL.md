---
name: secure-coding-guidelines-builder
description: Generate ISO 21434-aligned secure coding guidelines for embedded automotive software. Reads a project JSON (code base, CAL, language) and scaffolds a 14-tab excel workbook with secure coding rules (CERT C, MISRA Amendment 1, AUTOSAR C++14), memory/integer/string safety rules, cryptography and authentication rules, CWE Top 25 mappings, static analysis tool configuration, deviation process, and references. Produces audit-ready guidelines for ESC/TCU/IVI/APA projects. Always use this skill instead of producing freeform secure coding guidelines in chat.
---

# Secure Coding Guidelines Builder (ISO 21434)

Secure coding guidelines translate cybersecurity requirements into concrete, enforceable coding rules aligned with industry standards (CERT C Secure Coding Standard, MISRA C:2012 Amendment 1 security additions, AUTOSAR C++14 subset) and mapped to Common Weakness Enumeration (CWE) Top 25 vulnerabilities.

## When to use this skill

Use whenever the user wants to:
- Generate secure coding guidelines for an embedded automotive project (ESC, TCU, IVI, APA, etc.)
- Define memory safety rules (bounds checking, no use-after-free, buffer overflow prevention)
- Specify integer safety rules (overflow/underflow, sign conversion, wraparound)
- Document string/I-O safety rules (format strings, untrusted input validation)
- Establish cryptography rules (approved algorithms, key length minimums, side-channel resistance)
- Define authentication, authorization, logging, and audit trail requirements
- Map secure coding rules to CWE Top 25 vulnerabilities
- Configure static analysis tools (Coverity, CodeSonar, Polyspace) for compliance
- Document deviation and waiver process for security rule exceptions
- Hand off to code review, static analysis baseline setup, and ISO 21434 verification activities

Pre-requisite: a project description (code base name, CAL, target language, applicable standards). If the user has only a safety plan, redirect them to tsc-builder or hara-builder first.

## Workflow

### Step 1 — Confirm project scope
Ask for: project name, document ID, code base (ESC/TCU/IVI), CAL (A/B/C/D), target language (C/C++), applicable standards (CERT C / MISRA / AUTOSAR).

### Step 2 — Project metadata and configuration interview
Ask for (or accept as JSON input): project.name, doc_id, revision, date, author, approver, code_base, cal, language, applicable_standards, static_analysis_tools (Coverity/CodeSonar/Polyspace/etc.).
Capture into a JSON file matching examples/sample_secure_coding_guidelines_esc.json.

### Step 3 — Read the references on first use
Before generating, read:
- references/methodology.md — what secure coding guidelines are, ISO 21434 integration, template approach
- references/cert_c_categories.md — CERT C Secure Coding categories
- references/cwe_top25_mapping.md — mapping CERT/MISRA rules to CWE Top 25

### Step 4 — Generate
```bash
python scripts/generate_secure_coding_guidelines.py <input.json> <output.xlsx>
python scripts/recalc.py <output.xlsx>
```

### Step 5 — Review and customize
Review checkpoints in order:
1. **00_Title_Page** — confirms project, doc ID, revision, code base, language
2. **01_Document_Control** — revision history
3. **02_Scope** — applicable guidelines, tool chain, target ASIL/CAL
4. **03_Coding_Rules_Catalog** — all rules (CERT C / MISRA / AUTOSAR), severity (Mandatory/Required/Advisory), CWE mapping
5. **04-09** — category-specific rules (Memory, Integer, String/I-O, Cryptography, Authentication/Authorization, Logging/Audit)
6. **10_CWE_Top25_Coverage** — per CWE entry, which rules address it
7. **11_Tool_Configuration** — per static analysis tool, rule pack and false-positive handling
8. **12_Deviation_Process** — how to request, approve, and track security rule waivers
9. **13_References** — CERT C, MISRA, AUTOSAR, CWE, OWASP links

When the user requests changes, edit the input JSON and regenerate. The xlsx is a derived artifact; the input JSON is the source of truth.

## Output structure (14 tabs)

| Tab | Purpose |
|-----|---------|
| 00 | Title Page: Project, doc ID, revision, dates, code base, language, applicable standards |
| 01 | Document Control: Revision history and approval |
| 02 | Scope: Code base in scope, target CAL, applicable guidelines, tool chain |
| 03 | Coding Rules Catalog: All rules, source (CERT C / MISRA / AUTOSAR), category, severity, CWE mapping, rationale, examples |
| 04 | Memory Safety Rules: Bounds checking, use-after-free, double-free, buffer overflow, stack canary |
| 05 | Integer Safety Rules: Overflow/underflow, sign conversion, wraparound, bitwise operations |
| 06 | String/I-O Rules: Buffer overflow, format strings, untrusted input validation |
| 07 | Cryptography Rules: Approved algorithms, key length minimums, randomness, side-channel resistance |
| 08 | Authentication/Authorization: Password handling, session management, privilege separation |
| 09 | Logging/Audit: What to log, secrets/PII handling, log integrity, retention |
| 10 | CWE Top 25 Coverage: Per CWE entry, which rules in this guideline address it |
| 11 | Tool Configuration: Per static analysis tool, rule pack to enable, false-positive policy, baseline |
| 12 | Deviation Process: When/how to request deviation, approval workflow, deviation log |
| 13 | References: CERT C, MISRA, AUTOSAR, CWE, OWASP |

## Files in this skill

```
secure-coding-guidelines-builder/
├── SKILL.md
├── scripts/
│   ├── generate_secure_coding_guidelines.py  # main generator (input JSON → 14-tab xlsx)
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md
│   ├── cert_c_categories.md
│   └── cwe_top25_mapping.md
└── examples/
    └── sample_secure_coding_guidelines_esc.json
```
