/* CanIf.h — CAN Interface: hardware-independent routing between Can driver
 * and PduR. Callbacks are invoked by Can.c on RX/TX events.
 */
#ifndef CANIF_H
#define CANIF_H

#include "../../Std_Types.h"
#include "../Can/Can.h"

void CanIf_Init(void);
Std_ReturnType CanIf_Transmit(uint16_t txPduId, const Can_PduType *pdu);
void CanIf_RxIndication(uint8_t hrh, const Can_PduType *pdu);
void CanIf_TxConfirmation(uint8_t hth);

#endif /* CANIF_H */
