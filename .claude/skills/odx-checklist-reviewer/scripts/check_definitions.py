"""ODX checklist check definitions (~30 checks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CheckDef:
    """Check definition."""
    check_id: str
    category: str  # Variant | PDU | Service | Communication | Flash | Inherit
    title: str
    description: str
    obligation: str  # MUST | SHOULD | MAY


@dataclass
class CheckResult:
    """Check result."""
    check_id: str
    check_name: str | None
    rating: str  # FC | LC | PC | NC | NA
    finding: str | None
    confidence: str  # High | Medium | Low


CHECKS = [
    # Variant checks (V1-V8)
    CheckDef(
        "V1",
        "Variant",
        "Base variant ECU IDs unique",
        "Every base variant must have a unique, non-empty ECU ID",
        "MUST",
    ),
    CheckDef(
        "V2",
        "Variant",
        "Derived variant inheritance",
        "Every derived variant must inherit from exactly one base variant",
        "MUST",
    ),
    CheckDef(
        "V3",
        "Variant",
        "No circular inheritance",
        "Variant inheritance chain must form a forest (no cycles)",
        "MUST",
    ),
    CheckDef(
        "V4",
        "Layer",
        "ODX layer hierarchy complete",
        "All four ODX layers (D, C, V, FD) should be represented",
        "SHOULD",
    ),
    CheckDef(
        "V5",
        "Variant",
        "Variant naming consistency",
        "Variant IDs should follow naming convention (e.g., VAR_<market>_<config>)",
        "SHOULD",
    ),
    CheckDef(
        "V6",
        "Layer",
        "ODX-D services coverage",
        "All services defined in ODX-D should be mapped to at least one variant",
        "MUST",
    ),
    CheckDef(
        "V7",
        "Layer",
        "ODX-C communication defined",
        "Communication parameters must be specified for each physical channel",
        "MUST",
    ),
    CheckDef(
        "V8",
        "Layer",
        "ODX-V vehicle topology",
        "Vehicle topology and ECU mapping should be documented",
        "SHOULD",
    ),
    # PDU checks (P1-P12)
    CheckDef(
        "P1",
        "PDU",
        "PDU library complete",
        "All PDUs referenced in services must be defined in the PDU library",
        "MUST",
    ),
    CheckDef(
        "P2",
        "Service",
        "Service request/response pairs",
        "Every service must have both a request PDU and a response PDU",
        "MUST",
    ),
    CheckDef(
        "P3",
        "PDU",
        "Signal definitions complete",
        "All signals in PDUs should have unit, conversion formula, and range",
        "SHOULD",
    ),
    CheckDef(
        "P4",
        "Service",
        "DTC enumeration",
        "All diagnostic trouble codes should be enumerated with severity",
        "MUST",
    ),
    CheckDef(
        "P5",
        "Service",
        "Data object ranges",
        "Data objects should define min/max physical value ranges",
        "SHOULD",
    ),
    CheckDef(
        "P6",
        "Service",
        "Parameter validation rules",
        "Input parameters should define valid value ranges and constraints",
        "SHOULD",
    ),
    CheckDef(
        "P7",
        "Service",
        "Service completeness",
        "No orphaned services (every service should have request/response)",
        "MUST",
    ),
    CheckDef(
        "P8",
        "Service",
        "Negative response coverage",
        "All negative responses should include error code and description",
        "SHOULD",
    ),
    CheckDef(
        "P9",
        "PDU",
        "Multiplexing consistency",
        "Multiplexing rules in PDUs should be internally consistent",
        "MUST",
    ),
    CheckDef(
        "P10",
        "PDU",
        "Signal bit mapping",
        "No signal should overlap in bit position within the same PDU",
        "MUST",
    ),
    CheckDef(
        "P11",
        "Service",
        "Safety-relevant marking",
        "Services affecting ASIL functions should be marked safety-relevant",
        "SHOULD",
    ),
    CheckDef(
        "P12",
        "Service",
        "Service versioning",
        "Legacy or deprecated services should be explicitly marked",
        "MAY",
    ),
    # Communication checks (C1-C10)
    CheckDef(
        "C1",
        "Communication",
        "Bus speed definition",
        "Physical bus speed must be defined (CAN/LIN/Ethernet)",
        "MUST",
    ),
    CheckDef(
        "C2",
        "Communication",
        "Timing parameters",
        "P2 timeout, inter-frame delay, and response timing must be specified",
        "MUST",
    ),
    CheckDef(
        "C3",
        "Communication",
        "Flow control mechanism",
        "Flow control (CTS, WAIT) should be defined if applicable",
        "SHOULD",
    ),
    CheckDef(
        "C4",
        "Communication",
        "Protocol-specific headers",
        "CAN frame IDs, LIN frame bytes, Ethernet addresses must be defined",
        "MUST",
    ),
    CheckDef(
        "C5",
        "Flash",
        "Memory segment definition",
        "Flash memory must be partitioned into Boot, App, Calib, NV segments",
        "MUST",
    ),
    CheckDef(
        "C6",
        "Flash",
        "Programming algorithm",
        "Flash programming sequence and erase/write procedures must be defined",
        "SHOULD",
    ),
    CheckDef(
        "C7",
        "Flash",
        "CRC algorithm specification",
        "CRC/checksum algorithm, polynomial, and protected regions must be defined",
        "MUST",
    ),
    CheckDef(
        "C8",
        "Flash",
        "Security unlock procedure",
        "Authentication and security access timing should be documented",
        "SHOULD",
    ),
    CheckDef(
        "C9",
        "Flash",
        "Non-volatile data layout",
        "Persistent data regions (NV data, calibration) must be mapped",
        "MUST",
    ),
    CheckDef(
        "C10",
        "Flash",
        "Rollback / recovery strategy",
        "Mechanism for rollback on failed flash or recovery should be documented",
        "MAY",
    ),
]
