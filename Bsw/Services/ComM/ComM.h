/* ComM.h — Communication Manager: owns CAN channel bus-on/bus-off state. */
#ifndef COMM_H
#define COMM_H

#include "../../Std_Types.h"

typedef enum {
    COMM_NO_COMMUNICATION = 0,
    COMM_FULL_COMMUNICATION
} ComM_ModeType;

void ComM_Init(void);
Std_ReturnType ComM_RequestComMode(uint8_t channel, ComM_ModeType mode);
ComM_ModeType ComM_GetState(uint8_t channel);

#endif /* COMM_H */
