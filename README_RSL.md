# Road Speed Limiter (RSL), GEAR D

New limiter that holds a constant speed at the limit, even at full throttle.
It replaces Chart `<S4>/Chart` (Idle / SoftLanding / PIDGoverning) in
`Torque_Control.c`.

## Why the old chart oscillated / sat below the limit

* **SoftLanding** set torque from speed alone, `((L+2−v)/D)²·1100`. It has
  no integral, so the vehicle settles where that curve equals road load,
  which is always below L. PIDGoverning is only entered at `v ≥ L`, so it
  never takes over. That gave the ~59 km/h hold seen in the log.
* `TrqSoftDelta` is not updated when `|target − TrqUBound| < SMax`, so the
  last ±SMax step is reused and the limit overshoots and swings back.
* PIDGoverning added `Kp·e + ΣKi·e` to `TrqUBound` every step. That turns P
  into an integral and I into a double integral, which oscillates. The
  integral was also never reset.
* Exiting to Idle at `L − ReleaseDelta` gave back full pedal torque, so the
  vehicle accelerated back to the limit.

## How the new limiter works (`RoadSpeedLimiter.c`)

| State (`RslState`) | When | Torque limit |
|---|---|---|
| 0 OFF | `v < L − EngBand`, or `L ≤ LimitMin` (not received) | driver torque |
| 1 ARMED | in band, driver asks less than the limiter allows | driver torque, PI tracks it (no jump at engage) |
| 2 LIMITING | in band, PI output below driver demand | `Kp·e + I`, `e = vRef − v` |

* `vRef` ramps from the current speed to L at `RefRate`, so the vehicle
  eases onto the limit.
* The integral learns road load (slope, wind, mass), so speed settles on L.
* Output is clamped to `[MinTrq, DrvTrq]` and slew limited. The integrator
  uses back-calculation, so there is no wind-up (uphill it simply hands
  back full torque).
* Downhill it regens down to `MinTrq = −min(BrakeAllow, SlideAllow, maxRslRegenTrq)`.

## Changes in `Torque_Control.c`

* `#include "RoadSpeedLimiter.h"`
* `static RSL_State_T Torque_Control_RSL;` and `RSL_Init()` in `Torque_Control_initialize()`
* The `<S4>/Chart` block in `Torque_Control_step1()` is replaced by one `RSL_Step()` call.
  Everything else (Max1, Switch9 `fmin(TrqUBound, Check_D_DriveTorque)`) is unchanged.
* No header change is needed. Existing outports are reused for logging:

| Outport | Now means |
|---|---|
| `RslState` | 0 off, 1 armed, 2 limiting |
| `Rsl_PCont` | P term [Nm] |
| `Rsl_ICont` | I term [Nm] |
| `Rsl_Pid_TrqDlta` | speed error `vRef − v` [km/h] |
| `TrqSoftDelta` | speed reference `vRef` [km/h] |

Inports `Rsl_Kp, Rsl_ki, Rsl_ICont_Max, Rsl_DltaSoftDiff, Rsl_ReleaseDelta,
Rsl_Trq_diff_SMax, Rsl_Trq_diff_PIMax` are no longer used.
Add `RoadSpeedLimiter.c` to the build.

## Calibration (exported globals in `RoadSpeedLimiter.c`)

| Name | Default | Unit | Effect |
|---|---|---|---|
| `RSL_Kp` | 400 | Nm per km/h | higher = tighter hold, more sensitive to noise |
| `RSL_Ki` | 80 | Nm per km/h per s | removes steady error; too high = slow swing |
| `RSL_EngBand` | 5 | km/h | limiter armed from `L − EngBand` |
| `RSL_RefRate` | 0.5 | km/h per s | approach rate to L; lower = less overshoot |
| `RSL_TrqRate` | 25 | Nm per 0.05 s | slew limit of the torque limit |
| `RSL_LimitMin` | 5 | km/h | limits ≤ this are treated as "no limit" |

Starting gains from vehicle data:

```
Kacc = m·1.06·r / (3.6·i·η)    Nm per (km/h/s)   (≈ 460 for 18 t, r 0.5, i 6.3, η 0.92)
Kp   ≈ Kacc · 0.9              (crossover ≈ 0.9 rad/s)
Ki   ≈ Kp · 0.2
```

### Tuning on the vehicle (flat road, full throttle)
1. Log `TQ_TEMP_sVeilSpd`, FrontAxleSpeed, `RslState`, `TrqUBound`,
   `Rsl_PCont`, `Rsl_ICont`, `TrqSoftDelta`, `TQ_OUT_sVCUTorqCmd`.
