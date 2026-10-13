/*
 * File: RoadSpeedLimiter.c
 *
 * Road speed limiter (RSL) for GEAR D, full-throttle constant speed hold.
 * Replaces Chart '<S4>/Chart' (Idle / SoftLanding / PIDGoverning).
 *
 * How it works
 *   OFF       : v < L - EngBand. Driver torque passes, reference follows v.
 *   ARMED     : inside the band, but the driver asks for less torque than the
 *               limiter would allow. Driver torque passes; reference and
 *               integrator track so that limiting starts without a jump.
 *   LIMITING  : PI controller on (vRef - v) sets the torque upper bound.
 *               vRef ramps from the current speed to L at RefRate, so the
 *               vehicle eases onto the limit instead of overshooting.
 *               The integrator learns the road load, so speed settles on L.
 *
 * Anti-windup: output is clamped to [MinTrq, DrvTrq] and slew limited; the
 * integrator is back-calculated so P + I always equals the applied limit.
 */

#include "RoadSpeedLimiter.h"
#include <math.h>

/* Calibration parameters (starting values, see README_RSL.md for tuning) */
real32_T RSL_Kp = 400.0F;       /* [Nm per km/h]        */
real32_T RSL_Ki = 80.0F;        /* [Nm per km/h per s]  */
real32_T RSL_EngBand = 5.0F;    /* [km/h]               */
real32_T RSL_RefRate = 0.5F;    /* [km/h per s]         */
real32_T RSL_TrqRate = 25.0F;   /* [Nm per 0.05 s]      */
real32_T RSL_LimitMin = 5.0F;   /* [km/h]               */

void RSL_Init(RSL_State_T *s)
{
  s->vRef = 0.0F;
  s->I = 0.0F;
  s->Tprev = 0.0F;
  s->e = 0.0F;
  s->P = 0.0F;
  s->state = RSL_STATE_OFF;
}

real32_T RSL_Step(RSL_State_T *s, real32_T v, real32_T L, real32_T DrvTrq,
                  real32_T MinTrq)
{
  real32_T T;
  real32_T u;
  real32_T d;
  real32_T stp;

  /* MinTrq must never be above the driver demand */
  if (MinTrq > DrvTrq) {
    MinTrq = DrvTrq;
  }

  if ((!(L > RSL_LimitMin)) || (v < L - RSL_EngBand)) {
    /* OFF: limit invalid / not received, or far below the limit */
    s->state = RSL_STATE_OFF;
    s->vRef = v;
    s->I = DrvTrq;
    s->e = 0.0F;
    s->P = 0.0F;
    T = DrvTrq;
  } else {
    /* Reference moves toward L at RefRate (also follows a changed L) */
    stp = RSL_RefRate * RSL_TS;
    d = L - s->vRef;
    if (d > stp) {
      d = stp;
    } else if (d < -stp) {
      d = -stp;
    }

    s->vRef += d;
    s->e = s->vRef - v;
    s->P = RSL_Kp * s->e;
    u = s->P + s->I + RSL_Ki * RSL_TS * s->e;

    if (u >= DrvTrq) {
      /* ARMED: driver asks less than the limiter allows -> pass driver torque.
       * Track so that the next limiting step starts from DrvTrq (bumpless). */
      s->state = RSL_STATE_ARMED;
      T = DrvTrq;
      s->vRef = fminf(v, L);
      s->e = s->vRef - v;
      s->P = RSL_Kp * s->e;
      s->I = DrvTrq - s->P;
    } else {
      /* LIMITING */
      s->state = RSL_STATE_LIMITING;
      T = u;

      /* slew limit, then hard bounds [MinTrq, DrvTrq] (bounds win) */
      if (T > s->Tprev + RSL_TrqRate) {
        T = s->Tprev + RSL_TrqRate;
      } else if (T < s->Tprev - RSL_TrqRate) {
        T = s->Tprev - RSL_TrqRate;
      }

      T = fminf(fmaxf(T, MinTrq), DrvTrq);

      /* integrate, with back-calculation so that P + I == T */
      s->I += RSL_Ki * RSL_TS * s->e + (T - u);
    }
  }

  s->Tprev = T;
  return T;
}
