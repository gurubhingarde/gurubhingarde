/* Com.h — signal layer: pack/unpack app signals into PDUs.
 * Signal table (id, offset, length, PDU mapping) is POC-scope placeholder —
 * real build generates this from the ARXML signal DB.
 */
#ifndef COM_H
#define COM_H

#include "../../Std_Types.h"
#include "../Can/Can.h"

void Com_Init(void);
void Com_MainFunction(void);  /* periodic signal send, call from scheduler */
void Com_RxIndication(uint16_t rxPduId, const Can_PduType *pdu);

Std_ReturnType Com_SendSignal(uint16_t signalId, const void *data);
Std_ReturnType Com_ReceiveSignal(uint16_t signalId, void *data);

#endif /* COM_H */
