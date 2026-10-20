"""dltool - open DoIP/CAN ECU diagnostic and flash-download tool.

A clean-room implementation built from the public standards:

* ISO 13400 (DoIP - Diagnostics over IP, Ethernet)
* ISO 14229 (UDS - Unified Diagnostic Services)
* ISO 15765-2 (ISO-TP - diagnostics over CAN / CAN-FD)
* Motorola S-record firmware format

No proprietary or third-party vendor code is reproduced here; the wire
formats implemented are those defined by the above public specifications.
"""

from .firmware import Segment, ReprogrammingBlock, Firmware
from .uds.client import UdsClient, NegativeResponse
from .uds import services as uds
from .transport.base import Transport, TransportError

__all__ = [
    "Segment",
    "ReprogrammingBlock",
    "Firmware",
    "UdsClient",
    "NegativeResponse",
    "uds",
    "Transport",
    "TransportError",
    "__version__",
]

__version__ = "0.1.0"
