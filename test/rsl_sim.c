/*
 * rsl_sim.c - PC closed-loop test of the road speed limiter
 *
 * Runs the new RoadSpeedLimiter (RoadSpeedLimiter.c) and a port of the old
 * Chart '<S4>/Chart' against the same simple vehicle model, at full throttle,
 * and prints the speed-hold quality for each road section.
 *
 * Signal path modelled (same as Torque_Control.c, 0.05 s steps):
 *   speed -> first-order filter (tau 0.25 s, S114/S120) -> limiter
 *   limiter -> fmin(TrqUBound, DrvTrq) -> 1-step rate transition
 *   -> torque rate limiter (S111: +24 / -48 Nm per step) -> 1-step CAN
 *   -> motor lag (tau 0.02 s) -> vehicle
 *
 * Build & run (from repo root):
 *   gcc -std=c99 -O2 -Wall -Itest -I. test/rsl_sim.c RoadSpeedLimiter.c -lm -o rsl_sim
 *   ./rsl_sim            new limiter, summary
 *   ./rsl_sim old        old chart, summary
 *   ./rsl_sim new csv    new limiter, CSV trace on stdout
 *   ./rsl_sim new sum Kp Ki EngBand RefRate   try other calibration
 *
 * Vehicle data below are ASSUMPTIONS (18 t bus). Put in your real values.
 */

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "RoadSpeedLimiter.h"

/* ---------------- vehicle (assumed, edit these) ---------------- */
#ifndef VEH_MASS
#define VEH_MASS 18000.0      /* kg                                   */
#endif
#define VEH_MEFF      1.06         /* rotating mass factor                 */
#define TYRE_R        0.5          /* m                                    */
#ifndef RATIO
#define RATIO 6.3          /* motor to wheel                       */
#endif
#define ETA           0.92         /* driveline efficiency                 */
#define C_ROLL        0.008
#define CDA           6.5          /* Cd * A  [m^2]                        */
#define RHO           1.2
#define PEAK_POWER_KW 200.0
#define MAX_REGEN_NM  300.0        /* -min(BrakeAllow, SlideAllow)         */

/* downstream torque rate limiter (GearD_ForwardGain_Z / Drop_Z * 0.05) */
#define RATE_UP_NM    24.0
#define RATE_DN_NM    48.0

#ifndef SPD_NOISE
#define SPD_NOISE     0.1          /* speed signal noise, peak-peak [km/h] */
#endif

#define TS            0.05
#define SUBSTEPS      10

/* tables copied from Torque_Control.c */
static const float MotorSpeed_X[17] = { 200, 400, 600, 800, 1000, 1200, 1400,
  1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 4000 };
static const float MotorTorqueUpper_Y[17] = { 3340, 3290, 3056, 2822, 2162,
  1720, 1414, 1208, 1015, 894, 792, 697, 607, 570, 500, 500, 500 };
static const float AccelPert[5] = { 0.0F, 0.05F, 0.4F, 0.7F, 1.0F };
static const float Torque_AccelPert[5] = { 0.0F, 0.0F, 0.4F, 0.56F, 1.0F };

static float interp(float x, const float *bx, const float *by, int n)
{
  int i;
  if (x <= bx[0]) return by[0];
  if (x >= bx[n - 1]) return by[n - 1];
  for (i = 0; i < n - 1; i++) {
    if (x < bx[i + 1]) {
      return by[i] + (by[i + 1] - by[i]) * (x - bx[i]) / (bx[i + 1] - bx[i]);
    }
  }
  return by[n - 1];
}

/* deterministic noise, so every run is identical */
static unsigned int rng = 12345U;
static double noise(void)
{
  rng = rng * 1103515245U + 12345U;
  return ((rng >> 16) & 0x7FFF) / 32767.0 - 0.5;   /* -0.5 .. 0.5 */
}

/* ---------------- old Chart '<S4>/Chart' (ported 1:1) ---------------- */
/* Old calibration is unknown: these are GUESSES, edit to your values */
static double old_DltaSoftDiff = 5.0, old_ReleaseDelta = 2.0;
static double old_SMax = 50.0, old_PIMax = 50.0;
static double old_Kp = 5.0, old_ki = 0.5, old_ICont_Max = 50.0;

