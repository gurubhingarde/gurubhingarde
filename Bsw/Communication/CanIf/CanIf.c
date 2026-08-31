#include "CanIf.h"
#include "../PduR/PduR.h"

void CanIf_Init(void)
{
    Can_Init();
}

Std_ReturnType CanIf_Transmit(uint16_t txPduId, const Can_PduType *pdu)
{
    /* TODO: look up txPduId -> hth in the config table, then Can_Write() */
    (void)txPduId;
    return Can_Write(0u, pdu);
}

void CanIf_RxIndication(uint8_t hrh, const Can_PduType *pdu)
{
    /* TODO: look up hrh -> rxPduId in the config table */
    uint16_t rxPduId = 0u;
    (void)hrh;
    PduR_CanIfRxIndication(rxPduId, pdu);
}

void CanIf_TxConfirmation(uint8_t hth)
{
    (void)hth;
    /* TODO: forward to PduR if a TX confirmation is configured for this PDU */
}
