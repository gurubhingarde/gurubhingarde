/* Can.h — CAN driver, wraps MCAL FlexCAN (NXP RTD Can_43_FLEXCAN).
 * Stub until Mcal/ is vendored — bodies TODO in Can.c.
 */
#ifndef CAN_H
#define CAN_H

#include "../../Std_Types.h"

typedef struct {
    uint32_t id;
    uint8_t  dlc;
    uint8_t  data[8];
} Can_PduType;

void Can_Init(void);
Std_ReturnType Can_Write(uint8_t hth, const Can_PduType *pdu);
void Can_MainFunction_Read(void);   /* polled RX — call from scheduler */
void Can_MainFunction_Write(void);  /* polled TX confirmation */

#endif /* CAN_H */
