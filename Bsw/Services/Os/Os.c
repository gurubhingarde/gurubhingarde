#include "Os.h"

#define OS_MAX_TASKS 8u

typedef struct {
    Os_TaskFunc func;
    uint32_t    periodMs;
    uint32_t    lastRunMs;
} Os_TaskEntry;

static Os_TaskEntry s_tasks[OS_MAX_TASKS];
static uint8_t s_taskCount = 0u;

void Os_Init(void)
{
    /* TODO: configure SysTick for 1ms tick once Mcal/ is vendored */
    s_taskCount = 0u;
}

void Os_AddTask(Os_TaskFunc func, uint32_t periodMs)
{
    if (s_taskCount < OS_MAX_TASKS) {
        s_tasks[s_taskCount].func = func;
        s_tasks[s_taskCount].periodMs = periodMs;
        s_tasks[s_taskCount].lastRunMs = 0u;
        s_taskCount++;
    }
}

void Os_Run(void)
{
    /* TODO: read SysTick ms counter, run tasks whose period elapsed, sleep/wfi between ticks */
    for (;;) {
        /* placeholder loop body */
    }
}
