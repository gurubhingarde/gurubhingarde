# LDF Check Catalog (30 Checks)

## Document Structure Checks (14)

### CR-01: Document Structure
**Check:** Document is structured into ≥5 tabs  
**Rationale:** Organized structure supports navigation, traceability, and audit readiness  
**Pass Criteria:** Title, Document Control, Cluster Header, Node Attributes, Frame Catalog, Signal Catalog, Schedule Tables, and References tabs present  
**Common Issue:** Single flat spreadsheet without organization

### CR-02: Template Version
**Check:** Latest LDF template version used  
**Rationale:** Template ensures consistency with ISO 17987 conventions  
**Pass Criteria:** Document structure mirrors standard LDF template  
**Common Issue:** Custom or outdated template  

### CR-03: Searchable/Navigable
**Check:** Table of Contents present and hyperlinked  
**Rationale:** Enables quick navigation and review  
**Pass Criteria:** Document Control or TOC tab with tab references  
**Common Issue:** No TOC

### CR-04a, CR-04b, CR-04c, CR-04d, CR-04e: Title Page Metadata
**Checks:** Title, Author/Approver, Unique Revision, Change History, Status  
**Rationale:** Traceability and configuration control  
**Pass Criteria:** All fields populated on Title page and Document Control tab  
**Common Issue:** Missing fields leave document uncontrolled

### CR-05: Revision Consistency
**Check:** Revision ID matches across Title page and Document Control  
**Rationale:** Prevents version mismatch confusion  
**Pass Criteria:** Same revision shown in both places  
**Common Issue:** Inconsistent revision numbering

### CR-06: Configuration Management
**Check:** Document stored in CM system  
**Rationale:** Enterprise version control and change tracking  
**Pass Criteria:** Document managed per company CM policy  
**Common Issue:** Ad-hoc file sharing without CM

### CR-07: Headers/Footers
**Check:** Company logo, document ID, revision in page headers  
**Rationale:** Professional appearance and traceability on printed pages  
**Pass Criteria:** Headers include company ID and revision  
**Common Issue:** Missing or incomplete headers

### CR-08: TOC Completeness
**Check:** Table of Contents references all tabs  
**Rationale:** Complete navigation and audit trail  
**Pass Criteria:** All tabs listed and accessible from TOC  
**Common Issue:** Partial or outdated TOC

### CR-09: Cross-References
**Check:** Linked documents referenced (e.g., HSI, system architecture)  
**Rationale:** Traceability to related specifications  
**Pass Criteria:** Related specifications cited  
**Common Issue:** No linkage to upstream/downstream docs

### CR-10: Sections Complete
**Check:** ≥95% of structured fields populated  
**Rationale:** Ensures specification is substantially complete  
**Pass Criteria:** Minimal gaps in cluster, node, frame, signal, schedule definition  
**Common Issue:** Incomplete cluster definition

---

## Technical Assessment Checks (16)

### TSA-01: Cluster Metadata
**Check:** Cluster name, abbreviation, project, doc ID populated  
**Rationale:** Basic traceability and identification  
**Pass Criteria:** All cluster header fields present  
**Common Issue:** Missing name or project context

### TSA-02: LIN Version
**Check:** Valid LIN version specified (2.0, 2.1, 2.2A)  
**Rationale:** Ensures specification uses correct standard  
**Pass Criteria:** LIN version matches project requirement  
**Common Issue:** Unspecified or non-standard version

### TSA-03: Baud Rate
**Check:** Baud rate within 1–20 kbps range  
**Rationale:** LIN physical layer constraint per ISO 17987  
**Pass Criteria:** 1 ≤ baud_rate ≤ 20 kbps (typical 19.2)  
**Common Issue:** Out-of-range baud rate (e.g., 115.2 kbps)

### TSA-04: Timing Master
**Check:** Exactly 1 master node assigned  
**Rationale:** LIN cluster requires single timing master  
**Pass Criteria:** Master node role defined  
**Common Issue:** No master or multiple masters

### TSA-05: Master Node Definition
**Check:** Master node name and identifier present  
**Rationale:** Unambiguous master identification  
**Pass Criteria:** Master name and unique ID assigned  
**Common Issue:** Master reference without ID

### TSA-06: Slave Nodes
**Check:** ≥1 slave node defined with identifier  
**Rationale:** LIN cluster must have nodes responding to master  
**Pass Criteria:** List of slaves with unique IDs  
**Common Issue:** No slave nodes (master-only cluster invalid)

### TSA-07: Node Roles
**Check:** All slaves have defined communication role  
**Rationale:** Determines which frames each node publishes/subscribes  
**Pass Criteria:** Slave list annotated with publisher/subscriber roles  
**Common Issue:** Slaves with undefined roles

### TSA-08: Frame Definitions
**Check:** ≥1 frame with ID, name, type, length  
**Rationale:** Frames are the transport unit in LIN  
**Pass Criteria:** Frame Catalog populated  
**Common Issue:** No frames defined

### TSA-09: Frame Types
**Check:** Appropriate mix of unconditional, event-triggered, sporadic, diagnostic  
**Rationale:** Different frame types serve different latency/reliability needs  
**Pass Criteria:** At least unconditional + 1 other type for realistic systems  
**Common Issue:** Only unconditional frames (missing diagnostic)

### TSA-10: Frame Publishers
**Check:** Every frame has exactly 1 publisher  
**Rationale:** LIN frames are single-producer (no arbitration)  
**Pass Criteria:** Publisher assigned to all frames  
**Common Issue:** Unassigned or multi-publisher frames

### TSA-11: Frame Length
**Check:** All frames ≤ 8 bytes  
**Rationale:** LIN physical layer constraint  
**Pass Criteria:** Max frame length = 8  
**Common Issue:** Frame exceeds 8 bytes (overfull payload)

### TSA-12: Signal Definitions
**Check:** ≥1 signal with name, frame, type  
**Rationale:** Signals are the data units communicated in frames  
**Pass Criteria:** Signal Catalog populated  
**Common Issue:** No signals (frames without data)

### TSA-13: Signal Allocation
**Check:** Each signal in exactly 1 frame  
**Rationale:** Prevents ambiguity in frame data layout  
**Pass Criteria:** No signal duplicated across frames  
**Common Issue:** Same signal in multiple frames or unallocated signals

### TSA-14: Signal Encoding
**Check:** Scale, offset, unit populated for each signal  
**Rationale:** Defines physical-to-raw value conversion  
**Pass Criteria:** Encoding info complete  
**Common Issue:** Missing scale/offset/unit

### TSA-15: Signal Bounds
**Check:** Min/max values consistent with signal type  
**Rationale:** Validates signal range is well-defined  
**Pass Criteria:** min_value < max_value for all signals  
**Common Issue:** Inverted or missing bounds

### TSA-16: Schedule Tables
**Check:** ≥1 schedule table per operational mode  
**Rationale:** Defines which frames are transmitted in each operating state  
**Pass Criteria:** Schedule tables for at least Idle and Normal modes  
**Common Issue:** No schedules or single flat schedule

### TSA-17: Schedule Coverage
**Check:** All frames present in at least 1 schedule mode  
**Rationale:** Ensures no frame is orphaned (undefined transmission)  
**Pass Criteria:** Every frame ID appears in at least one schedule  
**Common Issue:** Frame defined but never scheduled

### TSA-18: Schedule Timing Feasibility
**Check:** Schedule slots non-overlapping, cycle time met  
**Rationale:** Physical timing constraint; ensures frames transmit without collision  
**Pass Criteria:** Total scheduled duration ≤ cycle time per mode  
**Common Issue:** Overlapping slots or exceeded cycle time
