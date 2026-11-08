# LDF Specification Methodology

## Overview

A LIN Description File (LDF) per ISO 17987 specifies the complete configuration of a LIN cluster: master node, slave nodes, frames, signals, schedule tables, and encoding types.

## Definition Flow

1. **Cluster Header** — LIN version (2.0, 2.1, 2.2A), baud rate (1–20 kbps), timing parameters
2. **Master Node** — single timing master; no periodic autonomy
3. **Slave Nodes** — list with identifiers; respond to master timing
4. **Frame Definitions**
   - Unconditional: periodic, fixed slot
   - Event-triggered: on-demand with timeout
   - Sporadic: lowest-priority, fills idle slots
   - Diagnostic: UDS-like services (0x22, 0x2E, 0x34, etc.)
5. **Signal Allocation** — each signal belongs to exactly one frame; type (physical/logical)
6. **Schedule Tables** — frame sequencing per operational mode (idle, normal, diagnostic)
7. **Encoding Types** — scale, offset, units, min/max physical bounds

## Validation Checkpoint

- Baud rate within 1–20 kbps
- Frame length ≤ 8 bytes
- No signal assigned to multiple frames
- Every slave responds to at least one frame
- Schedule covers all frames across all modes
- All signals defined in at least one frame