2. Check first that `TQ_TEMP_sVeilSpd` matches the axle speed (tyre radius / ratio).
3. Oscillation with a period < 3 s: lower `RSL_Kp`. Slow swing (> 5 s): lower `RSL_Ki`.
4. Overshoot on arrival: lower `RSL_RefRate` or raise `RSL_EngBand`.
5. Constant offset below L that does not go away: raise `RSL_Ki`.

## PC simulation (`test/rsl_sim.c`)

Closed loop with a simple vehicle model (assumed 18 t bus; edit the
`#define`s at the top), the 0.25 s speed filter, the rate-transition
delay, the downstream torque rate limiter and the motor lag.

```
gcc -std=c99 -O2 -Wall -Itest -I. test/rsl_sim.c RoadSpeedLimiter.c -lm -o rsl_sim
./rsl_sim                         # new limiter, summary
./rsl_sim new csv > new.csv       # full trace for plotting
./rsl_sim new sum 300 50 5 0.5    # try Kp Ki EngBand RefRate
./rsl_sim old                     # old chart (edit old_* calibration first)
gcc ... -DVEH_MASS=26000 ...      # other mass; also -DRATIO=, -DSPD_NOISE=
```

Result with the defaults (speed error v − L in km/h):

```
first approach overshoot above 60: +0.58 km/h
section                mean err    min err    max err  peak-peak
flat, settled             +0.04      -0.01      +0.47       0.47
uphill 3%                 -0.03      -0.14      +0.00       0.15
downhill 3%               +0.09      -0.01      +0.47       0.47
flat after re-press       -0.00      -0.02      +0.01       0.02
limit 60 -> 50            +0.12      -0.47      +2.41       2.88   (ramps down at RefRate)
```

Stable from 12 t to 26 t. With the assumed motor and 300 Nm regen at 26 t, the
vehicle can't hold 60 on a 3 % grade: that is a torque limit, not the
controller.

The `old` mode is a 1:1 port of the old chart, but its calibration values
are guesses. Put in the real `Rsl_*` values to reproduce the field behaviour.

## Moving it into Simulink

Replace `<S4>/Chart` with a **MATLAB Function** block (inputs
`v = TmpRTB..._p`, `L = CAL_sDVeilSpdLimit`, `DrvTrq = Check_D_DriveTorque`,
`MinTrq = -min(min(BrakeAllow, SlideAllow), abs(maxRslRegenTrq))`, output
`TrqUBound` into `<S4>/Max1`). Set all data to `single`, sample time 0.05.
Make the `RSL_*` values tunable parameters (Simulink.Parameter, ExportedGlobal).

```matlab
function [TrqUBound, RslState, P, I_out, e_out, vRef_out] = ...
         RoadSpeedLimiter(v, L, DrvTrq, MinTrq, ...
                          RSL_Kp, RSL_Ki, RSL_EngBand, RSL_RefRate, RSL_TrqRate, RSL_LimitMin)
%#codegen
Ts = single(0.05);
persistent vRef I Tprev
if isempty(vRef)
    vRef = single(0); I = single(0); Tprev = single(0);
end

MinTrq = min(MinTrq, DrvTrq);
P = single(0); e = single(0);

if ~(L > RSL_LimitMin) || (v < L - RSL_EngBand)
    RslState = uint8(0);                         % OFF
    vRef = v; I = DrvTrq; T = DrvTrq;
else
    stp  = RSL_RefRate * Ts;
    vRef = vRef + min(max(L - vRef, -stp), stp);
    e = vRef - v;
    P = RSL_Kp * e;
    u = P + I + RSL_Ki * Ts * e;
    if u >= DrvTrq
        RslState = uint8(1);                     % ARMED
        T = DrvTrq;
        vRef = min(v, L);
        e = vRef - v;
        P = RSL_Kp * e;
        I = DrvTrq - P;
    else
        RslState = uint8(2);                     % LIMITING
        T = min(max(u, Tprev - RSL_TrqRate), Tprev + RSL_TrqRate);
        T = min(max(T, MinTrq), DrvTrq);
        I = I + RSL_Ki * Ts * e + (T - u);       % back-calculation anti-windup
    end
end

Tprev = T;
TrqUBound = T;
I_out = I; e_out = e; vRef_out = vRef;
end
```

Before flashing, run the same scenario in Simulink (or swap the
generated function into `test/rsl_sim.c` in place of `RSL_Step`) and check
the results match the table above.
