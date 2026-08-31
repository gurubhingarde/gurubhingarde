/* EcuAbstraction.h — S32K144-specific wrapping of MCAL: pin map, board
 * config, clock tree choices. Keeps Bsw/Services and Bsw/Communication
 * hardware-agnostic; only this layer + Mcal/ know about the actual board.
 */
#ifndef ECU_ABSTRACTION_H
#define ECU_ABSTRACTION_H

void EcuAbstraction_Init(void);  /* TODO: Mcu_Init/Port_Init/Dio_Init via NXP RTD */

#endif /* ECU_ABSTRACTION_H */
