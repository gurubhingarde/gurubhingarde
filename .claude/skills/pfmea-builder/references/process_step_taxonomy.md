# Process Step Taxonomy — Typical PCB/Electronics Manufacturing

## Overview

This taxonomy covers standard manufacturing steps for PCB and electronic assembly. Use these as a starting point for your own process flow. Adapt, add, or remove steps based on your specific manufacturing process.

## Complete Process Flow Example: Electronics ECU (Engine Control Unit)

### Phase 1: Incoming Material Preparation

**PST-01: PCB Receive and Incoming Inspection**
- Equipment: Visual inspection station, X-ray (sample), dimension gage
- Function: Verify PCB quality before assembly
- Key Characteristics: Trace continuity, pad cleanliness, dimensions, surface defects
- Key Parameters: Visual standard per IPC-A-610, no cracks > 0.1mm
- Common Failure Modes: Cracked traces, damaged pads, contamination, wrong revision

**PST-02: PCB Storage and Handling**
- Equipment: ESD-safe racks, moisture-controlled cabinet, humidity monitor
- Function: Preserve PCB condition during storage
- Key Characteristics: Moisture absorption, static damage risk
- Key Parameters: Relative humidity 30-60%, temperature 18-25°C
- Common Failure Modes: Moisture absorbed (affects solderability), ESD damage to solder pads

**PST-03: Component Kitting and Verification**
- Equipment: Component dispensing system, vision verification, barcode scanner
- Function: Prepare accurate component set per BOM
- Key Characteristics: Component identity, quantity, orientation marking
- Key Parameters: BOM match 100%, no substitutions without ECR
- Common Failure Modes: Wrong component dispensed, quantity error, wrong revision BOM

### Phase 2: Solder Paste and Stencil Preparation

**PST-04: Solder Paste Inspection and Printing**
- Equipment: Solder paste dispenser, stencil, visual/automated inspection
- Function: Apply solder paste precisely to PCB pads
- Key Characteristics: Paste volume, placement accuracy, edge definition
- Key Parameters: Paste per IPC J-STD-005, stencil aperture tolerance per IPC-7525
- Common Failure Modes: Paste insufficient or excessive, slump/collapse, bridging risk, paste dried/oxidized

### Phase 3: SMT (Surface Mount Technology) Assembly

**PST-05: SMT Component Placement**
- Equipment: Pick-and-place machine (vision-guided), component feeders
- Function: Place all SMT components in correct position and orientation
- Key Characteristics: Component placement accuracy, orientation, repeatability
- Key Parameters: X/Y tolerance ±0.1mm, rotation tolerance ±0.5°, z-height per component
- Common Failure Modes: Wrong component placed, component placed backwards, misaligned, missing component, component damage during pick

**PST-06: AOI (Automated Optical Inspection) — Post-Placement**
- Equipment: Automated Optical Inspection machine, vision camera
- Function: Detect placement and paste defects before reflow
- Key Characteristics: Component placement, paste coverage, solder bridges, missing components
- Key Parameters: 100% of components, placement accuracy 100%
- Common Failure Modes: AOI false pass (missed defects), false fail (nuisance rejection), calibration drift

### Phase 4: Solder Reflow and Inspection

**PST-07: Reflow Soldering**
- Equipment: Convection reflow oven, thermal profiler, solder alloy (SAC305, Pb-free standard)
- Function: Melt solder paste and form reliable solder joints
- Key Characteristics: Solder joint wetting, intermetallic formation, thermal stress
- Key Parameters: Peak temperature per IPC J-STD-001, dwell time 60-150 sec, ramp rate 1-3°C/sec, atmospheric oxygen < 5% (optional inert)
- Common Failure Modes: Cold solder joint (insufficient wetting), reflow skips, thermal shock cracking, solder bridging, component movement during reflow

**PST-08: AOI (Automated Optical Inspection) — Post-Reflow**
- Equipment: AOI machine, high-resolution camera, 3D capability (optional)
- Function: Detect reflow defects before further assembly
- Key Characteristics: Solder joint quality, bridges, opens, component presence/orientation
- Key Parameters: 100% inspection, accept per IPC J-STD-001 Grade A
- Common Failure Modes: Missed cold joints, false acceptance of marginal joints, false rejection

