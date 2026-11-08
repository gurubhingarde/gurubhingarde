# MBSE Checks Detail

## CR01: All Required Tabs Present

Verifies the workbook contains all eight core ARCADIA tabs.

Required tabs:
- Title
- Document Control
- System Identification
- Operational Analysis
- System Analysis
- Logical Analysis
- Physical Analysis
- Inter-Layer Traceability

**Finding**: List missing tabs
**Recommended Action**: Create missing tabs and populate

## CR02: System Name Identified

System must have clear identity on Title page.

**Finding**: Extract or note absence of system name
**Recommended Action**: Populate Title with system name and abbreviation

## CR04: Operational Scenarios

3+ scenarios needed to capture relevant operational contexts.

**Finding**: Count scenarios in Operational Analysis tab
**Recommended Action**: Define additional scenarios (e.g., normal, degraded, emergency modes)

## CR05: System Functions

5+ system-level functions needed to adequately decompose system behavior.

**Finding**: Count functions in System Analysis tab
**Recommended Action**: Use functional hierarchy to expand top-level functions

## CR06-CR07: Logical and Physical Components

3+ logical, 2+ physical to ensure adequate decomposition and technology assignment.

**Finding**: Count components in respective tabs
**Recommended Action**: Allocate logical functions to logical components; map logical to physical
