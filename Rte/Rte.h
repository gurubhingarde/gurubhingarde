/* Rte.h — hand-written glue between App SWCs and Bsw/Communication/Com.
 * Stand-in for RTE-gen (no tresos/DaVinci license). Each Rte_Write/Read_*
 * pair below is what a real RTE generator would emit per SWC port; add one
 * pair per signal as App SWCs get ported in.
 */
#ifndef RTE_H
#define RTE_H

#include "../Bsw/Std_Types.h"
#include "Rte_Type.h"

void Rte_Init(void);

/* Example port stub — replace once first App SWC (Fault) is wired in */
Std_ReturnType Rte_Write_FaultLevel(FaultLevelType level);
Std_ReturnType Rte_Read_FaultLevel(FaultLevelType *level);

#endif /* RTE_H */
