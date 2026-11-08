# Block Diagram Conventions for FSC

The FSC fault tree expansion is mechanical *only if* the block diagram is captured with consistent semantics. This reference defines the node taxonomy, edge semantics, and JSON schema the skill consumes.

## Node taxonomy

Every node in the block diagram must be classified into one of the following types. The skill uses the type to assign the node to the correct FTA branch (Input / Process / Output).

| Type         | FTA branch        | Examples                                                                  |
|--------------|-------------------|---------------------------------------------------------------------------|
| `sensor`     | Input failure     | Wheel speed sensor, IMU, steering angle sensor, brake pressure sensor.    |
| `comm_in`    | Input failure     | CAN message from another ECU, FlexRay, Ethernet, LIN.                     |
| `power_in`   | Input failure     | Vehicle 12 V supply, ignition signal, ground.                             |
| `processor`  | Process failure   | Main MCU, safety MCU, FPGA, ASIC, DSP.                                    |
| `software`   | Process failure   | Software partition / runtime / OS that hosts the safety-related code.     |
| `memory`     | Process failure   | RAM, Flash, EEPROM, NVRAM holding safety-related data or code.            |
| `actuator`   | Output failure    | Hydraulic valve, motor, solenoid, light.                                  |
| `driver`     | Output failure    | Power-stage IC, gate driver, MOSFET bank.                                 |
| `comm_out`   | Output failure    | CAN/FlexRay/Ethernet message produced by the item.                        |

A node that physically performs more than one role (e.g., an MCU that does both arbitration and output drive) is split into multiple logical nodes — one per role — so each role appears in the correct FTA branch with its own FSR.

## Required attributes per node

The skill's JSON schema for a node:

```json
{
  "id": "N03",
  "name": "ESC Main MCU",
  "type": "processor",
  "asil_relevant": true,
  "inputs": ["N01", "N02"],
  "outputs": ["N05"],
  "redundancy_group": null,
  "shared_resources": ["12V_main", "GND", "CLK_50MHz"],
  "notes": "Hosts yaw control SW partition; lockstep with N03b."
}
```

| Field              | Purpose                                                                                            |
|--------------------|----------------------------------------------------------------------------------------------------|
| `id`               | Stable identifier used in cross-references and FSR IDs.                                            |
| `name`             | Human-readable label used in FTA basic events and FSR text.                                        |
| `type`             | One of the taxonomy values above.                                                                  |
| `asil_relevant`    | If false, the node is part of the diagram for context but is excluded from FTA expansion.          |
| `inputs`           | Array of node IDs whose outputs feed this node.                                                    |
| `outputs`          | Array of node IDs this node feeds.                                                                 |
| `redundancy_group` | Tag identifying nodes that are designed-to-be-redundant peers; nodes with the same tag are decomposition candidates. |
| `shared_resources` | Tags for any common-cause vector. Two nodes with overlapping shared_resources cannot be decomposition candidates. |
| `notes`            | Free-text aid for reviewers.                                                                       |

## Independence inference

Two nodes are eligible for ASIL decomposition only when ALL of the following hold:

1. They share a non-null `redundancy_group`.
2. Their `shared_resources` lists are **disjoint**.
3. Neither node lists the other in its `inputs` (avoids cascading dependency).
4. The analyst confirms environmental and software-partition independence in the ASIL Allocation tab.

The skill computes (1)–(3) automatically and proposes decomposition; it asks the analyst to confirm (4) before writing the developed-to ASIL.

## Recommended diagram inventory pass

When walking the user through an architecture image, capture nodes in this order to minimise omissions:

1. **All sensors first** (label them N01..Nxx). Note shared 5 V or 12 V supplies under `shared_resources`.
2. **All communication inputs** (CAN messages from other ECUs).
3. **Power and clock distribution** (often a missed node — sensors share 5 V regulator, MCUs share clock).
4. **Processors and software partitions** — label SW partitions as separate nodes when they run on the same processor with MPU separation.
5. **Output drivers and actuators**.
6. **Communication outputs** (CAN messages produced by the item).

Always close with a sanity check: "Is there any node that, if it failed, could violate the safety goal but isn't on this list?" This prompt catches power supplies, ground returns, watchdog ICs, and reset controllers that are easy to skip.
