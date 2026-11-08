"""DEM checklist check definitions (~28 checks)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class CheckDef:
    """Check definition."""
    check_id: str
    category: str  # Event | Debounce | Memory | Storage | Snapshot | OBD
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
    # Event checks (E1-E10)
    CheckDef(
        "E1",
        "Event",
        "DTC-to-event mapping complete",
        "Every DTC in the catalog must map to exactly one DEM Event",
        "MUST",
    ),
    CheckDef(
        "E2",
        "Event",
        "Event inventory completeness",
        "All configured events should be enumerated in the Event Inventory sheet",
        "MUST",
    ),
    CheckDef(
        "E3",
        "Event",
        "Event ID uniqueness",
        "No two events should share the same Event ID",
        "MUST",
    ),
    CheckDef(
        "E4",
        "Debounce",
        "Pre-passed threshold range",
        "Pre-passed threshold should be 5-10 counts (quick acceptance of good signal)",
        "SHOULD",
    ),
    CheckDef(
        "E5",
        "Debounce",
        "Pre-confirmed threshold range",
        "Pre-confirmed threshold should be 3-5 counts (quick confirmation)",
        "SHOULD",
    ),
    CheckDef(
        "E6",
        "Debounce",
        "Confirmed threshold range",
        "Confirmed threshold should be 1-20 counts (1 for ASIL D, 5-20 for QM)",
        "MUST",
    ),
    CheckDef(
        "E7",
        "Debounce",
        "Healed threshold range",
        "Healed threshold should be 40-80 counts (slow healing to prevent flutter)",
        "SHOULD",
    ),
    CheckDef(
        "E8",
        "Event",
        "Safety-critical event marking",
        "Events related to ASIL functions should be marked as safety-relevant",
        "SHOULD",
    ),
    CheckDef(
        "E9",
        "Event",
        "Event enable/disable consistency",
        "All events should be enabled unless explicitly disabled with rationale",
        "SHOULD",
    ),
    CheckDef(
        "E10",
        "Debounce",
        "Debounce strategy consistency",
        "Events within the same functional domain should use consistent debounce thresholds",
        "SHOULD",
    ),
    # Memory checks (M1-M10)
    CheckDef(
        "M1",
        "Memory",
        "Primary memory allocation",
        "Primary memory size must be specified (typically 512 bytes minimum)",
        "MUST",
    ),
    CheckDef(
        "M2",
        "Memory",
        "Memory adequacy for event count",
        "Allocated memory must accommodate all events (min 4 bytes per event + snapshot/EDR data)",
        "MUST",
    ),
    CheckDef(
        "M3",
        "Memory",
        "Secondary memory allocation",
        "Secondary memory should be 50% of primary (for aging data and statistics)",
        "SHOULD",
    ),
    CheckDef(
        "M4",
        "Storage",
        "NvM block mapping complete",
        "Every event must be assigned to a persistent NvM block ID",
        "MUST",
    ),
    CheckDef(
        "M5",
        "Storage",
        "NvM block ID uniqueness",
        "No two events should share the same NvM block ID",
        "MUST",
    ),
    CheckDef(
        "M6",
        "Memory",
        "Memory utilization vs. ECU budget",
        "DEM memory should not exceed 90% of available ECU memory",
        "SHOULD",
    ),
    CheckDef(
        "M7",
        "Memory",
        "Mirror memory configuration",
        "Mirror memory should be enabled for safety-critical events (optional but recommended)",
        "MAY",
    ),
    CheckDef(
        "M8",
        "Memory",
        "Aging counter memory allocation",
        "Memory for aging counters should be included in secondary memory allocation",
        "SHOULD",
    ),
    CheckDef(
        "M9",
        "Storage",
        "Persistent storage redundancy",
        "Critical event memory should have redundancy (mirror or backup mechanism)",
        "SHOULD",
    ),
    CheckDef(
        "M10",
        "Memory",
        "Memory growth margin",
        "Reserve at least 15-20% memory headroom for future events",
        "SHOULD",
    ),
    # Snapshot checks (S1-S8)
    CheckDef(
        "S1",
        "Snapshot",
        "Snapshot record class definition",
        "Every confirmed event should have a snapshot record class defined",
        "SHOULD",
    ),
    CheckDef(
        "S2",
        "Snapshot",
        "Snapshot data adequacy",
        "Snapshot should capture 4-8 data elements per event (min 8 bytes, max 32 bytes)",
        "SHOULD",
    ),
    CheckDef(
        "S3",
        "Snapshot",
        "Extended Data Record (EDR) definition",
        "Events should have EDR records for statistical or meta data (optional)",
        "MAY",
    ),
    CheckDef(
        "S4",
        "Snapshot",
        "EDR data completeness",
        "EDR should include occurrence counter, timestamp (if RTC), and aging counter",
        "SHOULD",
    ),
    CheckDef(
        "S5",
        "OBD",
        "OBD freeze frame enabled",
        "OBD-relevant events must have freeze frame capture enabled",
        "MUST",
    ),
    CheckDef(
        "S6",
        "OBD",
        "OBD frame 0 configuration",
        "Mandatory OBD PIDs should be defined for frame 0",
        "MUST",
    ),
    CheckDef(
        "S7",
        "OBD",
        "OBD additional frames (1-4)",
        "Optional freeze frames 1-4 may be configured for extended diagnostic data",
        "MAY",
    ),
    CheckDef(
        "S8",
        "Snapshot",
        "Safety-critical event snapshots",
        "All ASIL C/D events must have snapshot records defined",
        "MUST",
    ),
]