**PST-09: X-ray Inspection (Sample or 100%, Depending on Risk)**
- Equipment: X-ray system (or inline X-ray if high-reliability requirement)
- Function: Verify internal solder joint integrity and void content
- Key Characteristics: Ball grid array (BGA) solder joint quality, internal voids, interconnect integrity
- Key Parameters: Void acceptance ≤ 25% per IPC-A-610 Class A, sampling AQL 1.0 or 100%
- Common Failure Modes: Voids in solder balls (latent failure), missed hidden defects

### Phase 5: Through-Hole Assembly (if applicable)

**PST-10: Wave Solder or Hand Solder**
- Equipment: Wave solder machine (or soldering iron for hand soldering)
- Function: Solder through-hole components
- Key Characteristics: Solder joint quality, lead integrity, thermal stress
- Key Parameters: Solder per IPC J-STD-001, dwell time per component pin count
- Common Failure Modes: Cold joint, insufficient solder, lead oxidation, component damage from heat

### Phase 6: Electrical Verification

**PST-11: ICT (In-Circuit Test)**
- Equipment: ICT bed-of-nails tester, custom test probe fixture, ATE (Automatic Test Equipment)
- Function: Verify electrical continuity, shorts, parametric values
- Key Characteristics: Electrical connectivity, component functionality (resistance, capacitance, voltage)
- Key Parameters: Test coverage > 95%, digital pass/fail, parametric limits per specification
- Common Failure Modes: Test program error (missed faults), probe misalignment, false fail (nuisance), false pass (test gap), intermittent defects missed

**PST-12: FCT (Functional Test) — Optional Pre-Programming**
- Equipment: Custom functional test fixture or standalone tester, microprocessor support tools
- Function: Verify system-level functionality (e.g., power supply, clock, reset, communication bus)
- Key Characteristics: Power supply voltage stability, clock frequency, reset timing, bus communication
- Key Parameters: Supply voltage 4.5-5.5V (for 5V logic), clock tolerance ±5%, communication protocol per spec
- Common Failure Modes: Intermittent power supply noise, clock jitter, incorrect reset timing, communication errors

### Phase 7: Conformal Coating and Cleanup (if required)

**PST-13: Conformal Coat Application**
- Equipment: Spray booth or dip tank, conformal coat material (acrylic, silicone, parylene, urethane)
- Function: Protect PCB from moisture, corrosion, and environmental contamination
- Key Characteristics: Coating thickness, coverage uniformity, avoided areas (connectors, buttons)
- Key Parameters: Coating thickness 25-150 μm per material, coverage ≥ 95%, masked areas per design
- Common Failure Modes: Incomplete coverage (corrosion risk), coating on connector contacts (connection loss), excessive thickness (mechanical stress), contamination in coating

**PST-14: Cleaning (Post-Conformal Coat or Post-Assembly)**
- Equipment: Cleaning station, solvent or aqueous cleaner, drying oven
- Function: Remove flux residue and contamination
- Key Characteristics: Residue removal, cleanliness per IPC-A-610
- Key Parameters: Residue-free, visual cleanliness Class A
- Common Failure Modes: Insufficient cleaning (flux residue causes corrosion), corrosion from aggressive solvent, water damage from incomplete drying

### Phase 8: Programming and Configuration

**PST-15: Firmware Programming**
- Equipment: Programmer interface (JTAG, SPI, I²C, USB), development environment
- Function: Load firmware/software into microcontroller or programmable device
- Key Characteristics: Firmware version, checksum, configuration registers
- Key Parameters: Correct firmware image per build version, checksum verification, production configuration (serial number, calibration data)
- Common Failure Modes: Wrong firmware version loaded, checksum failure (corruption), incomplete programming, configuration registers incorrect

**PST-16: Calibration and Offset Loading** (if applicable)
- Equipment: Calibration jig, software tools
- Function: Load calibration data, trim offsets, serial numbers
- Key Characteristics: Calibration accuracy, offset correctness, serial number uniqueness
- Key Parameters: Offset tolerance per specification, serial number database check (no duplicates)
- Common Failure Modes: Wrong calibration set loaded, offset out of range, serial number collision/duplication

### Phase 9: Final Assembly and Integration

**PST-17: Mechanical Assembly**
- Equipment: Assembly fixtures, fasteners (screws, clips), torque tools
- Function: Integrate PCB sub-assemblies, connect mechanical components, install enclosure
- Key Characteristics: Fastener torque, alignment, mechanical fit, connector seating
- Key Parameters: Torque per spec (e.g., 0.5-0.8 Nm for M3 screw), alignment ≤ 0.5mm, full seating of connectors
- Common Failure Modes: Loose fastener (vibration failure), over-torqued (thread stripping), misalignment (connector failure), mechanical damage during assembly