static struct {
  int active, st;           /* st: 0 Idle, 1 SoftLanding, 2 PIDGoverning */
  double TrqUBound, TqSoftMax, SoftDelta, ICont;
} oc;

static double old_chart(double v, double L, double DrvTrq)
{
  double e, tgt, diff, P;
  if (!oc.active) { oc.active = 1; oc.st = 0; return oc.TrqUBound; }
  switch (oc.st) {
   case 0:
    if (L - v <= old_DltaSoftDiff) { oc.st = 1; oc.TqSoftMax = 1100; oc.TrqUBound = 1100; }
    else oc.TrqUBound = DrvTrq;
    break;
   case 2:
    e = L - v;
    if (e >= old_ReleaseDelta) { oc.st = 0; break; }
    P = old_Kp * e;
    if (e < 2.0) oc.ICont += old_ki * e;
    oc.ICont = fmin(fmax(oc.ICont, 0.0), old_ICont_Max);
    oc.TrqUBound += fmax(P + oc.ICont, -old_PIMax);
    oc.TrqUBound = fmin(fmax(oc.TrqUBound, -MAX_REGEN_NM), 900.0);
    break;
   default:
    if (L <= v) { oc.st = 2; break; }
    if (L - v >= old_ReleaseDelta) { oc.st = 0; break; }
    tgt = (L + 2.0 - v); tgt = tgt * tgt / (old_DltaSoftDiff * old_DltaSoftDiff) * oc.TqSoftMax;
    diff = tgt - oc.TrqUBound;
    if (diff <= -old_SMax) oc.SoftDelta = -old_SMax;
    else if (diff >= old_SMax) oc.SoftDelta = old_SMax;     /* else: stale (bug) */
    oc.TrqUBound += oc.SoftDelta;
    if (oc.SoftDelta < 0 && oc.SoftDelta < tgt) oc.TrqUBound = fmax(oc.TrqUBound, tgt);
    if (oc.SoftDelta > 0 && oc.SoftDelta > tgt) oc.TrqUBound = fmin(oc.TrqUBound, tgt);
    break;
  }
  return oc.TrqUBound;
}

/* ---------------- scenario ---------------- */
static double grade_at(double t)          /* road slope [-] */
{
  if (t >= 60.0 && t < 90.0) return 0.03;   /* uphill 3 %   */
  if (t >= 90.0 && t < 120.0) return -0.03; /* downhill 3 % */
  return 0.0;
}
static double pedal_at(double t)          /* pedal 0..1 */
{
  static const double jit[4] = { 0.988, 0.992, 0.996, 1.0 };  /* like your log */
  if (t >= 130.0 && t < 140.0) return 0.30;                  /* part lift     */
  return jit[(int)(t / TS) % 4];
}
static double limit_at(double t)          /* CAL_sDVeilSpdLimit */
{
  return (t >= 160.0) ? 50.0 : 60.0;
}

typedef struct { const char *name; double t0, t1; } Window;
static const Window win[] = {
  { "flat, settled      ", 20.0, 60.0 },
  { "uphill 3%         ", 70.0, 90.0 },
  { "downhill 3%       ", 100.0, 120.0 },
  { "flat after re-press", 145.0, 160.0 },
  { "limit 60 -> 50     ", 175.0, 200.0 },
};
#define NWIN ((int)(sizeof(win) / sizeof(win[0])))

