---
name: automotive-ethernet-builder
description: Generate an audit-ready Automotive Ethernet network configuration workbook per IEEE 100BASE-T1, 1000BASE-T1, and 10BASE-T1S covering SOME/IP service catalog, VLAN segmentation, switch configuration, TSN scheduling, and AVB stream allocation for high-bandwidth in-vehicle networks.
---

# Automotive Ethernet Configuration Builder

Generates a complete, audit-ready Automotive Ethernet network configuration xlsx per IEEE 100BASE-T1, 1000BASE-T1, 10BASE-T1S and AUTOSAR Ethernet stack standards. Covers network topology, VLAN segmentation, switch forwarding tables, SOME/IP service catalog, AVB stream allocation, TSN scheduling, multicast routing, and validation rules.

## When to use this skill

Use whenever the user mentions:
- Automotive Ethernet, BroadR-Reach, high-speed in-vehicle networks
- SOME/IP service-oriented communication, RPC/event services
- IEEE 100BASE-T1, 1000BASE-T1, 10BASE-T1S
- VLAN segmentation, switch configuration, multicast routing
- TSN (Time Sensitive Networking), AVB (Audio/Video Bridging)
- AUTOSAR Ethernet stack, network architecture design

## Workflow

1. Gather network topology: switches, ECUs, links, bandwidth requirements
2. Build input JSON per schema in `scripts/generate_autoeth.py`
3. Generate: `python scripts/generate_autoeth.py <input.json> <output.xlsx>`
4. Recalc formulas: `python scripts/recalc.py <output.xlsx>`
5. Review and iterate

## Output structure (12 tabs)

| # | Tab | Purpose |
|---|-----|---------|
| 1 | Title | Network name, project, doc ID, revision |
| 2 | Document Control | Revision history, distribution list |
| 3 | Network Topology | Switches, ECUs, physical links, bandwidth |
| 4 | Physical Layer Config | PHY per link (100BASE-T1, 1000BASE-T1, 10BASE-T1S), auto-negotiation |
| 5 | VLAN Segmentation | VLAN tags, priority classes, isolation domains |
| 6 | Switch Forwarding Tables | MAC address learning, port forwarding rules |
| 7 | SOME/IP Service Catalog | Service IDs, methods, events, provider/consumer roles |
| 8 | AVB Stream Allocation | Talker/Listener pairs, bandwidth reservation, traffic class |
| 9 | TSN Scheduling | Scheduled gate times, Qbv (per-queue traffic scheduling) |
| 10 | Multicast Routing | IGMP snooping, multicast group address allocation |
| 11 | Validation Rules | Bandwidth budget, MAC uniqueness, VLAN tag consistency |
| 12 | References | IEEE, AUTOSAR specification citations |

## Files

```
automotive-ethernet-builder/
├── SKILL.md
├── scripts/
│   ├── generate_autoeth.py
│   ├── recalc.py
│   └── office/soffice.py
├── references/
│   ├── methodology.md
│   └── autoeth_conventions.md
└── examples/
```
