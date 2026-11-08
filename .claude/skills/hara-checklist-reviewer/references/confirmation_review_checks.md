# Confirmation Review Checks (Generic Document Quality)

These 14 checks come from the TOMCO HARA Confirmation Measures template, which in turn implements the document-quality requirements of ISO 26262-8 Clause 10. They are the same set of checks the assessor applies to any safety-related work product (HARA, FSC, TSC, FMEDA, etc.).

| # | Requirement                                                                                                | Obligation | Auto-fill confidence | What the skill checks                                                                              |
|---|-----------------------------------------------------------------------------------------------------------|------------|----------------------|----------------------------------------------------------------------------------------------------|
| 1 | Document structured in a clear manner (headlines, layouts) supporting maintainability                      | Shall      | Medium               | Counts tabs, presence of section headers, structured tables                                        |
| 2 | Latest template available used                                                                             | Should     | Low (draft)          | Cannot detect from xlsx; flagged for human                                                         |
| 3 | Document structure facilitates information search (cross-references, index, abbreviations)                 | Should     | Medium               | Detects reference tabs, structured columns, ID columns                                             |
| 4a| Title covers the scope of the content                                                                      | Shall      | Low (draft)          | Subjective — drafts finding referencing the title cell                                             |
| 4b| Author and approver(s) listed                                                                              | Shall      | High                 | Reads Title page Author and Approver fields; FC if both non-empty                                  |
| 4c| Unique identification per revision                                                                         | Shall      | High                 | Reads Doc Control tab revision column                                                              |
| 4d| Change history available                                                                                   | Shall      | High                 | Counts Doc Control rows; FC if a revision history table is populated                               |
| 4e| Status of the work product provided                                                                        | Shall      | High                 | Reads Title page Status field; FC if non-empty                                                     |
| 5 | Current applicable revision identifiable                                                                   | Shall      | High                 | Reads Title page Revision field; FC if non-empty                                                   |
| 6 | Document under configuration and change management                                                         | Shall      | Low (draft)          | Organisational property; cannot detect from xlsx                                                   |
| 7 | Header and footer updated                                                                                  | Should     | Low (draft)          | Worksheet headers/footers not reliably accessible via openpyxl content                             |
| 8 | Correct table of content                                                                                   | Shall      | Medium               | FC if a Title or Contents tab lists the other tabs                                                 |
| 9 | Reference table lists all references in the work product                                                   | Should     | Low (draft)          | Drafts finding pointing to References tab if present                                               |
| 10| All sections of the work product completed                                                                 | Should     | High                 | Counts empty cells in HARA / Safety Goals tabs; PC if completion below threshold                   |

## Mapping to TOMCO checklist row IDs

The TOMCO checklist Confirmation Review tab numbers these 1 through 14 in column A. The skill writes its assessment in the same row order so the output xlsx is row-for-row comparable to a hand-filled TOMCO checklist.
