/* Os.h — cooperative scheduler stand-in, not OSEK-compliant. See README.md
 * in this folder for why. Fixed-rate task table driven by SysTick.
 */
#ifndef OS_H
#define OS_H

#include <stdint.h>

typedef void (*Os_TaskFunc)(void);

void Os_Init(void);
void Os_AddTask(Os_TaskFunc func, uint32_t periodMs);
void Os_Run(void);  /* never returns — main loop */

#endif /* OS_H */