**PST-18: System Functional Test (FCT) — Full Integration**
- Equipment: Full functional test bench, real-world simulator or vehicle hardware loop
- Function: Verify end-to-end system functionality in realistic environment
- Key Characteristics: Power supply stability, sensor inputs, actuator control, communication, safety functions
- Key Parameters: Supply voltage ramping, sensor stimulus (voltage, CAN messages), real-time response verification
- Common Failure Modes: Integration issue (component OK in isolation, fails in system), intermittent sensor/actuator fault, timing/synchronization issue, safety function fail

### Phase 10: Labeling, Documentation, and Packaging

**PST-19: Labeling and Serialization**
- Equipment: Label printer, barcode scanner, marking station
- Function: Apply identification labels, serial numbers, traceability codes
- Key Characteristics: Label legibility, serial number accuracy, barcode scanability, hazard labels (if applicable)
- Key Parameters: Barcode scannable (all 3 angles), serial number unique, label adhesive secure, expiration dates (if applicable)
- Common Failure Modes: Unreadable barcode (supply chain traceability fail), wrong serial number, label falls off during shipment, missing hazard label (regulatory issue)

**PST-20: Quality Audit / Final Inspection**
- Equipment: Inspection station, BOM verifier, visual audit checklist
- Function: 100% audit that product matches build specification
- Key Characteristics: BOM correctness, configuration (revision, options), visual defects, documentation completeness
- Key Parameters: BOM match per engineering build record, no visible defects per IPC-A-610, documentation in package
- Common Failure Modes: Audit skip or insufficient rigor, wrong variant shipped, missing documentation, hidden assembly defects (e.g., cold solder joint missed by earlier inspection)

**PST-21: Packaging and Preparation for Shipment**
- Equipment: Packaging station, void fill, moisture barrier, carton sealing
- Function: Protect product during shipment and storage
- Key Characteristics: Packaging integrity, moisture protection, cushioning, label placement
- Key Parameters: Void fill ≥ 2 inches, desiccant pack (if required), carton sealed and labeled, no mechanical damage visible
- Common Failure Modes: Insufficient cushioning (mechanical damage in transit), moisture ingress (corrosion), label damage (logistics routing fail), opened/tampered package (counterfeit risk)

## Summary Table: 21-Step Electronics Manufacturing Process

| Step ID | Step Name | Type | Key Risk |
|---------|-----------|------|----------|
| PST-01 | PCB Receive & Inspection | Inspection | Defective PCB assembly |
| PST-02 | PCB Storage & Handling | Storage | Moisture absorption, ESD |
| PST-03 | Component Kitting | Operation | BOM error, wrong revision |
| PST-04 | Solder Paste Inspection | Operation | Paste quality, volume |
| PST-05 | SMT Placement | Operation | Wrong component, orientation, accuracy |
| PST-06 | AOI Post-Placement | Inspection | False pass/fail, defect detection |
| PST-07 | Reflow Soldering | Operation | Cold joint, bridging, thermal damage |
| PST-08 | AOI Post-Reflow | Inspection | Missed defects |
| PST-09 | X-ray Inspection | Inspection | BGA void content, internal defects |
| PST-10 | Wave/Hand Solder | Operation | Solder joint quality, lead damage |
| PST-11 | ICT Test | Inspection | Test gaps, false pass/fail |
| PST-12 | FCT Pre-Programming | Inspection | Intermittent faults, functional gaps |
| PST-13 | Conformal Coat | Operation | Coverage, protection, connector damage |
| PST-14 | Cleaning | Operation | Flux residue, water damage |
| PST-15 | Firmware Programming | Operation | Wrong version, corruption, incomplete |
| PST-16 | Calibration | Operation | Wrong offsets, serial collision |
| PST-17 | Mechanical Assembly | Operation | Loose fastener, misalignment |
| PST-18 | System FCT | Inspection | Integration failure, timing issue |
| PST-19 | Labeling & Serialization | Operation | Barcode failure, wrong serial, missing label |
| PST-20 | Quality Audit | Inspection | Audit skip, wrong variant, defects missed |
| PST-21 | Packaging & Shipment | Operation | Damage, moisture, label loss |

Adapt this taxonomy to your specific product and process.
