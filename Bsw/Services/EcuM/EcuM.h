/* EcuM.h — ECU State Manager: owns startup/run/shutdown sequencing. */
#ifndef ECUM_H
#define ECUM_H

typedef enum {
    ECUM_STATE_STARTUP = 0,
    ECUM_STATE_RUN,
    ECUM_STATE_SLEEP,
    ECUM_STATE_SHUTDOWN
} EcuM_StateType;

void EcuM_Init(void);          /* calls Bsw/App init chain, enters RUN */
void EcuM_MainFunction(void);  /* drives state transitions */
EcuM_StateType EcuM_GetState(void);

#endif /* ECUM_H */
