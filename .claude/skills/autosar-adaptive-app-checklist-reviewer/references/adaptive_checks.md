# Adaptive App Checks

## C001: Application Manifest References
Requirement: Application manifest must reference only existing services.
Check: Cross-reference Application Manifest against Service Manifest.
Rating: FC if all references valid, PC if missing, NO if invalid.

## C002: Service Manifest Coverage
Requirement: Service manifest must cover all required services.
Check: Verify Service Manifest tab completeness.
Rating: FC if complete, PC if partial, NA if none required.

## C003: Machine Manifest Complete
Requirement: Machine manifest must define all required services and hosts.
Check: Verify Machine Manifest covers service deployment.
Rating: FC if complete, PC if partial, NO if missing.

## C004: ara::com Service Interfaces
Requirement: Service interfaces must be properly defined.
Check: Verify ara::com Service Interfaces tab populated.
Rating: FC if defined, LC if partial, NA if none required.

## C005: ara::exec State Consistency
Requirement: ara::exec states must transition consistently.
Check: Analyze state transitions in ara::exec Lifecycle.
Rating: FC if consistent, PC if questionable, NO if invalid.

## C006: SOME/IP Service ID Uniqueness
Requirement: SOME/IP service IDs must be unique system-wide.
Check: Scan Service ID column in SOME/IP Configuration.
Rating: FC if unique, NO if duplicates found.

## C007: Process Configuration
Requirement: Process configuration should be complete with POSIX attributes.
Check: Verify Process Configuration tab populated.
Rating: FC if complete, LC if partial, NA if not required.

## C008: Resource Budget Feasibility
Requirement: Resource budget must be feasible for target platform.
Check: Analyze Resource Constraints against platform spec.
Rating: FC if feasible, PC if marginal, NO if infeasible.

