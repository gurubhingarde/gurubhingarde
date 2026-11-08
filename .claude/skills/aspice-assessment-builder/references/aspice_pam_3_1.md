# ASPICE PAM v3.1 Reference

## Process Areas (PAs)

### System Engineering (SYS)
- **SYS.1**: System Concept — Establish high-level system vision
- **SYS.2**: System Requirements — Define what system must do
- **SYS.3**: System Architectural Design — Define system structure
- **SYS.4**: System Integration — Assemble and test system
- **SYS.5**: System Testing — Validate system meets requirements

### Software Engineering (SWE)
- **SWE.1**: Software Implementation — Write and unit test code
- **SWE.2**: Software Unit Verification — Verify units work correctly
- **SWE.3**: Software Integration — Integrate units into components
- **SWE.4**: Software Component Verification — Verify components
- **SWE.5**: Software Component Integration Testing — Integration tests
- **SWE.6**: Software System Testing — System-level SW tests

### Supporting Processes (SUP)
- **SUP.1**: Configuration Management — Track and manage artifacts
- **SUP.8**: Problem Resolution — Report and fix defects
- **SUP.9**: Quality Assurance — Ensure quality practices
- **SUP.10**: Verification — Check work meets specs

### Management (MAN)
- **MAN.3**: Project Management — Plan and track project
- **MAN.5**: Resource Management — Allocate people and resources

### Acquisition (ACQ)
- **ACQ.4**: Supplier Monitoring — Monitor supplier performance

## Process Attributes (PAs)

### Capability Level 1: Performed
- **PA1.1** (Process Performance): Base practices executed

### Capability Level 2: Managed
- **PA2.1** (Performance Management): Process goals established, monitored
- **PA2.2** (Work Product Management): Work products defined, managed

### Capability Level 3: Established
- **PA3.1** (Process Definition): Process documented, communicated
- **PA3.2** (Process Deployment): Process deployed across organization

### Capability Level 4: Predictable
- **PA4.1** (Process Measurement): Process metrics collected and analyzed
- **PA4.2** (Process Control): Process adjustments made based on metrics

### Capability Level 5: Innovating
- **PA5.1** (Process Innovation): Improvements identified and implemented
- **PA5.2** (Process Optimization): Optimization opportunities pursued

## Indicator Ratings (N/P/L/F)

- **N (Not achieved)**: Practice not performed or insufficient evidence
- **P (Partially achieved)**: Practice partially performed, gaps exist
- **L (Largely achieved)**: Practice well performed, minor gaps only
- **F (Fully achieved)**: Practice fully performed, all objectives met

## Rating Algorithm (CL Determination)

- **CL0**: Process not performed
- **CL1**: PA1.1 >= L
- **CL2**: CL1 + PA2.1 >= L + PA2.2 >= L
- **CL3**: CL2 + PA3.1 >= L + PA3.2 >= L
- **CL4**: CL3 + PA4.1 >= L + PA4.2 >= L
- **CL5**: CL4 + PA5.1 >= L + PA5.2 >= L

## Base Practices (BPs)

Each process has 3-8 base practices. Examples:

### SWE.1 Base Practices:
- Implement software units per design
- Execute unit tests and record results
- Integrate software units into components

### SYS.1 Base Practices:
- Establish system concept statement
- Define system boundary and interfaces
- Identify stakeholder needs

## Generic Practices (GPs)

Generic practices apply across processes:
- **GP1** (CL2+): Establish and maintain documented process descriptions
- **GP2** (CL2+): Manage work products (versions, changes)
- **GP3** (CL3+): Define and deploy standard processes
- **GP4** (CL3+): Communicate process across organization
- **GP5** (CL4+): Establish and maintain measurement systems
- **GP6** (CL4+): Analyze and adjust process based on data
- **GP7** (CL5+): Identify innovation opportunities
- **GP8** (CL5+): Implement innovations
