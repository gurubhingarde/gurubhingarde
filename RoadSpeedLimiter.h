/*
 * File: RoadSpeedLimiter.h
 *
 * Road speed limiter (RSL) for GEAR D, full-throttle constant speed hold.
 * Replaces Chart '<S4>/Chart' (Idle / SoftLanding / PIDGoverning).
 *
 * Called every 0.05 s from Torque_Control_step1().
 */

#ifndef RoadSpeedLimiter_h_
#define RoadSpeedLimiter_h_

#include "rtwtypes.h"

/* Limiter state, reported on Outport RslState */
#define RSL_STATE_OFF       ((uint8_T)0U)   /* speed below L - EngBand, driver torque passes  */
#define RSL_STATE_ARMED     ((uint8_T)1U)   /* inside band, driver asks less than limiter      */
#define RSL_STATE_LIMITING  ((uint8_T)2U)   /* limiter is cutting driver torque                */

/* Sample time of the calling task [s] */
#define RSL_TS              (0.05F)

/* Persistent state of one limiter instance */
typedef struct {
  real32_T vRef;     /* speed reference, ramps toward the limit   [km/h] */
  real32_T I;        /* PI integrator                             [Nm]   */
  real32_T Tprev;    /* last torque limit output                  [Nm]   */
  real32_T e;        /* last speed error (vRef - v), for logging  [km/h] */
  real32_T P;        /* last proportional term, for logging       [Nm]   */
  uint8_T  state;    /* RSL_STATE_xxx                                    */
} RSL_State_T;

/* Calibration parameters (exported, tune via calibration tool) */
extern real32_T RSL_Kp;        /* proportional gain              [Nm per km/h]      */
extern real32_T RSL_Ki;        /* integral gain                  [Nm per km/h per s] */
extern real32_T RSL_EngBand;   /* limiter armed at L - EngBand   [km/h]             */
extern real32_T RSL_RefRate;   /* speed reference ramp rate      [km/h per s]       */
extern real32_T RSL_TrqRate;   /* max change of limit per step   [Nm per 0.05 s]    */
extern real32_T RSL_LimitMin;  /* limits at or below this = off  [km/h]             */

extern void RSL_Init(RSL_State_T *s);

/*
 * v      : vehicle speed used for control (filtered)          [km/h]
 * L      : speed limit (CAL_sDVeilSpdLimit)                    [km/h]
 * DrvTrq : driver drive torque demand (Check_D_DriveTorque)    [Nm, >= 0]
 * MinTrq : lowest allowed torque, i.e. max regen               [Nm, <= 0]
 * return : torque upper bound for the drive path               [Nm]
 */
extern real32_T RSL_Step(RSL_State_T *s, real32_T v, real32_T L,
  real32_T DrvTrq, real32_T MinTrq);

#endif                                 /* RoadSpeedLimiter_h_ */
