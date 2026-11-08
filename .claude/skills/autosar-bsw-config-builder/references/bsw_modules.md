# AUTOSAR BSW Module Catalog

## MCAL Module List
- Port: GPIO and pin configuration
- Dio: Digital input/output
- Adc: Analog-to-digital conversion
- Pwm: Pulse-width modulation
- Gpt: General purpose timers
- Icu: Input capture units
- Wdg: Watchdog timer
- Spi: Serial peripheral interface
- Uart: Universal async receiver/transmitter
- I2c: I2C communication interface

## ECU Abstraction Modules
- EcuM: ECU Manager (lifecycle, state machine)
- FeeM: EEPROM emulation (flash)
- MemIf: Memory interface abstraction
- Ea: EEPROM abstraction

## Service Layer Modules
- Com: PDU and signal communication
- PduR: PDU router (signal-to-PDU mapping)
- CanIf: CAN interface
- CanTp: CAN transport protocol
- LinIf: LIN interface
- LinTp: LIN transport protocol
- NvM: Non-volatile memory manager
- Det: Diagnostics event manager
- Dem: Diagnostics event memory
- Dcm: Diagnostics communication manager

## Complex Drivers
- Can: CAN controller driver
- Lin: LIN controller driver
- Eth: Ethernet controller driver
- EthTrcv: Ethernet transceiver

