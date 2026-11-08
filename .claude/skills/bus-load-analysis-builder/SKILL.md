---
name: bus-load-analysis-builder
description: Generate an audit-ready bus load analysis workbook quantifying CAN, CAN FD, FlexRay, or Automotive Ethernet bandwidth utilization with scenario-based load calculations including worst-case and fault-injection scenarios Use this skill when the user mentions bus load analysis builder.
---

# Bus Load Analysis Builder

Build a professional 10-tab xlsx workbook quantifying bandwidth utilization on vehicle networks.

## What this skill does

- Generates audit-ready bus load analysis workbook
- Supports CAN, CAN FD, FlexRay, and Automotive Ethernet protocols
- Calculates per-bus load percentage with baud rate conversion
- Includes scenario-based analysis (nominal, peak, worst-case, fault-injection)
- Provides headroom margin and load trend charts
- Features live Excel formulas for real-time scenario updates

## How to use it

Provide a JSON input with:
- Bus configuration (protocol, baud rate, frame overhead)
- Message inventory (cycle time, DLC, frame format)
- Optional: scenario overrides for peak/worst-case analysis

## What you get

10-tab professional xlsx:
1. Title
2. Document Control
3. Bus Configuration
4. Message Inventory
5. Signal Cycle Allocation
6. Load Calculation Worksheet (live formulas)
7. Scenario Analysis
8. Load Trend Charts
9. Recommendations
10. References

---

*Use this skill whenever the user mentions bus load, bandwidth analysis, CAN load percentage, network utilization, or busload margin.*
