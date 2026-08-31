#include "ComM.h"

#define COMM_MAX_CHANNELS 1u

static ComM_ModeType s_channelState[COMM_MAX_CHANNELS] = { COMM_NO_COMMUNICATION };

void ComM_Init(void)
{
    for (uint8_t i = 0u; i < COMM_MAX_CHANNELS; i++) {
        s_channelState[i] = COMM_NO_COMMUNICATION;
    }
}

Std_ReturnType ComM_RequestComMode(uint8_t channel, ComM_ModeType mode)
{
    if (channel >= COMM_MAX_CHANNELS) {
        return E_NOT_OK;
    }
    /* POC: single requester, no vote counting — full impl needs per-user refcount */
    s_channelState[channel] = mode;
    return E_OK;
}

ComM_ModeType ComM_GetState(uint8_t channel)
{
    if (channel >= COMM_MAX_CHANNELS) {
        return COMM_NO_COMMUNICATION;
    }
    return s_channelState[channel];
}
