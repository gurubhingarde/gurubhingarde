"""UDS (ISO 14229) service identifiers, sub-functions and response codes."""

from __future__ import annotations

from enum import IntEnum

#: Positive-response offset added to the request SID by the server.
POSITIVE_RESPONSE_OFFSET = 0x40
#: SID of a negative response message.
NEGATIVE_RESPONSE_SID = 0x7F


class ServiceId(IntEnum):
    """Request service identifiers (SIDs)."""

    DIAGNOSTIC_SESSION_CONTROL = 0x10
    ECU_RESET = 0x11
    CLEAR_DIAGNOSTIC_INFORMATION = 0x14
    READ_DTC_INFORMATION = 0x19
    READ_DATA_BY_IDENTIFIER = 0x22
    READ_MEMORY_BY_ADDRESS = 0x23
    SECURITY_ACCESS = 0x27
    COMMUNICATION_CONTROL = 0x28
    READ_DATA_BY_PERIODIC_IDENTIFIER = 0x2A
    WRITE_DATA_BY_IDENTIFIER = 0x2E
    INPUT_OUTPUT_CONTROL_BY_IDENTIFIER = 0x2F
    ROUTINE_CONTROL = 0x31
    REQUEST_DOWNLOAD = 0x34
    REQUEST_UPLOAD = 0x35
    TRANSFER_DATA = 0x36
    REQUEST_TRANSFER_EXIT = 0x37
    WRITE_MEMORY_BY_ADDRESS = 0x3D
    TESTER_PRESENT = 0x3E
    CONTROL_DTC_SETTING = 0x85


class Session(IntEnum):
    """DiagnosticSessionControl (0x10) sub-functions."""

    DEFAULT = 0x01
    PROGRAMMING = 0x02
    EXTENDED = 0x03
    SAFETY_SYSTEM = 0x04


class ResetType(IntEnum):
    """ECUReset (0x11) sub-functions."""

    HARD = 0x01
    KEY_OFF_ON = 0x02
    SOFT = 0x03
    ENABLE_RAPID_POWER_SHUTDOWN = 0x04
    DISABLE_RAPID_POWER_SHUTDOWN = 0x05


class RoutineControlType(IntEnum):
    """RoutineControl (0x31) sub-functions."""

    START = 0x01
    STOP = 0x02
    REQUEST_RESULTS = 0x03


class NRC(IntEnum):
    """Negative Response Codes (ISO 14229-1 Annex A)."""

    GENERAL_REJECT = 0x10
    SERVICE_NOT_SUPPORTED = 0x11
    SUB_FUNCTION_NOT_SUPPORTED = 0x12
    INCORRECT_MESSAGE_LENGTH_OR_INVALID_FORMAT = 0x13
    RESPONSE_TOO_LONG = 0x14
    BUSY_REPEAT_REQUEST = 0x21
    CONDITIONS_NOT_CORRECT = 0x22
    REQUEST_SEQUENCE_ERROR = 0x24
    NO_RESPONSE_FROM_SUBNET_COMPONENT = 0x25
    FAILURE_PREVENTS_EXECUTION = 0x26
    REQUEST_OUT_OF_RANGE = 0x31
    SECURITY_ACCESS_DENIED = 0x33
    INVALID_KEY = 0x35
    EXCEEDED_NUMBER_OF_ATTEMPTS = 0x36
    REQUIRED_TIME_DELAY_NOT_EXPIRED = 0x37
    UPLOAD_DOWNLOAD_NOT_ACCEPTED = 0x70
    TRANSFER_DATA_SUSPENDED = 0x71
    GENERAL_PROGRAMMING_FAILURE = 0x72
    WRONG_BLOCK_SEQUENCE_COUNTER = 0x73
    REQUEST_CORRECTLY_RECEIVED_RESPONSE_PENDING = 0x78
    SUB_FUNCTION_NOT_SUPPORTED_IN_ACTIVE_SESSION = 0x7E
    SERVICE_NOT_SUPPORTED_IN_ACTIVE_SESSION = 0x7F
    VOLTAGE_TOO_HIGH = 0x92
    VOLTAGE_TOO_LOW = 0x93


def nrc_name(code: int) -> str:
    """Human-readable name for a negative response code."""
    try:
        return NRC(code).name
    except ValueError:
        return f"UNKNOWN_NRC_0x{code:02X}"


# Common Data Identifiers (DIDs) for ReadDataByIdentifier.
COMMON_DIDS = {
    0xF180: "BootSoftwareIdentification",
    0xF181: "ApplicationSoftwareIdentification",
    0xF182: "ApplicationDataIdentification",
    0xF187: "VehicleManufacturerSparePartNumber",
    0xF189: "VehicleManufacturerECUSoftwareVersionNumber",
    0xF18C: "ECUSerialNumber",
    0xF190: "VIN",
    0xF194: "SystemSupplierECUSoftwareNumber",
}
