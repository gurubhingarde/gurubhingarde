#include "PduR.h"
#include "../CanIf/CanIf.h"
#include "../Com/Com.h"

void PduR_Init(void)
{
    /* TODO: nothing to init for a static routing table */
}

void PduR_CanIfRxIndication(uint16_t rxPduId, const Can_PduType *pdu)
{
    /* TODO: route table lookup rxPduId -> Com PDU id */
    Com_RxIndication(rxPduId, pdu);
}

Std_ReturnType PduR_ComTransmit(uint16_t txPduId, const Can_PduType *pdu)
{
    /* TODO: route table lookup Com PDU id -> CanIf txPduId */
    return CanIf_Transmit(txPduId, pdu);
}
