#include "EcuM.h"
#include "../ComM/ComM.h"
#include "../../Communication/CanIf/CanIf.h"
#include "../../Communication/PduR/PduR.h"
#include "../../Communication/Com/Com.h"

static EcuM_StateType s_state = ECUM_STATE_STARTUP;

void EcuM_Init(void)
{
    /* TODO: Mcal init (clock/pins) first, once Mcal/ is vendored */
    CanIf_Init();
    PduR_Init();
    Com_Init();
    ComM_Init();
    s_state = ECUM_STATE_RUN;
}

void EcuM_MainFunction(void)
{
    /* TODO: state transition logic (RUN -> SLEEP on request, wake sources) */
}

EcuM_StateType EcuM_GetState(void)
{
    return s_state;
}
