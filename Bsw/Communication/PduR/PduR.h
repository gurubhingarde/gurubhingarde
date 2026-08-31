/* PduR.h — PDU Router: static routing table between CanIf and Com.
 * No dynamic routing — table is fixed at build time (POC scope).
 */
#ifndef PDUR_H
#define PDUR_H

#include "../../Std_Types.h"
#include "../Can/Can.h"

void PduR_Init(void);
void PduR_CanIfRxIndication(uint16_t rxPduId, const Can_PduType *pdu);
Std_ReturnType PduR_ComTransmit(uint16_t txPduId, const Can_PduType *pdu);

#endif /* PDUR_H */