int main(int argc, char **argv)
{
  int useOld = (argc > 1 && strcmp(argv[1], "old") == 0);
  int csv = (argc > 2 && strcmp(argv[2], "csv") == 0);
  RSL_State_T rsl;
  double v = 45.0 / 3.6;                   /* m/s, start at 45 km/h */
  double vFilt = 45.0;                     /* km/h                  */
  double cmdRT = 0, cmdRL = 0, cmdCAN = 0, Tmot = 0;
  double sum[NWIN] = { 0 }, mx[NWIN], mn[NWIN];
  int cnt[NWIN] = { 0 };
  double overshoot1 = 0;
  int k, w, j;

  if (argc > 6) {
    sscanf(argv[3], "%f", &RSL_Kp);
    sscanf(argv[4], "%f", &RSL_Ki);
    sscanf(argv[5], "%f", &RSL_EngBand);
    sscanf(argv[6], "%f", &RSL_RefRate);
  }

  for (w = 0; w < NWIN; w++) { mx[w] = -1e9; mn[w] = 1e9; }
  RSL_Init(&rsl);
  memset(&oc, 0, sizeof(oc));

  if (csv) printf("t,v_kmh,v_filt,limit,drv_trq,trq_ubound,motor_trq,state,vref,grade\n");

  for (k = 0; k < (int)(200.0 / TS); k++) {
    double t = k * TS;
    double vk = v * 3.6;
    double L = limit_at(t);
    double n = v / TYRE_R * RATIO * 60.0 / (2.0 * 3.14159265358979);
    double avail, drv, minTrq, ub, out;
    int state;

    /* driver demand at the pedal (Check_D_DriveTorque) */
    avail = fmin(interp((float)n, MotorSpeed_X, MotorTorqueUpper_Y, 17),
                 9550.0 * PEAK_POWER_KW / fmax(n, 200.0));
    drv = avail * interp((float)pedal_at(t), AccelPert, Torque_AccelPert, 5);
    minTrq = -MAX_REGEN_NM;

    /* limiter (step1) */
    if (useOld) {
      ub = fmax(minTrq, old_chart(vFilt, L, drv));
      state = oc.st;
    } else {
      ub = RSL_Step(&rsl, (float)vFilt, (float)L, (float)drv, (float)minTrq);
      ub = fmax(minTrq, ub);              /* MinMax '<S4>/Max1' */
      state = rsl.state;
    }
    out = fmin(ub, drv);                  /* TQ_DOUT1, DS_JudgeFlg branch */

    /* step0: uses last step1 output, then rate limiter, then CAN */
    cmdCAN = cmdRL;
    if (cmdRT > cmdRL + RATE_UP_NM) cmdRL += RATE_UP_NM;
    else if (cmdRT < cmdRL - RATE_DN_NM) cmdRL -= RATE_DN_NM;
    else cmdRL = cmdRT;
    cmdRT = out;

    /* vehicle */
    for (j = 0; j < SUBSTEPS; j++) {
      double dt = TS / SUBSTEPS, th = atan(grade_at(t));
      double Fw, Fr;
      Tmot += (cmdCAN - Tmot) * dt / 0.02;
      Fw = Tmot * RATIO * (Tmot >= 0 ? ETA : 1.0 / ETA) / TYRE_R;
      Fr = VEH_MASS * 9.81 * (C_ROLL * cos(th) + sin(th)) + 0.5 * RHO * CDA * v * v;
      v += (Fw - Fr) / (VEH_MASS * VEH_MEFF) * dt;
      if (v < 0) v = 0;
    }

    /* speed measurement + S114/S120 filter (tau 0.25 s) */
    vFilt += TS / 0.25 * (v * 3.6 + SPD_NOISE * noise() - vFilt);

    if (csv) {
      printf("%.2f,%.3f,%.3f,%.1f,%.1f,%.1f,%.1f,%d,%.3f,%.3f\n", t, vk, vFilt,
             L, drv, ub, Tmot, state, useOld ? 0.0 : rsl.vRef, grade_at(t));
    }

    if (t < 60.0 && vk - 60.0 > overshoot1) overshoot1 = vk - 60.0;
    for (w = 0; w < NWIN; w++) {
      if (t >= win[w].t0 && t < win[w].t1) {
        double e = vk - L;
        sum[w] += e; cnt[w]++;
        if (e > mx[w]) mx[w] = e;
        if (e < mn[w]) mn[w] = e;
      }
    }
  }

  if (!csv) {
    printf("%s limiter, full throttle, limit 60 km/h (50 from t=160 s)\n",
           useOld ? "OLD chart" : "NEW");
    printf("  first approach overshoot above 60: %+.2f km/h\n", overshoot1);
    printf("  %-20s %10s %10s %10s %10s\n", "section", "mean err", "min err",
           "max err", "peak-peak");
    for (w = 0; w < NWIN; w++) {
      printf("  %-20s %+10.2f %+10.2f %+10.2f %10.2f\n", win[w].name,
             sum[w] / cnt[w], mn[w], mx[w], mx[w] - mn[w]);
    }
  }
  return 0;
}
