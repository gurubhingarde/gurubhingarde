#include "Com.h"
#include "../PduR/PduR.h"

void Com_Init(void)
{
    /* TODO: init signal table state */
}

void Com_MainFunction(void)
{
    /* TODO: walk periodic-signal table, pack due signals, PduR_ComTransmit() */
}

void Com_RxIndication(uint16_t rxPduId, const Can_PduType *pdu)
{
    /* TODO: unpack signals mapped to rxPduId into signal storage */
    (void)rxPduId;
    (void)pdu;
}

Std_ReturnType Com_SendSignal(uint16_t signalId, const void *data)
{
    /* TODO: write into signal storage, mark dirty for next Com_MainFunction */
    (void)signalId;
    (void)data;
    return E_NOT_OK;
}

Std_ReturnType Com_ReceiveSignal(uint16_t signalId, void *data)
{
    /* TODO: read latest value from signal storage */
    (void)signalId;
    (void)data;
    return E_NOT_OK;
}
