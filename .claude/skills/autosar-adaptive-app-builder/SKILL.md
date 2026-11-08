---
name: autosar-adaptive-app-builder
description: Generate an audit-ready AUTOSAR Adaptive Application specification workbook per AUTOSAR Adaptive Platform R22-11 covering application manifests, service manifests, machine manifests, ara - -com service interfaces, ara - -exec lifecycle, deployment topology, and POSIX execution context for service-oriented automotive applications. Use this skill when the user mentions autosar adaptive app builder.
---

# autosar-adaptive-app-builder

Generate an audit-ready AUTOSAR Adaptive Application specification workbook per AUTOSAR Adaptive Platform R22-11 covering application manifests, service manifests, machine manifests, ara::com service interfaces, ara::exec lifecycle, deployment topology, and POSIX execution context for service-oriented automotive applications.

## When to use

Use this skill whenever the user mentions AUTOSAR Adaptive, ara::com, ara::exec, Adaptive Application, application manifest, machine manifest, or service-oriented automotive software.

## How to use

Provide or reference an Adaptive Application scope:
- Application name, SWCL (SoftwareComponent for Adaptive)
- ara::com service interface definitions (request-response, event, field)
- ara::exec process and state machine lifecycle
- Machine manifest scope (host ECU, processors, network interfaces)
- Service instance mappings and SOME/IP configuration
- Deployment constraints and resource budgets

The skill generates a 13-tab workbook with:
- Application identity and manifest
- Service manifest with ara::com interface definitions
- Machine manifest with host configuration
- ara::exec lifecycle states and transitions
- Process configuration and execution context
- Deployment topology and SOME/IP service ID mapping
- Resource constraints and allocation
- Validation rules

## Output

Multi-tab XLSX workbook (audit-ready):
- Title, Document Control, Application Identity
- Application Manifest, Service Manifest
- Machine Manifest
- ara::com Service Interfaces
- ara::exec Lifecycle States
- Process Configuration
- Deployment Topology
- Resource Constraints, SOME/IP Configuration
- Validation Rules, References
