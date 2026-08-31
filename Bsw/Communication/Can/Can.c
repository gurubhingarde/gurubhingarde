#include "Can.h"
#include "../CanIf/CanIf.h"

void Can_Init(void)
{
    /* TODO: call Can_43_FLEXCAN_Init() from NXP RTD once Mcal/ vendored */
}

Std_ReturnType Can_Write(uint8_t hth, const Can_PduType *pdu)
{
    (void)hth;
    (void)pdu;
    /* TODO: call Can_43_FLEXCAN_Write() */
    return E_NOT_OK;
}

void Can_MainFunction_Read(void)
{
    /* TODO: poll RX FIFO / ISR-filled buffer, then: */
    /* CanIf_RxIndication(hrh, &pdu); */
}

void Can_MainFunction_Write(void)
{
    /* TODO: poll TX complete flag, then: */
    /* CanIf_TxConfirmation(hth); */
}
