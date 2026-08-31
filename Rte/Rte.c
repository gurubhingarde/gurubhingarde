#include "Rte.h"
#include "../Bsw/Communication/Com/Com.h"

#define SIGNAL_ID_FAULT_LEVEL 0u  /* TODO: real id from signal DB once App/Fault is ported in */

void Rte_Init(void)
{
    /* nothing to do yet — no SWC state to init */
}

Std_ReturnType Rte_Write_FaultLevel(FaultLevelType level)
{
    return Com_SendSignal(SIGNAL_ID_FAULT_LEVEL, &level);
}

Std_ReturnType Rte_Read_FaultLevel(FaultLevelType *level)
{
    return Com_ReceiveSignal(SIGNAL_ID_FAULT_LEVEL, level);
}
