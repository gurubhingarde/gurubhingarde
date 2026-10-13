/*
 * File: Torque_Control.c
 *
 * Code generated for Simulink model 'Torque_Control'.
 *
 * Model version                  : 3.47
 * Simulink Coder version         : 25.2 (R2025b) 28-Jul-2025
 * C/C++ source code generated on : Tue Sep  8 09:56:49 2026
 *
 * Target selection: ert.tlc
 * Embedded hardware selection: NXP->Cortex-M4
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#include "Torque_Control.h"
#include "rtwtypes.h"
#include <math.h>
#include <string.h>
#include "Torque_Control_private.h"
#include "RoadSpeedLimiter.h"

/* Named constants for Chart: '<S4>/Chart' */
#define Torque_Contr_IN_NO_ACTIVE_CHILD ((uint8_T)0U)
#define Torque_Control_IN_Idle         ((uint8_T)1U)
#define Torque_Control_IN_PIDGoverning ((uint8_T)2U)
#define Torque_Control_IN_SoftLanding  ((uint8_T)3U)

/* Named constants for Chart: '<S18>/Chart' */
#define Torque_Contro_IN_R_Judge_Creep1 ((uint8_T)2U)
#define Torque_Contro_IN_R_Judge_Creep2 ((uint8_T)3U)
#define Torque_Contro_IN_R_Judge_Creep3 ((uint8_T)4U)
#define Torque_Control_IN_R_Judge_Creep ((uint8_T)1U)

/* Named constants for Chart: '<S19>/Chart1' */
#define Torque_Control_IN_OFF          ((uint8_T)1U)
#define Torque_Control_IN_OFFLAST      ((uint8_T)2U)
#define Torque_Control_IN_ON           ((uint8_T)3U)

/* Named constants for Chart: '<S19>/Chart2' */
#define Torque_Control_IN_STEP1        ((uint8_T)1U)
#define Torque_Control_IN_STEP2        ((uint8_T)2U)
#define Torque_Control_IN_STEP3        ((uint8_T)3U)
#define Torque_Control_IN_STEP4        ((uint8_T)4U)

/* Exported block parameters */
real32_T AccelPert[5] = { 0.0F, 0.05F, 0.4F, 0.7F, 1.0F } ;/* Variable: AccelPert
                                                            * Referenced by: '<S6>/Torque_AccelPert3'
                                                            */

real32_T AccelPert1[4] = { 0.0F, 0.05F, 0.7F, 1.0F } ;/* Variable: AccelPert1
                                                       * Referenced by: '<S6>/Torque_AccelPert1'
                                                       */

real32_T AccelPert2[4] = { 0.0F, 0.05F, 0.7F, 1.0F } ;/* Variable: AccelPert2
                                                       * Referenced by: '<S6>/Torque_AccelPert2'
                                                       */

real32_T BMSSOC[4] = { 0.0F, 0.5F, 3.0F, 5.0F } ;/* Variable: BMSSOC
                                                  * Referenced by: '<S10>/BMSSOC_LimitK'
                                                  */

real32_T BMSSOCLimitK[4] = { 0.0F, 0.0F, 1.0F, 1.0F } ;/* Variable: BMSSOCLimitK
                                                        * Referenced by: '<S10>/BMSSOC_LimitK'
                                                        */

real32_T BrakePert[4] = { 0.0F, 0.05F, 0.35F, 1.0F } ;/* Variable: BrakePert
                                                       * Referenced by: '<S6>/Torque_BrakePert'
                                                       */

real32_T DVeilSpd_CrawlTorque[8] = { 500.0F, 500.0F, 400.0F, 300.0F, 200.0F,
  100.0F, 0.0F, 0.0F } ;               /* Variable: DVeilSpd_CrawlTorque
                                        * Referenced by: '<S4>/DVeilSpd_CrawlTorque'
                                        */

real32_T EcoMode_AccelPert[4] = { 0.0F, 0.0F, 0.52F, 1.0F } ;/* Variable: EcoMode_AccelPert
                                                              * Referenced by: '<S6>/Torque_AccelPert2'
                                                              */

real32_T GearD2_VeilSpd[8] = { 0.0F, 1.0F, 2.0F, 3.0F, 4.0F, 5.0F, 6.0F, 7.0F } ;/* Variable: GearD2_VeilSpd
                                                                      * Referenced by: '<S4>/DVeilSpd_CrawlTorque'
                                                                      */

real32_T GearD_ForwardDrop_Y[8] = { -1200.0F, -1200.0F, -1040.0F, -1120.0F,
  -960.0F, -960.0F, -880.0F, -800.0F } ;/* Variable: GearD_ForwardDrop_Y
                                         * Referenced by: '<S8>/GearD_SpdForwardDown'
                                         */

real32_T GearD_ForwardDrop_Z[8] = { -600.0F, -600.0F, -600.0F, -1120.0F, -960.0F,
  -960.0F, -880.0F, -800.0F } ;        /* Variable: GearD_ForwardDrop_Z
                                        * Referenced by: '<S9>/GearD_TorqForwardDown'
                                        */

real32_T GearD_ForwardGain_Y[8] = { 600.0F, 600.0F, 520.0F, 560.0F, 480.0F,
  480.0F, 440.0F, 400.0F } ;           /* Variable: GearD_ForwardGain_Y
                                        * Referenced by: '<S8>/GearD_SpdForwardUp'
                                        */

real32_T GearD_ForwardGain_Z[8] = { 400.0F, 400.0F, 400.0F, 560.0F, 480.0F,
  480.0F, 440.0F, 400.0F } ;           /* Variable: GearD_ForwardGain_Z
                                        * Referenced by: '<S9>/GearD_TorqForwardUp'
                                        */

real32_T GearD_ForwardMotSpd_X[8] = { -100.0F, -50.0F, 0.0F, 100.0F, 200.0F,
  2000.0F, 2200.0F, 2400.0F } ;        /* Variable: GearD_ForwardMotSpd_X
                                        * Referenced by: '<S8>/GearD_SpdForwardUp'
                                        */

real32_T GearD_ForwardMotSpd_X1[8] = { -100.0F, -50.0F, 0.0F, 100.0F, 200.0F,
  2000.0F, 2200.0F, 2400.0F } ;        /* Variable: GearD_ForwardMotSpd_X1
                                        * Referenced by: '<S8>/GearD_SpdForwardDown'
                                        */

real32_T GearD_ForwardMotTorq_X[8] = { -100.0F, -50.0F, 0.0F, 100.0F, 200.0F,
  2000.0F, 2200.0F, 2400.0F } ;        /* Variable: GearD_ForwardMotTorq_X
                                        * Referenced by: '<S9>/GearD_TorqForwardUp'
                                        */

real32_T GearD_ForwardMotTorq_X1[8] = { -100.0F, -50.0F, 0.0F, 100.0F, 200.0F,
  2000.0F, 2200.0F, 2400.0F } ;        /* Variable: GearD_ForwardMotTorq_X1
                                        * Referenced by: '<S9>/GearD_TorqForwardDown'
                                        */

real32_T GearR_BackwardDrop_Y[7] = { -260.0F, -260.0F, -240.0F, -240.0F, -200.0F,
  -160.0F, -160.0F } ;                 /* Variable: GearR_BackwardDrop_Y
                                        * Referenced by: '<S8>/GearR_SpdBackwardDown'
                                        */

real32_T GearR_BackwardDrop_Z[7] = { -260.0F, -260.0F, -240.0F, -240.0F, -200.0F,
  -160.0F, -160.0F } ;                 /* Variable: GearR_BackwardDrop_Z
                                        * Referenced by: '<S9>/GearR_TorqBackwardDown'
                                        */

real32_T GearR_BackwardGain_Y[7] = { 520.0F, 520.0F, 480.0F, 480.0F, 400.0F,
  320.0F, 320.0F } ;                   /* Variable: GearR_BackwardGain_Y
                                        * Referenced by: '<S8>/GearR_SpdBackwardUp'
                                        */

real32_T GearR_BackwardGain_Z[7] = { 520.0F, 520.0F, 480.0F, 480.0F, 400.0F,
  320.0F, 320.0F } ;                   /* Variable: GearR_BackwardGain_Z
                                        * Referenced by: '<S9>/GearR_TorqBackwardUp'
                                        */

real32_T GearR_BackwardMotSpd_X[7] = { -2000.0F, -1000.0F, -300.0F, -100.0F,
  0.0F, 100.0F, 200.0F } ;             /* Variable: GearR_BackwardMotSpd_X
                                        * Referenced by: '<S8>/GearR_SpdBackwardUp'
                                        */

real32_T GearR_BackwardMotSpd_X1[7] = { -2000.0F, -1000.0F, -300.0F, -100.0F,
  0.0F, 100.0F, 200.0F } ;             /* Variable: GearR_BackwardMotSpd_X1
                                        * Referenced by: '<S8>/GearR_SpdBackwardDown'
                                        */

real32_T GearR_BackwardMotTorq_X[7] = { -2000.0F, -1000.0F, -300.0F, -100.0F,
  0.0F, 100.0F, 200.0F } ;             /* Variable: GearR_BackwardMotTorq_X
                                        * Referenced by: '<S9>/GearR_TorqBackwardUp'
                                        */

real32_T GearR_BackwardMotTorq_X1[7] = { -2000.0F, -1000.0F, -300.0F, -100.0F,
  0.0F, 100.0F, 200.0F } ;             /* Variable: GearR_BackwardMotTorq_X1
                                        * Referenced by: '<S9>/GearR_TorqBackwardDown'
                                        */

real32_T GearR_VeilSpd[8] = { 0.0F, 1.0F, 2.0F, 3.0F, 4.0F, 5.0F, 6.0F, 7.0F } ;/* Variable: GearR_VeilSpd
                                                                      * Referenced by: '<S5>/RVeilSpd_CrawlTorque'
                                                                      */

real32_T MCUTemp[4] = { 70.0F, 75.0F, 95.0F, 100.0F } ;/* Variable: MCUTemp
                                                        * Referenced by: '<S10>/MCUTemp_LimitK'
                                                        */

real32_T MCUTempLimitK[4] = { 1.0F, 1.0F, 0.0F, 0.0F } ;/* Variable: MCUTempLimitK
                                                         * Referenced by: '<S10>/MCUTemp_LimitK'
                                                         */

real32_T MotTemp[4] = { 125.0F, 160.0F, 175.0F, 180.0F } ;/* Variable: MotTemp
                                                           * Referenced by: '<S10>/MotTemp_LimitK'
                                                           */

real32_T MotTempLimitK[4] = { 1.0F, 1.0F, 0.0F, 0.0F } ;/* Variable: MotTempLimitK
                                                         * Referenced by: '<S10>/MotTemp_LimitK'
                                                         */

real32_T MotorChangeEfficiency_Z[17] = { 65.66F, 78.71F, 83.83F, 86.9F, 88.2F,
  87.51F, 87.97F, 89.69F, 89.63F, 89.65F, 89.16F, 89.5F, 89.5F, 89.5F, 89.5F,
  89.5F, 89.5F } ;                     /* Variable: MotorChangeEfficiency_Z
                                        * Referenced by: '<S3>/MotorChangeEfficiency'
                                        */

real32_T MotorSpeed_X[17] = { 200.0F, 400.0F, 600.0F, 800.0F, 1000.0F, 1200.0F,
  1400.0F, 1600.0F, 1800.0F, 2000.0F, 2200.0F, 2400.0F, 2600.0F, 2800.0F,
  3000.0F, 3200.0F, 4000.0F } ;        /* Variable: MotorSpeed_X
                                        * Referenced by:
                                        *   '<S3>/MotorChangeEfficiency'
                                        *   '<S3>/Speed_Torque'
                                        */

real32_T MotorTorqueUpper_Y[17] = { 3340.0F, 3290.0F, 3056.0F, 2822.0F, 2162.0F,
  1720.0F, 1414.0F, 1208.0F, 1015.0F, 894.0F, 792.0F, 697.0F, 607.0F, 570.0F,
  500.0F, 500.0F, 500.0F } ;           /* Variable: MotorTorqueUpper_Y
                                        * Referenced by: '<S3>/Speed_Torque'
                                        */

real32_T RVeilSpd_CrawlTorque[8] = { -500.0F, -500.0F, -400.0F, -300.0F, -200.0F,
  -100.0F, 0.0F, 0.0F } ;              /* Variable: RVeilSpd_CrawlTorque
                                        * Referenced by: '<S5>/RVeilSpd_CrawlTorque'
                                        */

real32_T SportMode_AccelPert[4] = { 0.0F, 0.0F, 0.88F, 1.0F } ;/* Variable: SportMode_AccelPert
                                                                * Referenced by: '<S6>/Torque_AccelPert1'
                                                                */

real32_T Torque_AccelPert[5] = { 0.0F, 0.0F, 0.4F, 0.56F, 1.0F } ;/* Variable: Torque_AccelPert
                                                                   * Referenced by: '<S6>/Torque_AccelPert3'
                                                                   */

real32_T Torque_BrakePert[4] = { 0.0F, 0.0F, 1.0F, 1.0F } ;/* Variable: Torque_BrakePert
                                                            * Referenced by: '<S6>/Torque_BrakePert'
                                                            */

real32_T VeilFltLvl[5] = { 0.0F, 1.0F, 2.0F, 3.0F, 4.0F } ;/* Variable: VeilFltLvl
                                                            * Referenced by: '<S10>/FaultLevel_LimitK'
                                                            */

real32_T VeilFltLvlLimitK[5] = { 1.0F, 1.0F, 0.5F, 0.0F, 0.0F } ;/* Variable: VeilFltLvlLimitK
                                                                  * Referenced by: '<S10>/FaultLevel_LimitK'
                                                                  */

/* Block signals (default storage) */
B_Torque_Control_T Torque_Control_B;

/* Block states (default storage) */
DW_Torque_Control_T Torque_Control_DW;

/* External inputs (root inport signals with default storage) */
ExtU_Torque_Control_T Torque_Control_U;

/* External outputs (root outports fed by signals with default storage) */
ExtY_Torque_Control_T Torque_Control_Y;

/* Road speed limiter state (replaces Chart '<S4>/Chart') */
static RSL_State_T Torque_Control_RSL;

/* Real-time model */
static RT_MODEL_Torque_Control_T Torque_Control_M_;
RT_MODEL_Torque_Control_T *const Torque_Control_M = &Torque_Control_M_;
real32_T Torque_Control_look1_i_k8T0tS4Z(real32_T u0, const real32_T bp0[],
  const real32_T table[], uint32_T maxIndex)
{
  real32_T frac;
  real32_T yL_0d0;
  uint32_T iLeft;

  /* Column-major Lookup 1-D
     Canonical function name: look1_iflf_binlcpw
     Search method: 'binary'
     Use previous index: 'off'
     Interpolation method: 'Linear point-slope'
     Extrapolation method: 'Clip'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  /* Prelookup - Index and Fraction
     Index Search method: 'binary'
     Extrapolation method: 'Clip'
     Use previous index: 'off'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  if (u0 <= bp0[0U]) {
    iLeft = 0U;
    frac = 0.0F;
  } else if (u0 < bp0[maxIndex]) {
    uint32_T bpIdx;
    uint32_T iRght;

    /* Binary Search */
    bpIdx = maxIndex >> 1U;
    iLeft = 0U;
    iRght = maxIndex;
    while (iRght - iLeft > 1U) {
      if (u0 < bp0[bpIdx]) {
        iRght = bpIdx;
      } else {
        iLeft = bpIdx;
      }

      bpIdx = (iRght + iLeft) >> 1U;
    }

    frac = (u0 - bp0[iLeft]) / (bp0[iLeft + 1U] - bp0[iLeft]);
  } else {
    iLeft = maxIndex - 1U;
    frac = 1.0F;
  }

  /* Column-major Interpolation 1-D
     Canonical function name: intrp1d_fu32fl_pw
     Interpolation method: 'Linear point-slope'
     Use last breakpoint for index at or above upper limit: 'off'
     Overflow mode: 'portable wrapping'
   */
  yL_0d0 = table[iLeft];
  return (table[iLeft + 1U] - yL_0d0) * frac + yL_0d0;
}

real32_T Torque_Control_look1_i_rQYGWmZ3(real32_T u0, const real32_T bp0[],
  const real32_T table[], uint32_T maxIndex)
{
  real32_T frac;
  real32_T yL_0d0;
  uint32_T iLeft;

  /* Column-major Lookup 1-D
     Canonical function name: look1_iflf_binlxpw
     Search method: 'binary'
     Use previous index: 'off'
     Interpolation method: 'Linear point-slope'
     Extrapolation method: 'Linear'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  /* Prelookup - Index and Fraction
     Index Search method: 'binary'
     Extrapolation method: 'Linear'
     Use previous index: 'off'
     Use last breakpoint for index at or above upper limit: 'off'
     Remove protection against out-of-range input in generated code: 'off'
   */
  if (u0 <= bp0[0U]) {
    iLeft = 0U;
    frac = (u0 - bp0[0U]) / (bp0[1U] - bp0[0U]);
  } else if (u0 < bp0[maxIndex]) {
    uint32_T bpIdx;
    uint32_T iRght;

    /* Binary Search */
    bpIdx = maxIndex >> 1U;
    iLeft = 0U;
    iRght = maxIndex;
    while (iRght - iLeft > 1U) {
      if (u0 < bp0[bpIdx]) {
        iRght = bpIdx;
      } else {
        iLeft = bpIdx;
      }

      bpIdx = (iRght + iLeft) >> 1U;
    }

    frac = (u0 - bp0[iLeft]) / (bp0[iLeft + 1U] - bp0[iLeft]);
  } else {
    iLeft = maxIndex - 1U;
    frac = (u0 - bp0[maxIndex - 1U]) / (bp0[maxIndex] - bp0[maxIndex - 1U]);
  }

  /* Column-major Interpolation 1-D
     Canonical function name: intrp1d_fu32fl_pw
     Interpolation method: 'Linear point-slope'
     Use last breakpoint for index at or above upper limit: 'off'
     Overflow mode: 'portable wrapping'
   */
  yL_0d0 = table[iLeft];
  return (table[iLeft + 1U] - yL_0d0) * frac + yL_0d0;
}

/* Model step function for TID0 */
void Torque_Control_step0(void)        /* Sample time: [0.05s, 0.0s] */
{
  real_T rtb_y;
  int32_T tmp;
  real32_T rtb_Abs14;
  real32_T rtb_Delay;
  real32_T rtb_UkYk1;
  int16_T tmp_0;
  uint8_T tmp_1;
  boolean_T guard1;
  boolean_T rtb_LogicalOperator;
  boolean_T rtb_LogicalOperator4_d_tmp;
  boolean_T rtb_LogicalOperator_e_tmp;
  boolean_T rtb_LogicalOperator_e_tmp_0;
  boolean_T rtb_LogicalOperator_e_tmp_1;
  boolean_T rtb_LogicalOperator_e_tmp_tmp;
  boolean_T rtb_LogicalOperator_j_tmp;
  boolean_T rtb_LogicalOperator_j_tmp_0;
  boolean_T rtb_LogicalOperator_j_tmp_1;

  /* Logic: '<S114>/Logical Operator' incorporates:
   *  Constant: '<S114>/Time constant'
   *  Constant: '<S118>/Constant'
   *  RelationalOperator: '<S118>/Compare'
   *  Sum: '<S114>/Sum1'
   */
  rtb_LogicalOperator = (((real32_T)(0.25 - Torque_Control_B.Probe[0]) <= 0.0F) &&
    Torque_Control_ConstB.Compare);

  /* Abs: '<S11>/Abs' incorporates:
   *  Constant: '<S11>/Constant'
   *  Constant: '<S11>/Constant1'
   *  Constant: '<S11>/Constant2'
   *  Constant: '<S11>/Constant3'
   *  Inport: '<Root>/CAL_sRatio'
   *  Inport: '<Root>/CAL_sTyreRadius'
   *  Inport: '<Root>/TQ_IN_sMotSpdFilter'
   *  Product: '<S11>/Divide'
   */
  Torque_Control_Y.TQ_TEMP_sVeilSpdPreFltr = fabsf(6.28318501F *
    Torque_Control_U.CAL_sTyreRadius * 60.0F *
    Torque_Control_U.TQ_IN_sMotSpdFilter / 1000.0F / Torque_Control_U.CAL_sRatio);

  /* DiscreteIntegrator: '<S120>/Integrator' */
  if (Torque_Control_DW.Integrator_IC_LOADING != 0) {
    Torque_Control_DW.Integrator_DSTATE =
      Torque_Control_Y.TQ_TEMP_sVeilSpdPreFltr;
  }

  if (rtb_LogicalOperator || (Torque_Control_DW.Integrator_PrevResetState != 0))
  {
    Torque_Control_DW.Integrator_DSTATE =
      Torque_Control_Y.TQ_TEMP_sVeilSpdPreFltr;
  }

  /* Relay: '<S94>/Relay' incorporates:
   *  DiscreteIntegrator: '<S120>/Integrator'
   */
  Torque_Control_DW.Relay_Mode = ((Torque_Control_DW.Integrator_DSTATE >= 6.0F) ||
    ((!(Torque_Control_DW.Integrator_DSTATE <= 2.0F)) &&
     Torque_Control_DW.Relay_Mode));

  /* Logic: '<S94>/Logical Operator2' incorporates:
   *  Inport: '<Root>/TQ_IN_bBrakeSW'
   *  Logic: '<S5>/Logical Operator1'
   *  Switch: '<S5>/Switch1'
   */
  rtb_LogicalOperator_e_tmp_tmp = !Torque_Control_U.TQ_IN_bBrakeSW;

  /* Logic: '<S94>/Logical Operator' incorporates:
   *  Constant: '<S97>/Constant'
   *  Constant: '<S98>/Constant'
   *  Inport: '<Root>/TQ_IN_bAccelSW'
   *  Inport: '<Root>/TQ_IN_bCmdBackw'
   *  Inport: '<Root>/TQ_IN_sAccelPert'
   *  Inport: '<Root>/TQ_IN_sBrakePert'
   *  Logic: '<S94>/Logical Operator1'
   *  Logic: '<S94>/Logical Operator2'
   *  Logic: '<S95>/Logical Operator5'
   *  RelationalOperator: '<S97>/Compare'
   *  RelationalOperator: '<S98>/Compare'
   */
  rtb_LogicalOperator_e_tmp = ((!Torque_Control_U.TQ_IN_bAccelSW) &&
    (Torque_Control_U.TQ_IN_sAccelPert <= 0.05F) &&
    rtb_LogicalOperator_e_tmp_tmp && (Torque_Control_U.TQ_IN_sBrakePert <= 0.05F)
    && Torque_Control_U.TQ_IN_bCmdBackw);

  /* Logic: '<S94>/Logical Operator3' incorporates:
   *  Inport: '<Root>/TQ_IN_bAirPressLow'
   *  Logic: '<Root>/Logical Operator10'
   *  Logic: '<Root>/Logical Operator3'
   *  Logic: '<S95>/Logical Operator2'
   */
  rtb_LogicalOperator_e_tmp_0 = !Torque_Control_U.TQ_IN_bAirPressLow;

  /* Logic: '<S94>/Logical Operator4' incorporates:
   *  Inport: '<Root>/TQ_IN_bHandBrake'
   *  Logic: '<S95>/Logical Operator1'
   */
  rtb_LogicalOperator_e_tmp_1 = !Torque_Control_U.TQ_IN_bHandBrake;

  /* Logic: '<S94>/Logical Operator' incorporates:
   *  Constant: '<S99>/Constant'
   *  Inport: '<Root>/CAL_bRCrawlFlg'
   *  Inport: '<Root>/TQ_IN_bMCUEnFB'
   *  Inport: '<Root>/TQ_IN_bReady'
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   *  Logic: '<S94>/Logical Operator3'
   *  Logic: '<S94>/Logical Operator4'
   *  RelationalOperator: '<S99>/Compare'
   *  Relay: '<S94>/Relay'
   */
  Torque_Control_Y.TQ_TEMP_bRCrawlFlg = (rtb_LogicalOperator_e_tmp &&
    Torque_Control_U.TQ_IN_bMCUEnFB && Torque_Control_U.TQ_IN_bReady &&
    rtb_LogicalOperator_e_tmp_0 && rtb_LogicalOperator_e_tmp_1 &&
    (Torque_Control_U.TQ_IN_u8VeilFltLvl <= 2) && (!Torque_Control_DW.Relay_Mode)
    && Torque_Control_U.CAL_bRCrawlFlg);

  /* Chart: '<S94>/Chart' incorporates:
   *  Inport: '<Root>/CAL_i16MaxCrawlTorq'
   *  Inport: '<Root>/TQ_IN_bHandBrake'
   *  Inport: '<Root>/TQ_IN_sBrakePert'
   *  Inport: '<Root>/TQ_IN_sMotSpd'
   *  Inport: '<Root>/TQ_IN_sMotTorq'
   *  Outport: '<Root>/TQ_OUT_bRCrawlFlt'
   */
  if (Torque_Control_DW.is_active_c3_Torque_Control == 0) {
    Torque_Control_DW.is_active_c3_Torque_Control = 1U;
    Torque_Control_DW.is_c3_Torque_Control = Torque_Control_IN_R_Judge_Creep;

    /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
    Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;
    Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;
  } else {
    guard1 = false;
    switch (Torque_Control_DW.is_c3_Torque_Control) {
     case Torque_Control_IN_R_Judge_Creep:
      if (Torque_Control_Y.TQ_OUT_bRCrawlFlt &&
          ((Torque_Control_U.TQ_IN_sBrakePert > 0.1) ||
           Torque_Control_U.TQ_IN_bHandBrake)) {
        Torque_Control_DW.is_c3_Torque_Control = Torque_Contro_IN_R_Judge_Creep3;

        /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;
        Torque_Control_Y.TQ_OUT_bRCrawlFlt = false;
      } else if (Torque_Control_Y.TQ_TEMP_bRCrawlFlg &&
                 (!Torque_Control_Y.TQ_OUT_bRCrawlFlt)) {
        Torque_Control_DW.is_c3_Torque_Control = Torque_Contro_IN_R_Judge_Creep1;

        /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlg = true;
        Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;
      }
      break;

     case Torque_Contro_IN_R_Judge_Creep1:
      if (!Torque_Control_Y.TQ_TEMP_bRCrawlFlg) {
        Torque_Control_DW.is_c3_Torque_Control = Torque_Control_IN_R_Judge_Creep;

        /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;
        Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;
      } else if ((Torque_Control_U.TQ_IN_sMotSpd > 20.0F) &&
                 (Torque_Control_U.TQ_IN_sMotTorq < (real_T)
                  Torque_Control_U.CAL_i16MaxCrawlTorq * -0.95)) {
        Torque_Control_DW.is_c3_Torque_Control = Torque_Contro_IN_R_Judge_Creep2;
      }
      break;

     case Torque_Contro_IN_R_Judge_Creep2:
      if ((Torque_Control_U.TQ_IN_sMotSpd <= 0.0F) ||
          (Torque_Control_U.TQ_IN_sMotTorq >= (real_T)
           Torque_Control_U.CAL_i16MaxCrawlTorq * -0.95)) {
        Torque_Control_DW.is_c3_Torque_Control = Torque_Contro_IN_R_Judge_Creep1;

        /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlg = true;
        Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;

        /* Outport: '<Root>/TQ_OUT_bRCrawlFlt' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlt = false;
      } else if (Torque_Control_DW.TQ_TEMP_CrawlCnt >= 1000.0) {
        /* Outport: '<Root>/TQ_OUT_bRCrawlFlt' */
        Torque_Control_Y.TQ_OUT_bRCrawlFlt = true;
        guard1 = true;
      } else if (!Torque_Control_Y.TQ_TEMP_bRCrawlFlg) {
        guard1 = true;
      } else {
        Torque_Control_DW.TQ_TEMP_CrawlCnt++;
      }
      break;

     default:
      /* case IN_R_Judge_Creep3: */
      Torque_Control_DW.is_c3_Torque_Control = Torque_Control_IN_R_Judge_Creep;

      /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
      Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;
      Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;
      break;
    }

    if (guard1) {
      Torque_Control_DW.is_c3_Torque_Control = Torque_Control_IN_R_Judge_Creep;

      /* Outport: '<Root>/TQ_OUT_bRCrawlFlg' */
      Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;
      Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;
    }
  }

  /* End of Chart: '<S94>/Chart' */

  /* Switch: '<S5>/Switch2' incorporates:
   *  Outport: '<Root>/TQ_OUT_bRCrawlFlg'
   */
  if (Torque_Control_Y.TQ_OUT_bRCrawlFlg) {
    /* Abs: '<S5>/Abs1' incorporates:
     *  Inport: '<Root>/CAL_i16MaxCrawlTorq'
     */
    if (Torque_Control_U.CAL_i16MaxCrawlTorq < 0) {
      tmp_0 = (int16_T)-Torque_Control_U.CAL_i16MaxCrawlTorq;
    } else {
      tmp_0 = Torque_Control_U.CAL_i16MaxCrawlTorq;
    }

    /* Switch: '<S5>/Switch2' incorporates:
     *  Abs: '<S5>/Abs1'
     *  DiscreteIntegrator: '<S120>/Integrator'
     *  Gain: '<S5>/Gain2'
     *  Lookup_n-D: '<S5>/RVeilSpd_CrawlTorque'
     *  MinMax: '<S5>/MinMax'
     */
    Torque_Control_Y.TQ_sCrawCheck = fmaxf((real32_T)(-32768 * tmp_0) *
      3.05175781E-5F, Torque_Control_look1_i_rQYGWmZ3
      (Torque_Control_DW.Integrator_DSTATE, GearR_VeilSpd, RVeilSpd_CrawlTorque,
       7U));

    /* Saturate: '<S5>/Saturation2' */
    if (Torque_Control_Y.TQ_sCrawCheck > 100.0F) {
      /* Switch: '<S5>/Switch2' */
      Torque_Control_Y.TQ_sCrawCheck = 100.0F;
    } else if (Torque_Control_Y.TQ_sCrawCheck < -1000.0F) {
      /* Switch: '<S5>/Switch2' */
      Torque_Control_Y.TQ_sCrawCheck = -1000.0F;
    }

    /* End of Saturate: '<S5>/Saturation2' */
  } else {
    /* Switch: '<S5>/Switch2' incorporates:
     *  Constant: '<S5>/Constant1'
     */
    Torque_Control_Y.TQ_sCrawCheck = 0.0F;
  }

  /* End of Switch: '<S5>/Switch2' */

  /* MATLAB Function: '<S5>/RSpdLimitK' incorporates:
   *  DataTypeConversion: '<S5>/Data Type Conversion1'
   *  DataTypeConversion: '<S5>/Data Type Conversion32'
   *  DiscreteIntegrator: '<S120>/Integrator'
   *  Inport: '<Root>/CAL_sRVeilSpdLimit'
   *  Inport: '<Root>/TQ_IN_sMotSpd'
   */
  if (Torque_Control_U.TQ_IN_sMotSpd > 0.0F) {
    rtb_y = 1.0;
  } else if ((Torque_Control_DW.Integrator_DSTATE <
              Torque_Control_U.CAL_sRVeilSpdLimit - 10.0) &&
             (Torque_Control_DW.Integrator_DSTATE >= 0.0F)) {
    rtb_y = 1.0;
  } else if ((Torque_Control_DW.Integrator_DSTATE >=
              Torque_Control_U.CAL_sRVeilSpdLimit - 10.0) &&
             (Torque_Control_DW.Integrator_DSTATE <
              Torque_Control_U.CAL_sRVeilSpdLimit)) {
    rtb_y = (real_T)Torque_Control_DW.Integrator_DSTATE -
      Torque_Control_U.CAL_sRVeilSpdLimit;
    rtb_y = 0.01 * (rtb_y * rtb_y);
  } else {
    rtb_y = 0.0;
  }

  /* End of MATLAB Function: '<S5>/RSpdLimitK' */

  /* Switch: '<S5>/Switch5' incorporates:
   *  Inport: '<Root>/TQ_IN_bDoorOpenSigl'
   *  Inport: '<Root>/TQ_IN_bDoorUnlockReq'
   *  Logic: '<S5>/Logical Operator2'
   *  Logic: '<S5>/NOT'
   *  Saturate: '<S5>/Saturation1'
   */
  if ((!Torque_Control_U.TQ_IN_bDoorUnlockReq) &&
      Torque_Control_U.TQ_IN_bDoorOpenSigl) {
    /* Switch: '<S5>/Switch5' incorporates:
     *  Constant: '<S5>/Constant'
     */
    Torque_Control_Y.TQ_TEMP_sRSpdLimitK = 0.0;
  } else if (rtb_y > 1.0) {
    /* Switch: '<S5>/Switch5' incorporates:
     *  Saturate: '<S5>/Saturation1'
     */
    Torque_Control_Y.TQ_TEMP_sRSpdLimitK = 1.0;
  } else {
    /* Switch: '<S5>/Switch5' incorporates:
     *  Saturate: '<S5>/Saturation1'
     */
    Torque_Control_Y.TQ_TEMP_sRSpdLimitK = (real32_T)rtb_y;
  }

  /* End of Switch: '<S5>/Switch5' */

  /* Product: '<S3>/Divide1' incorporates:
   *  Constant: '<S3>/Constant5'
   *  Inport: '<Root>/CAL_sVeilChangeEfficiency'
   *  Inport: '<Root>/TQ_IN_sBMSDisChgCurr30s'
   *  Inport: '<Root>/TQ_IN_sBMSVolt'
   */
  Torque_Control_Y.TQ_TEMP_sBMSOutputPower =
    Torque_Control_U.TQ_IN_sBMSDisChgCurr30s * Torque_Control_U.TQ_IN_sBMSVolt *
    Torque_Control_U.CAL_sVeilChangeEfficiency / 1000.0F;

  /* Abs: '<S3>/Abs14' incorporates:
   *  Inport: '<Root>/TQ_IN_sMotSpdFilter'
   */
  rtb_Abs14 = fabsf(Torque_Control_U.TQ_IN_sMotSpdFilter);

  /* Saturate: '<S3>/Saturation' incorporates:
   *  Inport: '<Root>/TQ_IN_sMotSpdFilter'
   *  Lookup_n-D: '<S3>/MotorChangeEfficiency'
   */
  Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency =
    Torque_Control_look1_i_k8T0tS4Z(Torque_Control_U.TQ_IN_sMotSpdFilter,
    MotorSpeed_X, MotorChangeEfficiency_Z, 16U);

  /* Saturate: '<S3>/Saturation' */
  if (Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency > 1.0F) {
    /* Saturate: '<S3>/Saturation' */
    Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency = 1.0F;
  } else if (Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency < 0.75F) {
    /* Saturate: '<S3>/Saturation' */
    Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency = 0.75F;
  }

  /* End of Saturate: '<S3>/Saturation' */

  /* Product: '<S3>/Divide4' incorporates:
   *  Constant: '<S3>/Constant1'
   *  Inport: '<Root>/TQ_IN_sMCUTorqUpper'
   *  Inport: '<Root>/TQ_IN_sMotSpdFilter'
   */
  Torque_Control_Y.TQ_TEMP_sMotInputPower = Torque_Control_U.TQ_IN_sMCUTorqUpper
    * Torque_Control_U.TQ_IN_sMotSpdFilter / 9550.0F /
    Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency;

  /* Switch: '<S3>/Switch3' incorporates:
   *  Abs: '<S3>/Abs13'
   *  Inport: '<Root>/CAL_sRatedMotSpd'
   *  RelationalOperator: '<S3>/Relational Operator3'
   *  RelationalOperator: '<S3>/Relational Operator4'
   *  Saturate: '<S3>/Saturation2'
   *  Switch: '<S3>/Switch4'
   */
  if (rtb_Abs14 >= Torque_Control_U.CAL_sRatedMotSpd) {
    /* Saturate: '<S3>/Saturation1' */
    if (rtb_Abs14 > 15000.0F) {
      rtb_Delay = 15000.0F;
    } else if (rtb_Abs14 < 10.0F) {
      rtb_Delay = 10.0F;
    } else {
      rtb_Delay = rtb_Abs14;
    }

    /* Switch: '<S3>/Switch3' incorporates:
     *  Constant: '<S3>/Constant2'
     *  Product: '<S3>/Divide5'
     *  Saturate: '<S3>/Saturation1'
     */
    Torque_Control_Y.TQ_TEMP_sBMSAllowDriveTorq =
      Torque_Control_Y.TQ_TEMP_sBMSOutputPower * 9550.0F / rtb_Delay;
  } else if (Torque_Control_Y.TQ_TEMP_sBMSOutputPower >=
             Torque_Control_Y.TQ_TEMP_sMotInputPower) {
    /* Switch: '<S3>/Switch3' incorporates:
     *  Inport: '<Root>/CAL_sPeakMotTorq'
     *  Switch: '<S3>/Switch4'
     */
    Torque_Control_Y.TQ_TEMP_sBMSAllowDriveTorq =
      Torque_Control_U.CAL_sPeakMotTorq;
  } else {
    if (rtb_Abs14 > 15000.0F) {
      /* Saturate: '<S3>/Saturation2' incorporates:
       *  Switch: '<S3>/Switch4'
       */
      rtb_Delay = 15000.0F;
    } else if (rtb_Abs14 < 200.0F) {
      /* Saturate: '<S3>/Saturation2' incorporates:
       *  Switch: '<S3>/Switch4'
       */
      rtb_Delay = 200.0F;
    } else {
      /* Saturate: '<S3>/Saturation2' incorporates:
       *  Abs: '<S3>/Abs13'
       *  Switch: '<S3>/Switch4'
       */
      rtb_Delay = rtb_Abs14;
    }

    /* Switch: '<S3>/Switch3' incorporates:
     *  Abs: '<S3>/Abs13'
     *  Constant: '<S3>/Constant3'
     *  Product: '<S3>/Divide6'
     *  Saturate: '<S3>/Saturation2'
     *  Switch: '<S3>/Switch4'
     */
    Torque_Control_Y.TQ_TEMP_sBMSAllowDriveTorq =
      Torque_Control_Y.TQ_TEMP_sBMSOutputPower *
      Torque_Control_Y.TQ_TEMP_sMotChangeEfficiency * 9550.0F / rtb_Delay;
  }

  /* End of Switch: '<S3>/Switch3' */

  /* Lookup_n-D: '<S10>/BMSSOC_LimitK' incorporates:
   *  Inport: '<Root>/TQ_IN_sBMSSOC'
   */
  Torque_Control_Y.TQ_TEMP_sBMSSOCLimitK = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_U.TQ_IN_sBMSSOC, BMSSOC, BMSSOCLimitK, 3U);

  /* Lookup_n-D: '<S10>/MCUTemp_LimitK' incorporates:
   *  Inport: '<Root>/TQ_IN_sMCUTemp'
   */
  Torque_Control_Y.TQ_TEMP_sMCUTempLimitK = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_U.TQ_IN_sMCUTemp, MCUTemp, MCUTempLimitK, 3U);

  /* Lookup_n-D: '<S10>/MotTemp_LimitK' incorporates:
   *  Inport: '<Root>/TQ_IN_sMotTemp'
   */
  Torque_Control_Y.TQ_TEMP_sMotTempLimitK = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_U.TQ_IN_sMotTemp, MotTemp, MotTempLimitK, 3U);

  /* Lookup_n-D: '<S10>/FaultLevel_LimitK' incorporates:
   *  DataTypeConversion: '<S10>/Data Type Conversion'
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   */
  Torque_Control_Y.TQ_TEMP_sVeilFltLvlLimitK = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_U.TQ_IN_u8VeilFltLvl, VeilFltLvl, VeilFltLvlLimitK, 4U);

  /* Saturate: '<S10>/Saturation' incorporates:
   *  MinMax: '<S10>/Min'
   */
  Torque_Control_Y.TQ_OUT_sFinallyLimitK = fminf(fminf(fminf
    (Torque_Control_Y.TQ_TEMP_sBMSSOCLimitK,
     Torque_Control_Y.TQ_TEMP_sMCUTempLimitK),
    Torque_Control_Y.TQ_TEMP_sMotTempLimitK),
    Torque_Control_Y.TQ_TEMP_sVeilFltLvlLimitK);

  /* Saturate: '<S10>/Saturation' */
  if (Torque_Control_Y.TQ_OUT_sFinallyLimitK > 1.0F) {
    /* Saturate: '<S10>/Saturation' */
    Torque_Control_Y.TQ_OUT_sFinallyLimitK = 1.0F;
  } else if (Torque_Control_Y.TQ_OUT_sFinallyLimitK < 0.0F) {
    /* Saturate: '<S10>/Saturation' */
    Torque_Control_Y.TQ_OUT_sFinallyLimitK = 0.0F;
  }

  /* End of Saturate: '<S10>/Saturation' */

  /* Saturate: '<S3>/Saturation3' incorporates:
   *  Abs: '<S3>/Abs15'
   */
  if (rtb_Abs14 > 15000.0F) {
    rtb_Delay = 15000.0F;
  } else if (rtb_Abs14 < 200.0F) {
    rtb_Delay = 200.0F;
  } else {
    rtb_Delay = rtb_Abs14;
  }

  /* Abs: '<S3>/Abs9' incorporates:
   *  Abs: '<S3>/Abs1'
   *  Constant: '<S3>/Constant4'
   *  Inport: '<Root>/CAL_sPeakMotPower'
   *  Product: '<S3>/Divide7'
   *  Product: '<S3>/Product2'
   *  Saturate: '<S3>/Saturation3'
   */
  Torque_Control_Y.TQ_TEMP_sPowerAllowTorq = fabsf
    (Torque_Control_Y.TQ_OUT_sFinallyLimitK * Torque_Control_U.CAL_sPeakMotPower
     * 9550.0F / rtb_Delay);

  /* MinMax: '<S3>/MinMax1' incorporates:
   *  Abs: '<S3>/Abs11'
   *  Inport: '<Root>/TQ_IN_sMCUTorqUpper'
   *  Inport: '<Root>/TQ_IN_sMotSpdFilter'
   *  Lookup_n-D: '<S3>/Speed_Torque'
   *  MinMax: '<S3>/MinMax'
   */
  Torque_Control_Y.TQ_TEMP_sVeilAllowBrakeTorq = fminf
    (Torque_Control_look1_i_rQYGWmZ3(Torque_Control_U.TQ_IN_sMotSpdFilter,
      MotorSpeed_X, MotorTorqueUpper_Y, 16U), fabsf
     (Torque_Control_U.TQ_IN_sMCUTorqUpper));

  /* MinMax: '<S3>/Min' incorporates:
   *  Abs: '<S3>/Abs7'
   *  Inport: '<Root>/CAL_sPeakMotTorq'
   */
  Torque_Control_Y.TQ_TEMP_sVeilAllowDriveTorq = fminf(fminf(fminf
    (Torque_Control_Y.TQ_TEMP_sBMSAllowDriveTorq,
     Torque_Control_Y.TQ_TEMP_sPowerAllowTorq),
    Torque_Control_Y.TQ_TEMP_sVeilAllowBrakeTorq), fabsf
    (Torque_Control_U.CAL_sPeakMotTorq));

  /* Switch: '<S6>/Switch' incorporates:
   *  Inport: '<Root>/TQ_IN_bEcoMode'
   *  Inport: '<Root>/TQ_IN_bSportMode'
   *  Switch: '<S6>/Switch1'
   */
  if (Torque_Control_U.TQ_IN_bSportMode) {
    /* Saturate: '<S6>/Saturation' incorporates:
     *  Inport: '<Root>/TQ_IN_sAccelPert'
     *  Lookup_n-D: '<S6>/Torque_AccelPert1'
     */
    Torque_Control_Y.TQ_TEMP_sAccelPert = Torque_Control_look1_i_rQYGWmZ3
      (Torque_Control_U.TQ_IN_sAccelPert, AccelPert1, SportMode_AccelPert, 3U);
  } else if (Torque_Control_U.TQ_IN_bEcoMode) {
    /* Saturate: '<S6>/Saturation' incorporates:
     *  Inport: '<Root>/TQ_IN_sAccelPert'
     *  Lookup_n-D: '<S6>/Torque_AccelPert2'
     *  Switch: '<S6>/Switch1'
     */
    Torque_Control_Y.TQ_TEMP_sAccelPert = Torque_Control_look1_i_rQYGWmZ3
      (Torque_Control_U.TQ_IN_sAccelPert, AccelPert2, EcoMode_AccelPert, 3U);
  } else {
    /* Saturate: '<S6>/Saturation' incorporates:
     *  Inport: '<Root>/TQ_IN_sAccelPert'
     *  Lookup_n-D: '<S6>/Torque_AccelPert3'
     *  Switch: '<S6>/Switch1'
     */
    Torque_Control_Y.TQ_TEMP_sAccelPert = Torque_Control_look1_i_rQYGWmZ3
      (Torque_Control_U.TQ_IN_sAccelPert, AccelPert, Torque_AccelPert, 4U);
  }

  /* End of Switch: '<S6>/Switch' */

  /* Saturate: '<S6>/Saturation' */
  if (Torque_Control_Y.TQ_TEMP_sAccelPert > 1.0F) {
    /* Saturate: '<S6>/Saturation' */
    Torque_Control_Y.TQ_TEMP_sAccelPert = 1.0F;
  } else if (Torque_Control_Y.TQ_TEMP_sAccelPert < 0.0F) {
    /* Saturate: '<S6>/Saturation' */
    Torque_Control_Y.TQ_TEMP_sAccelPert = 0.0F;
  }

  /* End of Saturate: '<S6>/Saturation' */

  /* Saturate: '<S5>/Saturation' incorporates:
   *  Abs: '<S5>/Abs'
   *  Gain: '<S5>/Gain'
   *  Gain: '<S5>/Gain1'
   *  Product: '<S5>/Product'
   */
  Torque_Control_Y.TQ_R_sDriveTorqCheck = -fabs
    (Torque_Control_Y.TQ_TEMP_sRSpdLimitK * (0.8F *
      Torque_Control_Y.TQ_TEMP_sVeilAllowDriveTorq) *
     Torque_Control_Y.TQ_TEMP_sAccelPert);

  /* Saturate: '<S5>/Saturation' */
  if (Torque_Control_Y.TQ_R_sDriveTorqCheck < -2000.0) {
    /* Saturate: '<S5>/Saturation' */
    Torque_Control_Y.TQ_R_sDriveTorqCheck = -2000.0;
  }

  /* End of Saturate: '<S5>/Saturation' */

  /* Logic: '<S95>/Logical Operator9' incorporates:
   *  Inport: '<Root>/TQ_IN_bCmdNtw'
   *  Logic: '<Root>/Logical Operator14'
   *  Logic: '<Root>/Logical Operator6'
   */
  rtb_LogicalOperator4_d_tmp = !Torque_Control_U.TQ_IN_bCmdNtw;

  /* Logic: '<S95>/Logical Operator4' incorporates:
   *  Constant: '<S103>/Constant'
   *  Constant: '<S104>/Constant'
   *  Inport: '<Root>/CAL_bRSlopeFlg'
   *  Inport: '<Root>/TQ_IN_bMCUEnFB'
   *  Inport: '<Root>/TQ_IN_bReady'
   *  Inport: '<Root>/TQ_IN_sMotSpd'
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   *  Logic: '<S95>/Logical Operator5'
   *  Logic: '<S95>/Logical Operator9'
   *  Outport: '<Root>/TQ_OUT_bRCrawlFlt'
   *  RelationalOperator: '<S103>/Compare'
   *  RelationalOperator: '<S104>/Compare'
   */
  Torque_Control_Y.TQ_TEMP_bRSlopeFlg = (Torque_Control_Y.TQ_OUT_bRCrawlFlt ||
    (rtb_LogicalOperator_e_tmp && rtb_LogicalOperator4_d_tmp &&
     Torque_Control_U.TQ_IN_bMCUEnFB && Torque_Control_U.TQ_IN_bReady &&
     rtb_LogicalOperator_e_tmp_0 && rtb_LogicalOperator_e_tmp_1 &&
     Torque_Control_U.CAL_bRSlopeFlg && (Torque_Control_U.TQ_IN_u8VeilFltLvl <=
    2) && (Torque_Control_U.TQ_IN_sMotSpd > 20.0F)));

  /* Delay: '<Root>/Delay' */
  rtb_Delay = Torque_Control_DW.Delay_DSTATE;

  /* Chart: '<S95>/Chart1' */
  if (Torque_Control_DW.is_active_c4_Torque_Control == 0) {
    Torque_Control_DW.is_active_c4_Torque_Control = 1U;
    Torque_Control_DW.is_c4_Torque_Control = Torque_Control_IN_STEP1;

    /* Outport: '<Root>/TQ_OUT_bRSlopeFlg' */
    Torque_Control_Y.TQ_OUT_bRSlopeFlg = false;

    /* Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg' */
    Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg = false;

    /* Outport: '<Root>/TQ_OUT_sRSmoothTorq' */
    Torque_Control_Y.TQ_OUT_sRSmoothTorq = 0.0F;
    Torque_Control_DW.TQ_TEMP_u16SlopeCnt = 0U;

    /* Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' */
    /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
    Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 1U;
  } else {
    switch (Torque_Control_DW.is_c4_Torque_Control) {
     case Torque_Control_IN_STEP1:
      if (Torque_Control_Y.TQ_TEMP_bRSlopeFlg) {
        Torque_Control_DW.is_c4_Torque_Control = Torque_Control_IN_STEP2;
      }
      break;

     case Torque_Control_IN_STEP2:
      if ((Torque_Control_DW.TQ_TEMP_u16SlopeCnt >
           Torque_Control_U.CAL_u16RSlopeSetTime) ||
          (Torque_Control_U.TQ_IN_sBrakePert > 0.05) ||
          Torque_Control_U.TQ_IN_bHandBrake || Torque_Control_U.TQ_IN_bCmdNtw) {
        Torque_Control_DW.is_c4_Torque_Control = Torque_Control_IN_STEP3;

        /* Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg = true;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt = 0U;

        /* Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 3U;
      } else if (((Torque_Control_U.TQ_IN_sAccelPert >= 0.1) && (fabs(rtb_Delay
                    - Torque_Control_U.TQ_IN_sMotTorq) < 20.0)) ||
                 ((!Torque_Control_U.TQ_IN_bCmdBackw) ||
                  (!Torque_Control_U.TQ_IN_bMCUEnFB) ||
                  (!Torque_Control_U.TQ_IN_bReady) ||
                  Torque_Control_U.TQ_IN_bAirPressLow ||
                  (Torque_Control_U.TQ_IN_u8VeilFltLvl >= 3))) {
        Torque_Control_DW.is_c4_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/TQ_OUT_bRSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeFlg = false;

        /* Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg = false;

        /* Outport: '<Root>/TQ_OUT_sRSmoothTorq' */
        Torque_Control_Y.TQ_OUT_sRSmoothTorq = 0.0F;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt = 0U;

        /* Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 1U;
      } else {
        /* Outport: '<Root>/TQ_OUT_bRSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeFlg = true;

        /* Outport: '<Root>/TQ_OUT_sRSmoothTorq' incorporates:
         *  Inport: '<Root>/TQ_IN_sMotTorq'
         */
        Torque_Control_Y.TQ_OUT_sRSmoothTorq = Torque_Control_U.TQ_IN_sMotTorq;
        tmp = Torque_Control_DW.TQ_TEMP_u16SlopeCnt + 1;
        if (Torque_Control_DW.TQ_TEMP_u16SlopeCnt + 1 > 65535) {
          tmp = 65535;
        }

        Torque_Control_DW.TQ_TEMP_u16SlopeCnt = (uint16_T)tmp;

        /* Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 2U;
      }
      break;

     default:
      /* case IN_STEP3: */
      if (Torque_Control_DW.TQ_TEMP_u16SlopeCnt >= 10) {
        Torque_Control_DW.is_c4_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/TQ_OUT_bRSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeFlg = false;

        /* Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg = false;

        /* Outport: '<Root>/TQ_OUT_sRSmoothTorq' */
        Torque_Control_Y.TQ_OUT_sRSmoothTorq = 0.0F;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt = 0U;

        /* Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 1U;
      } else {
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt++;
      }
      break;
    }
  }

  /* End of Chart: '<S95>/Chart1' */

  /* Switch: '<S5>/Switch1' incorporates:
   *  Constant: '<S92>/Constant'
   *  Inport: '<Root>/TQ_IN_bAccelSW'
   *  Inport: '<Root>/TQ_IN_sAccelPert'
   *  Logic: '<S5>/Logical Operator'
   *  Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg'
   *  RelationalOperator: '<S92>/Compare'
   *  Switch: '<S5>/Switch'
   */
  if (Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg) {
    /* Saturate: '<S6>/Saturation1' incorporates:
     *  Outport: '<Root>/TQ_OUT_sRSmoothTorq'
     */
    Torque_Control_Y.TQ_TEMP_sBrakePert = Torque_Control_Y.TQ_OUT_sRSmoothTorq;
  } else if (Torque_Control_U.TQ_IN_bAccelSW &&
             (Torque_Control_U.TQ_IN_sAccelPert >= 0.05F) &&
             rtb_LogicalOperator_e_tmp_tmp) {
    /* Saturate: '<S6>/Saturation1' incorporates:
     *  Switch: '<S5>/Switch'
     */
    Torque_Control_Y.TQ_TEMP_sBrakePert = (real32_T)
      Torque_Control_Y.TQ_R_sDriveTorqCheck;
  } else {
    /* Saturate: '<S6>/Saturation1' incorporates:
     *  Switch: '<S5>/Switch'
     */
    Torque_Control_Y.TQ_TEMP_sBrakePert = Torque_Control_Y.TQ_sCrawCheck;
  }

  /* Logic: '<S7>/Logical Operator8' incorporates:
   *  Constant: '<S107>/Constant'
   *  DiscreteIntegrator: '<S120>/Integrator'
   *  Inport: '<Root>/TQ_IN_bDisabledPedalSigl'
   *  RelationalOperator: '<S107>/Compare'
   */
  Torque_Control_Y.TQ_TEMP_bDisabledPedalSigl =
    (Torque_Control_U.TQ_IN_bDisabledPedalSigl &&
     (Torque_Control_DW.Integrator_DSTATE <= 5.0F));

  /* Switch: '<Root>/Switch3' incorporates:
   *  Constant: '<Root>/Constant3'
   *  Inport: '<Root>/CAL_bHandBrakeUseFlg'
   *  Inport: '<Root>/TQ_IN_bHandBrake'
   */
  if (Torque_Control_U.CAL_bHandBrakeUseFlg) {
    tmp_1 = Torque_Control_U.TQ_IN_bHandBrake;
  } else {
    tmp_1 = 0U;
  }

  /* Logic: '<Root>/Logical Operator' incorporates:
   *  Inport: '<Root>/TQ_IN_bMCUEnFB'
   *  Inport: '<Root>/TQ_IN_bReady'
   *  Logic: '<Root>/Logical Operator1'
   */
  rtb_LogicalOperator_e_tmp_tmp = (Torque_Control_U.TQ_IN_bReady &&
    Torque_Control_U.TQ_IN_bMCUEnFB);

  /* Logic: '<Root>/Logical Operator13' incorporates:
   *  Inport: '<Root>/TQ_IN_bBMSPDReq'
   *  Logic: '<Root>/Logical Operator4'
   */
  rtb_LogicalOperator_e_tmp = !Torque_Control_U.TQ_IN_bBMSPDReq;

  /* Logic: '<Root>/Logical Operator18' incorporates:
   *  Inport: '<Root>/TQ_IN_bChgGunSt'
   *  Logic: '<Root>/Logical Operator19'
   */
  rtb_LogicalOperator_e_tmp_1 = !Torque_Control_U.TQ_IN_bChgGunSt;

  /* Logic: '<Root>/Logical Operator7' incorporates:
   *  Inport: '<Root>/TQ_IN_bUrgentPD'
   *  Logic: '<Root>/Logical Operator16'
   */
  rtb_LogicalOperator_j_tmp = !Torque_Control_U.TQ_IN_bUrgentPD;

  /* Logic: '<Root>/Logical Operator9' incorporates:
   *  Inport: '<Root>/TQ_IN_bPDTorqFlg'
   *  Logic: '<Root>/Logical Operator17'
   */
  rtb_LogicalOperator_j_tmp_0 = !Torque_Control_U.TQ_IN_bPDTorqFlg;

  /* Logic: '<Root>/Logical Operator5' incorporates:
   *  Logic: '<Root>/Logical Operator12'
   */
  rtb_LogicalOperator_j_tmp_1 = !Torque_Control_Y.TQ_TEMP_bDisabledPedalSigl;

  /* Logic: '<S7>/Logical Operator' incorporates:
   *  Constant: '<S1>/Constant'
   *  Inport: '<Root>/TQ_IN_bCmdBackw'
   *  Inport: '<Root>/TQ_IN_bCmdForw'
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   *  Logic: '<Root>/Logical Operator'
   *  Logic: '<Root>/Logical Operator13'
   *  Logic: '<Root>/Logical Operator15'
   *  Logic: '<Root>/Logical Operator18'
   *  Logic: '<Root>/Logical Operator2'
   *  Logic: '<Root>/Logical Operator5'
   *  Logic: '<Root>/Logical Operator7'
   *  Logic: '<Root>/Logical Operator9'
   *  RelationalOperator: '<S1>/Compare'
   *  Switch: '<Root>/Switch3'
   */
  Torque_Control_Y.TQ_TEMP_bAllowFBFlg = (rtb_LogicalOperator_e_tmp_tmp &&
    (!Torque_Control_U.TQ_IN_bCmdForw) && Torque_Control_U.TQ_IN_bCmdBackw &&
    rtb_LogicalOperator4_d_tmp && (Torque_Control_U.TQ_IN_u8VeilFltLvl <= 2) &&
    rtb_LogicalOperator_e_tmp && rtb_LogicalOperator_e_tmp_1 &&
    rtb_LogicalOperator_j_tmp && rtb_LogicalOperator_j_tmp_0 &&
    rtb_LogicalOperator_e_tmp_0 && (tmp_1 == 0) && rtb_LogicalOperator_j_tmp_1);

  /* Switch: '<Root>/Switch2' incorporates:
   *  Constant: '<Root>/Constant1'
   *  Inport: '<Root>/CAL_bHandBrakeUseFlg'
   *  Inport: '<Root>/TQ_IN_bHandBrake'
   */
  if (Torque_Control_U.CAL_bHandBrakeUseFlg) {
    tmp_1 = Torque_Control_U.TQ_IN_bHandBrake;
  } else {
    tmp_1 = 0U;
  }

  /* Logic: '<Root>/Logical Operator1' incorporates:
   *  Constant: '<S2>/Constant'
   *  Inport: '<Root>/TQ_IN_bCmdBackw'
   *  Inport: '<Root>/TQ_IN_bCmdForw'
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   *  Logic: '<Root>/Logical Operator11'
   *  Logic: '<Root>/Logical Operator8'
   *  RelationalOperator: '<S2>/Compare'
   *  Switch: '<Root>/Switch2'
   */
  Torque_Control_Y.D_Judge_Flg = (rtb_LogicalOperator_e_tmp_tmp &&
    Torque_Control_U.TQ_IN_bCmdForw && (!Torque_Control_U.TQ_IN_bCmdBackw) &&
    rtb_LogicalOperator4_d_tmp && (Torque_Control_U.TQ_IN_u8VeilFltLvl <= 2) &&
    rtb_LogicalOperator_e_tmp && rtb_LogicalOperator_e_tmp_1 &&
    rtb_LogicalOperator_j_tmp && rtb_LogicalOperator_j_tmp_0 &&
    rtb_LogicalOperator_e_tmp_0 && (tmp_1 == 0) && rtb_LogicalOperator_j_tmp_1);

  /* Switch: '<Root>/Switch' incorporates:
   *  Switch: '<Root>/Switch1'
   */
  if (Torque_Control_Y.TQ_TEMP_bAllowFBFlg) {
    /* Switch: '<Root>/Switch' */
    Torque_Control_Y.TQ_OUT_sOutputTorqCmd = Torque_Control_Y.TQ_TEMP_sBrakePert;
  } else if (Torque_Control_Y.D_Judge_Flg) {
    /* Switch: '<Root>/Switch' incorporates:
     *  Switch: '<Root>/Switch1'
     */
    Torque_Control_Y.TQ_OUT_sOutputTorqCmd = (real32_T)
      Torque_Control_B.TmpRTBAtSwitch1Inport1;
  } else {
    /* Switch: '<Root>/Switch' incorporates:
     *  Constant: '<Root>/Constant2'
     *  Switch: '<Root>/Switch1'
     */
    Torque_Control_Y.TQ_OUT_sOutputTorqCmd = 0.0F;
  }

  /* End of Switch: '<Root>/Switch' */

  /* Outputs for Enabled SubSystem: '<Root>/Subsystem1' incorporates:
   *  EnablePort: '<S9>/Enable'
   */
  /* Outputs for Enabled SubSystem: '<Root>/Subsystem' incorporates:
   *  EnablePort: '<S8>/Enable'
   */
  /* Switch: '<Root>/Switch5' incorporates:
   *  Delay: '<Root>/Delay'
   *  Inport: '<Root>/CAL_bSpdChangeRateFlg'
   */
  if (Torque_Control_U.CAL_bSpdChangeRateFlg) {
    if (!Torque_Control_DW.Subsystem_MODE) {
      /* InitializeConditions for Delay: '<S109>/Delay' */
      Torque_Control_DW.icLoad_f = true;
      Torque_Control_DW.Subsystem_MODE = true;
    }

    /* Switch: '<S8>/Switch8' incorporates:
     *  Inport: '<Root>/TQ_IN_bCmdForw'
     */
    if (Torque_Control_U.TQ_IN_bCmdForw) {
      /* Outport: '<Root>/TQ_Check1' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotSpd'
       *  Lookup_n-D: '<S8>/GearD_SpdForwardUp'
       */
      Torque_Control_Y.TQ_Check1 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotSpd, GearD_ForwardMotSpd_X,
         GearD_ForwardGain_Y, 7U);
    } else {
      /* Outport: '<Root>/TQ_Check1' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotSpd'
       *  Lookup_n-D: '<S8>/GearR_SpdBackwardUp'
       */
      Torque_Control_Y.TQ_Check1 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotSpd, GearR_BackwardMotSpd_X,
         GearR_BackwardGain_Y, 6U);
    }

    /* End of Switch: '<S8>/Switch8' */

    /* Switch: '<S8>/Switch4' incorporates:
     *  Inport: '<Root>/TQ_IN_bMCUSpdMode'
     */
    if (Torque_Control_U.TQ_IN_bMCUSpdMode) {
      /* Outport: '<Root>/TQ_Check3' incorporates:
       *  Gain: '<S8>/Gain'
       *  Outport: '<Root>/TQ_Check1'
       */
      Torque_Control_Y.TQ_Check3 = 3.0F * Torque_Control_Y.TQ_Check1;
    } else {
      /* Outport: '<Root>/TQ_Check3' incorporates:
       *  Outport: '<Root>/TQ_Check1'
       */
      Torque_Control_Y.TQ_Check3 = Torque_Control_Y.TQ_Check1;
    }

    /* End of Switch: '<S8>/Switch4' */

    /* Product: '<S109>/delta fall limit' incorporates:
     *  Outport: '<Root>/TQ_Check3'
     *  Product: '<S109>/delta rise limit'
     *  SampleTimeMath: '<S109>/sample time'
     *
     * About '<S109>/sample time':
     *  y = K where K = ( w * Ts )
     *   */
    Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = Torque_Control_Y.TQ_Check3 *
      0.05F;

    /* Delay: '<S109>/Delay' */
    if (Torque_Control_DW.icLoad_f) {
      Torque_Control_DW.Delay_DSTATE_fg = Torque_Control_Y.TQ_OUT_sOutputTorqCmd;
    }

    /* Sum: '<S109>/Difference Inputs1' incorporates:
     *  Delay: '<S109>/Delay'
     *
     * Block description for '<S109>/Difference Inputs1':
     *
     *  Add in CPU
     */
    rtb_UkYk1 = Torque_Control_Y.TQ_OUT_sOutputTorqCmd -
      Torque_Control_DW.Delay_DSTATE_fg;

    /* Switch: '<S8>/Switch10' incorporates:
     *  Inport: '<Root>/TQ_IN_bCmdForw'
     */
    if (Torque_Control_U.TQ_IN_bCmdForw) {
      /* Outport: '<Root>/TQ_Check2' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotSpd'
       *  Lookup_n-D: '<S8>/GearD_SpdForwardDown'
       */
      Torque_Control_Y.TQ_Check2 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotSpd, GearD_ForwardMotSpd_X1,
         GearD_ForwardDrop_Y, 7U);
    } else {
      /* Outport: '<Root>/TQ_Check2' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotSpd'
       *  Lookup_n-D: '<S8>/GearR_SpdBackwardDown'
       */
      Torque_Control_Y.TQ_Check2 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotSpd, GearR_BackwardMotSpd_X1,
         GearR_BackwardDrop_Y, 6U);
    }

    /* End of Switch: '<S8>/Switch10' */

    /* Switch: '<S8>/Switch6' incorporates:
     *  Inport: '<Root>/TQ_IN_bMCUSpdMode'
     */
    if (Torque_Control_U.TQ_IN_bMCUSpdMode) {
      /* Outport: '<Root>/TQ_Check4' incorporates:
       *  Gain: '<S8>/Gain1'
       *  Outport: '<Root>/TQ_Check2'
       */
      Torque_Control_Y.TQ_Check4 = 3.0F * Torque_Control_Y.TQ_Check2;
    } else {
      /* Outport: '<Root>/TQ_Check4' incorporates:
       *  Outport: '<Root>/TQ_Check2'
       */
      Torque_Control_Y.TQ_Check4 = Torque_Control_Y.TQ_Check2;
    }

    /* End of Switch: '<S8>/Switch6' */

    /* Switch: '<S110>/Switch2' incorporates:
     *  RelationalOperator: '<S110>/LowerRelop1'
     */
    if (!(rtb_UkYk1 > Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq)) {
      /* Product: '<S109>/delta fall limit' incorporates:
       *  Outport: '<Root>/TQ_Check4'
       *  SampleTimeMath: '<S109>/sample time'
       *
       * About '<S109>/sample time':
       *  y = K where K = ( w * Ts )
       *   */
      Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = 0.05F *
        Torque_Control_Y.TQ_Check4;

      /* Switch: '<S110>/Switch' incorporates:
       *  RelationalOperator: '<S110>/UpperRelop'
       */
      if (!(rtb_UkYk1 < Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq)) {
        /* Product: '<S109>/delta fall limit' */
        Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = rtb_UkYk1;
      }

      /* End of Switch: '<S110>/Switch' */
    }

    /* End of Switch: '<S110>/Switch2' */

    /* Sum: '<S109>/Difference Inputs2' incorporates:
     *  Delay: '<S109>/Delay'
     *
     * Block description for '<S109>/Difference Inputs2':
     *
     *  Add in CPU
     */
    Torque_Control_B.DifferenceInputs2_b =
      Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq +
      Torque_Control_DW.Delay_DSTATE_fg;

    /* Update for Delay: '<S109>/Delay' */
    Torque_Control_DW.icLoad_f = false;
    Torque_Control_DW.Delay_DSTATE_fg = Torque_Control_B.DifferenceInputs2_b;
    if (Torque_Control_DW.Subsystem1_MODE) {
      /* Disable for Sum: '<S111>/Difference Inputs2' incorporates:
       *  Outport: '<S9>/TQ_TEMP_MotTorq_TorqCmd'
       *
       * Block description for '<S111>/Difference Inputs2':
       *
       *  Add in CPU
       */
      Torque_Control_B.DifferenceInputs2 = 0.0F;
      Torque_Control_DW.Subsystem1_MODE = false;
    }

    Torque_Control_DW.Delay_DSTATE = Torque_Control_B.DifferenceInputs2_b;
  } else {
    if (Torque_Control_DW.Subsystem_MODE) {
      /* Disable for Sum: '<S109>/Difference Inputs2' incorporates:
       *  Outport: '<S8>/TQ_TEMP_MotSpd_TorqCmd'
       *
       * Block description for '<S109>/Difference Inputs2':
       *
       *  Add in CPU
       */
      Torque_Control_B.DifferenceInputs2_b = 0.0F;
      Torque_Control_DW.Subsystem_MODE = false;
    }

    if (!Torque_Control_DW.Subsystem1_MODE) {
      /* InitializeConditions for Delay: '<S111>/Delay' */
      Torque_Control_DW.icLoad = true;
      Torque_Control_DW.Subsystem1_MODE = true;
    }

    /* Switch: '<S9>/Switch11' incorporates:
     *  Inport: '<Root>/TQ_IN_bCmdForw'
     */
    if (Torque_Control_U.TQ_IN_bCmdForw) {
      /* Outport: '<Root>/TQ_Check5' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotTorq'
       *  Lookup_n-D: '<S9>/GearD_TorqForwardUp'
       */
      Torque_Control_Y.TQ_Check5 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotTorq, GearD_ForwardMotTorq_X,
         GearD_ForwardGain_Z, 7U);
    } else {
      /* Outport: '<Root>/TQ_Check5' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotTorq'
       *  Lookup_n-D: '<S9>/GearR_TorqBackwardUp'
       */
      Torque_Control_Y.TQ_Check5 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotTorq, GearR_BackwardMotTorq_X,
         GearR_BackwardGain_Z, 6U);
    }

    /* End of Switch: '<S9>/Switch11' */

    /* Switch: '<S9>/Switch7' incorporates:
     *  Inport: '<Root>/TQ_IN_bMCUSpdMode'
     */
    if (Torque_Control_U.TQ_IN_bMCUSpdMode) {
      /* Outport: '<Root>/TQ_Check7' incorporates:
       *  Gain: '<S9>/Gain2'
       *  Outport: '<Root>/TQ_Check5'
       */
      Torque_Control_Y.TQ_Check7 = 3.0F * Torque_Control_Y.TQ_Check5;
    } else {
      /* Outport: '<Root>/TQ_Check7' incorporates:
       *  Outport: '<Root>/TQ_Check5'
       */
      Torque_Control_Y.TQ_Check7 = Torque_Control_Y.TQ_Check5;
    }

    /* End of Switch: '<S9>/Switch7' */

    /* Product: '<S109>/delta fall limit' incorporates:
     *  Outport: '<Root>/TQ_Check7'
     *  Product: '<S111>/delta rise limit'
     *  SampleTimeMath: '<S111>/sample time'
     *
     * About '<S111>/sample time':
     *  y = K where K = ( w * Ts )
     *   */
    Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = Torque_Control_Y.TQ_Check7 *
      0.05F;

    /* Delay: '<S111>/Delay' */
    if (Torque_Control_DW.icLoad) {
      Torque_Control_DW.Delay_DSTATE_f = Torque_Control_Y.TQ_OUT_sOutputTorqCmd;
    }

    /* Sum: '<S111>/Difference Inputs1' incorporates:
     *  Delay: '<S111>/Delay'
     *
     * Block description for '<S111>/Difference Inputs1':
     *
     *  Add in CPU
     */
    rtb_UkYk1 = Torque_Control_Y.TQ_OUT_sOutputTorqCmd -
      Torque_Control_DW.Delay_DSTATE_f;

    /* Switch: '<S9>/Switch9' incorporates:
     *  Inport: '<Root>/TQ_IN_bCmdForw'
     */
    if (Torque_Control_U.TQ_IN_bCmdForw) {
      /* Outport: '<Root>/TQ_Check6' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotTorq'
       *  Lookup_n-D: '<S9>/GearD_TorqForwardDown'
       */
      Torque_Control_Y.TQ_Check6 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotTorq, GearD_ForwardMotTorq_X1,
         GearD_ForwardDrop_Z, 7U);
    } else {
      /* Outport: '<Root>/TQ_Check6' incorporates:
       *  Inport: '<Root>/TQ_IN_sMotTorq'
       *  Lookup_n-D: '<S9>/GearR_TorqBackwardDown'
       */
      Torque_Control_Y.TQ_Check6 = Torque_Control_look1_i_rQYGWmZ3
        (Torque_Control_U.TQ_IN_sMotTorq, GearR_BackwardMotTorq_X1,
         GearR_BackwardDrop_Z, 6U);
    }

    /* End of Switch: '<S9>/Switch9' */

    /* Switch: '<S9>/Switch12' incorporates:
     *  Inport: '<Root>/TQ_IN_bMCUSpdMode'
     */
    if (Torque_Control_U.TQ_IN_bMCUSpdMode) {
      /* Outport: '<Root>/TQ_Check8' incorporates:
       *  Gain: '<S9>/Gain3'
       *  Outport: '<Root>/TQ_Check6'
       */
      Torque_Control_Y.TQ_Check8 = 3.0F * Torque_Control_Y.TQ_Check6;
    } else {
      /* Outport: '<Root>/TQ_Check8' incorporates:
       *  Outport: '<Root>/TQ_Check6'
       */
      Torque_Control_Y.TQ_Check8 = Torque_Control_Y.TQ_Check6;
    }

    /* End of Switch: '<S9>/Switch12' */

    /* Switch: '<S112>/Switch2' incorporates:
     *  RelationalOperator: '<S112>/LowerRelop1'
     */
    if (!(rtb_UkYk1 > Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq)) {
      /* Product: '<S109>/delta fall limit' incorporates:
       *  Outport: '<Root>/TQ_Check8'
       *  Product: '<S111>/delta fall limit'
       *  SampleTimeMath: '<S111>/sample time'
       *
       * About '<S111>/sample time':
       *  y = K where K = ( w * Ts )
       *   */
      Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = 0.05F *
        Torque_Control_Y.TQ_Check8;

      /* Switch: '<S112>/Switch' incorporates:
       *  RelationalOperator: '<S112>/UpperRelop'
       */
      if (!(rtb_UkYk1 < Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq)) {
        /* Product: '<S109>/delta fall limit' */
        Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = rtb_UkYk1;
      }

      /* End of Switch: '<S112>/Switch' */
    }

    /* End of Switch: '<S112>/Switch2' */

    /* Sum: '<S111>/Difference Inputs2' incorporates:
     *  Delay: '<S111>/Delay'
     *
     * Block description for '<S111>/Difference Inputs2':
     *
     *  Add in CPU
     */
    Torque_Control_B.DifferenceInputs2 =
      Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq +
      Torque_Control_DW.Delay_DSTATE_f;

    /* Update for Delay: '<S111>/Delay' */
    Torque_Control_DW.icLoad = false;
    Torque_Control_DW.Delay_DSTATE_f = Torque_Control_B.DifferenceInputs2;
    Torque_Control_DW.Delay_DSTATE = Torque_Control_B.DifferenceInputs2;
  }

  /* End of Switch: '<Root>/Switch5' */
  /* End of Outputs for SubSystem: '<Root>/Subsystem' */
  /* End of Outputs for SubSystem: '<Root>/Subsystem1' */

  /* Outport: '<Root>/TQ_OUT_sVCUTorqCmd' incorporates:
   *  Delay: '<Root>/Delay'
   */
  Torque_Control_Y.TQ_OUT_sVCUTorqCmd = Torque_Control_DW.Delay_DSTATE;

  /* Outport: '<Root>/R_JudgeFlg' */
  Torque_Control_Y.R_JudgeFlg = Torque_Control_Y.TQ_TEMP_bAllowFBFlg;

  /* Outport: '<Root>/TQ_ROUT' */
  Torque_Control_Y.TQ_ROUT = Torque_Control_Y.TQ_TEMP_sBrakePert;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControl_gw = rtb_Delay;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlInp =
    Torque_Control_Y.TQ_TEMP_sAccelPert;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_n =
    Torque_Control_Y.TQ_TEMP_sVeilAllowDriveTorq;

  /* Outport: '<Root>/TQ_TEMP_sMotAllowDriveTorq' */
  Torque_Control_Y.TQ_TEMP_sMotAllowDriveTorq =
    Torque_Control_Y.TQ_TEMP_sVeilAllowBrakeTorq;

  /* Switch: '<S3>/Switch1' incorporates:
   *  Abs: '<S3>/Abs12'
   *  Inport: '<Root>/CAL_sRatedMotSpd'
   *  RelationalOperator: '<S3>/Relational Operator2'
   */
  if (!(rtb_Abs14 >= Torque_Control_U.CAL_sRatedMotSpd)) {
    rtb_Abs14 = Torque_Control_U.CAL_sRatedMotSpd;
  }

  /* Saturate: '<S6>/Saturation1' incorporates:
   *  Abs: '<S3>/Abs2'
   *  Constant: '<S3>/Constant7'
   *  Inport: '<Root>/TQ_IN_sBMSChgCurr30s'
   *  Inport: '<Root>/TQ_IN_sBMSVolt'
   *  Product: '<S3>/Divide3'
   *  Switch: '<S3>/Switch1'
   */
  Torque_Control_Y.TQ_TEMP_sBrakePert = fabsf
    (Torque_Control_U.TQ_IN_sBMSChgCurr30s * Torque_Control_U.TQ_IN_sBMSVolt *
     9.55F / rtb_Abs14);

  /* Product: '<S109>/delta fall limit' incorporates:
   *  Abs: '<S3>/Abs10'
   *  Inport: '<Root>/TQ_IN_sMCUTorqLower'
   */
  Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = fabsf
    (Torque_Control_U.TQ_IN_sMCUTorqLower);

  /* Abs: '<S3>/Abs8' incorporates:
   *  Inport: '<Root>/CAL_i16MaxBrakeTorq'
   */
  if (Torque_Control_U.CAL_i16MaxBrakeTorq < 0) {
    tmp = (uint16_T)-Torque_Control_U.CAL_i16MaxBrakeTorq;
  } else {
    tmp = (uint16_T)Torque_Control_U.CAL_i16MaxBrakeTorq;
  }

  /* MinMax: '<S3>/MinMax1' incorporates:
   *  Abs: '<S3>/Abs8'
   */
  Torque_Control_Y.TQ_TEMP_sVeilAllowBrakeTorq = fminf(fminf(fminf
    (Torque_Control_Y.TQ_TEMP_sBrakePert, (real32_T)tmp),
    Torque_Control_Y.TQ_TEMP_sPowerAllowTorq),
    Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq);

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_c =
    Torque_Control_Y.TQ_TEMP_sVeilAllowBrakeTorq;

  /* Abs: '<S3>/Abs9' incorporates:
   *  Inport: '<Root>/CAL_i16MaxSlideTorq'
   */
  if (Torque_Control_U.CAL_i16MaxSlideTorq < 0) {
    tmp = (uint16_T)-Torque_Control_U.CAL_i16MaxSlideTorq;
  } else {
    tmp = (uint16_T)Torque_Control_U.CAL_i16MaxSlideTorq;
  }

  /* Product: '<S109>/delta fall limit' incorporates:
   *  Abs: '<S3>/Abs9'
   *  MinMax: '<S3>/MinMax2'
   */
  Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq = fminf(fminf
    (Torque_Control_Y.TQ_TEMP_sBrakePert,
     Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq), (real32_T)tmp);

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_d =
    Torque_Control_Y.TQ_TEMP_sVeilAllowSlideTorq;

  /* Outport: '<Root>/TQ_TEMP_sBMSAllowBrakeTorq' */
  Torque_Control_Y.TQ_TEMP_sBMSAllowBrakeTorq =
    Torque_Control_Y.TQ_TEMP_sBrakePert;

  /* Outport: '<Root>/TQ_TEMP_sVeilSpd' incorporates:
   *  DiscreteIntegrator: '<S120>/Integrator'
   */
  Torque_Control_Y.TQ_TEMP_sVeilSpd = Torque_Control_DW.Integrator_DSTATE;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  DiscreteIntegrator: '<S120>/Integrator'
   */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p =
    Torque_Control_DW.Integrator_DSTATE;

  /* Logic: '<S7>/Logical Operator' incorporates:
   *  Constant: '<S108>/Constant'
   *  Inport: '<Root>/CAL_sAllowFBSOCSET'
   *  Inport: '<Root>/TQ_IN_bABSSt'
   *  Inport: '<Root>/TQ_IN_bSnowMode'
   *  Inport: '<Root>/TQ_IN_sBMSSOC'
   *  Inport: '<Root>/TQ_IN_sMotSpd'
   *  RelationalOperator: '<S105>/Compare'
   *  RelationalOperator: '<S106>/Compare'
   *  RelationalOperator: '<S108>/Compare'
   *  RelationalOperator: '<S7>/Relational Operator2'
   */
  Torque_Control_Y.TQ_TEMP_bAllowFBFlg = ((Torque_Control_U.TQ_IN_sMotSpd >
    100.0F) && (!Torque_Control_U.TQ_IN_bABSSt) &&
    (Torque_Control_U.TQ_IN_sBMSSOC <= Torque_Control_U.CAL_sAllowFBSOCSET) && (
    !Torque_Control_U.TQ_IN_bSnowMode));

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControl_g3 =
    Torque_Control_Y.TQ_TEMP_bAllowFBFlg;

  /* Saturate: '<S6>/Saturation1' incorporates:
   *  Inport: '<Root>/TQ_IN_sBrakePert'
   *  Lookup_n-D: '<S6>/Torque_BrakePert'
   */
  Torque_Control_Y.TQ_TEMP_sBrakePert = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_U.TQ_IN_sBrakePert, BrakePert, Torque_BrakePert, 3U);

  /* Saturate: '<S6>/Saturation1' */
  if (Torque_Control_Y.TQ_TEMP_sBrakePert > 1.0F) {
    /* Saturate: '<S6>/Saturation1' */
    Torque_Control_Y.TQ_TEMP_sBrakePert = 1.0F;
  } else if (Torque_Control_Y.TQ_TEMP_sBrakePert < 0.0F) {
    /* Saturate: '<S6>/Saturation1' */
    Torque_Control_Y.TQ_TEMP_sBrakePert = 0.0F;
  }

  /* End of Saturate: '<S6>/Saturation1' */

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' */
  Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_g =
    Torque_Control_Y.TQ_TEMP_sBrakePert;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bBrakeSW'
   */
  Torque_Control_B.TQ_IN_bBrakeSW = Torque_Control_U.TQ_IN_bBrakeSW;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_sAccelPert'
   */
  Torque_Control_B.TQ_IN_sAccelPert = Torque_Control_U.TQ_IN_sAccelPert;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_sBrakePert'
   */
  Torque_Control_B.TQ_IN_sBrakePert = Torque_Control_U.TQ_IN_sBrakePert;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bDoorOpenSigl'
   */
  Torque_Control_B.TQ_IN_bDoorOpenSigl = Torque_Control_U.TQ_IN_bDoorOpenSigl;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bDoorUnlockReq'
   */
  Torque_Control_B.TQ_IN_bDoorUnlockReq = Torque_Control_U.TQ_IN_bDoorUnlockReq;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bCmdForw'
   */
  Torque_Control_B.TQ_IN_bCmdForw = Torque_Control_U.TQ_IN_bCmdForw;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bCmdNtw'
   */
  Torque_Control_B.TQ_IN_bCmdNtw = Torque_Control_U.TQ_IN_bCmdNtw;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bMCUEnFB'
   */
  Torque_Control_B.TQ_IN_bMCUEnFB = Torque_Control_U.TQ_IN_bMCUEnFB;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bReady'
   */
  Torque_Control_B.TQ_IN_bReady = Torque_Control_U.TQ_IN_bReady;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bAirPressLow'
   */
  Torque_Control_B.TQ_IN_bAirPressLow = Torque_Control_U.TQ_IN_bAirPressLow;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bHandBrake'
   */
  Torque_Control_B.TQ_IN_bHandBrake = Torque_Control_U.TQ_IN_bHandBrake;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_u8VeilFltLvl'
   */
  Torque_Control_B.TQ_IN_u8VeilFltLvl = Torque_Control_U.TQ_IN_u8VeilFltLvl;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/CAL_i16MaxCrawlTorq'
   */
  Torque_Control_B.CAL_i16MaxCrawlTorq = Torque_Control_U.CAL_i16MaxCrawlTorq;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_sMotTorq'
   */
  Torque_Control_B.TQ_IN_sMotTorq = Torque_Control_U.TQ_IN_sMotTorq;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_sMotSpd'
   */
  Torque_Control_B.TQ_IN_sMotSpd = Torque_Control_U.TQ_IN_sMotSpd;

  /* RateTransition generated from: '<Root>/GEAR_D_TorqueControl' incorporates:
   *  Inport: '<Root>/TQ_IN_bAccelSW'
   */
  Torque_Control_B.TQ_IN_bAccelSW = Torque_Control_U.TQ_IN_bAccelSW;

  /* Update for DiscreteIntegrator: '<S120>/Integrator' incorporates:
   *  Constant: '<S114>/Time constant'
   *  MinMax: '<S114>/Max'
   *  Product: '<S113>/1//T'
   *  Sum: '<S113>/Sum1'
   */
  Torque_Control_DW.Integrator_IC_LOADING = 0U;
  Torque_Control_DW.Integrator_DSTATE += 0.05F * (1.0F / (real32_T)fmax
    (Torque_Control_B.Probe[0], 0.25) *
    (Torque_Control_Y.TQ_TEMP_sVeilSpdPreFltr -
     Torque_Control_DW.Integrator_DSTATE));
  Torque_Control_DW.Integrator_PrevResetState = (int8_T)rtb_LogicalOperator;
}

/* Model step function for TID1 */
void Torque_Control_step1(void)        /* Explicit Task: GEAR_D_TorqueControl */
{
  real_T rtb_Product3;
  int32_T tmp_0;
  real32_T rtb_Abs5;
  real32_T tmp;
  boolean_T guard1;
  boolean_T rtb_Compare_p;
  boolean_T rtb_LogicalOperator4_g_tmp;
  boolean_T rtb_LogicalOperator_i_tmp;
  boolean_T rtb_LogicalOperator_n_tmp;

  /* Outputs for Atomic SubSystem: '<Root>/GEAR_D_TorqueControl' */
  /* MATLAB Function: '<S4>/RegenFactor' */
  if (!Torque_Control_DW.RegenState_not_empty) {
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 20.0F) {
      Torque_Control_DW.RegenState = 4U;
      Torque_Control_DW.RegenState_not_empty = true;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 15.0F) {
      Torque_Control_DW.RegenState = 3U;
      Torque_Control_DW.RegenState_not_empty = true;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 10.0F) {
      Torque_Control_DW.RegenState = 2U;
      Torque_Control_DW.RegenState_not_empty = true;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 7.0F) {
      Torque_Control_DW.RegenState = 1U;
      Torque_Control_DW.RegenState_not_empty = true;
    } else {
      Torque_Control_DW.RegenState = 0U;
      Torque_Control_DW.RegenState_not_empty = true;
    }
  }

  switch (Torque_Control_DW.RegenState) {
   case 0U:
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 7.0F) {
      Torque_Control_DW.RegenState = 1U;
    }
    break;

   case 1U:
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 10.0F) {
      Torque_Control_DW.RegenState = 2U;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 5.0F) {
      Torque_Control_DW.RegenState = 0U;
    }
    break;

   case 2U:
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 15.0F) {
      Torque_Control_DW.RegenState = 3U;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 8.0F) {
      Torque_Control_DW.RegenState = 1U;
    }
    break;

   case 3U:
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 20.0F) {
      Torque_Control_DW.RegenState = 4U;
    } else if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 13.0F) {
      Torque_Control_DW.RegenState = 2U;
    }
    break;

   case 4U:
    if (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 17.0F) {
      Torque_Control_DW.RegenState = 3U;
    }
    break;

   default:
    Torque_Control_DW.RegenState = 4U;
    break;
  }

  switch (Torque_Control_DW.RegenState) {
   case 0U:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 0.0;
    break;

   case 1U:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 0.25;
    break;

   case 2U:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 0.5;
    break;

   case 3U:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 0.75;
    break;

   case 4U:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 1.0;
    break;

   default:
    Torque_Control_Y.TQ_TEMP_sForwordFBK = 0.0;
    break;
  }

  /* End of MATLAB Function: '<S4>/RegenFactor' */

  /* Switch: '<S4>/Switch' incorporates:
   *  Inport: '<Root>/CAL_bEBSUseFlg'
   *  Inport: '<Root>/CAL_bFootBrakeUseFlg'
   *  Inport: '<Root>/TQ_IN_bEBSBrakeReq'
   *  Inport: '<Root>/TQ_IN_sEBSBrakePert'
   *  Logic: '<S4>/Logical Operator12'
   *  Product: '<S4>/Product4'
   *  Switch: '<S4>/Switch7'
   */
  if (Torque_Control_U.TQ_IN_bEBSBrakeReq && Torque_Control_U.CAL_bEBSUseFlg) {
    rtb_Product3 = Torque_Control_Y.TQ_TEMP_sForwordFBK *
      Torque_Control_U.TQ_IN_sEBSBrakePert *
      Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_c;
  } else if (Torque_Control_U.CAL_bFootBrakeUseFlg) {
    /* Switch: '<S4>/Switch7' incorporates:
     *  Product: '<S4>/Product2'
     */
    rtb_Product3 = (real32_T)(Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_c *
      Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_g *
      Torque_Control_Y.TQ_TEMP_sForwordFBK);
  } else {
    rtb_Product3 = 0.0;
  }

  /* End of Switch: '<S4>/Switch' */

  /* Abs: '<S4>/Abs' */
  if (rtb_Product3 < 0.0) {
    rtb_Abs5 = (real32_T)-rtb_Product3;
  } else {
    rtb_Abs5 = (real32_T)rtb_Product3;
  }

  /* End of Abs: '<S4>/Abs' */

  /* Product: '<S4>/Product3' incorporates:
   *  Inport: '<Root>/TQ_IN_u8RetarderGear'
   */
  rtb_Product3 = Torque_Control_Y.TQ_TEMP_sForwordFBK *
    Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_d * (real_T)
    Torque_Control_U.TQ_IN_u8RetarderGear;

  /* Abs: '<S4>/Abs1' */
  if (rtb_Product3 < 0.0) {
    /* Gain: '<S4>/Gain1' */
    Torque_Control_Y.Check_D_SlideTorque = -(real32_T)-rtb_Product3;
    tmp = (real32_T)-rtb_Product3;
  } else {
    /* Gain: '<S4>/Gain1' */
    Torque_Control_Y.Check_D_SlideTorque = -(real32_T)rtb_Product3;
    tmp = (real32_T)rtb_Product3;
  }

  /* MinMax: '<S4>/MinMax1' incorporates:
   *  Abs: '<S4>/Abs1'
   *  Gain: '<S4>/Gain'
   *  Gain: '<S4>/Gain1'
   */
  Torque_Control_Y.Check_D_BrakeTorque = fminf(-rtb_Abs5, -tmp);

  /* Relay: '<S4>/Relay' incorporates:
   *  Relay: '<S4>/Relay1'
   */
  rtb_Compare_p = !(Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p <= 8.0F);
  Torque_Control_DW.Relay_Mode_a =
    ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 10.0F) ||
     (rtb_Compare_p && Torque_Control_DW.Relay_Mode_a));

  /* Logic: '<S4>/Logical Operator5' incorporates:
   *  Logic: '<S18>/Logical Operator1'
   *  Logic: '<S4>/Logical Operator2'
   */
  rtb_LogicalOperator4_g_tmp = !Torque_Control_B.TQ_IN_bAccelSW;

  /* Logic: '<S4>/Logical Operator4' incorporates:
   *  Constant: '<S15>/Constant'
   *  Logic: '<S4>/Logical Operator5'
   *  RelationalOperator: '<S15>/Compare'
   *  Relay: '<S4>/Relay'
   */
  Torque_Control_Y.BD_JudgeFlg = (rtb_LogicalOperator4_g_tmp &&
    Torque_Control_B.TQ_IN_bBrakeSW && (Torque_Control_B.TQ_IN_sAccelPert <=
    0.05F) && Torque_Control_B.TmpRTBAtGEAR_D_TorqueControl_g3 &&
    Torque_Control_DW.Relay_Mode_a);

  /* Relay: '<S4>/Relay2' */
  Torque_Control_DW.Relay2_Mode = ((Torque_Control_B.TQ_IN_sAccelPert >= 0.1F) ||
    ((!(Torque_Control_B.TQ_IN_sAccelPert <= 0.0F)) &&
     Torque_Control_DW.Relay2_Mode));

  /* Logic: '<S4>/Logical Operator1' incorporates:
   *  Logic: '<S18>/Logical Operator2'
   *  Logic: '<S4>/Logical Operator8'
   */
  rtb_LogicalOperator_n_tmp = !Torque_Control_B.TQ_IN_bBrakeSW;

  /* Logic: '<S4>/Logical Operator' incorporates:
   *  Logic: '<S4>/Logical Operator1'
   *  Relay: '<S4>/Relay2'
   */
  Torque_Control_Y.DS_JudgeFlg = (Torque_Control_B.TQ_IN_bAccelSW &&
    rtb_LogicalOperator_n_tmp && Torque_Control_DW.Relay2_Mode);

  /* MATLAB Function: '<S4>/DoorSpdLimitK' incorporates:
   *  Constant: '<S4>/Constant4'
   *  DataTypeConversion: '<S4>/Data Type Conversion32'
   */
  if (Torque_Control_B.TQ_IN_sMotSpd < 0.0F) {
    Torque_Control_Y.TQ_TEMP_sForwordLimitK = 1.0;
  } else if ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 20.0F) &&
             (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 0.0F)) {
    Torque_Control_Y.TQ_TEMP_sForwordLimitK = 1.0;
  } else if ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 20.0F) &&
             (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p < 30.0F)) {
    Torque_Control_Y.TQ_TEMP_sForwordLimitK = 0.01 *
      ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p - 30.0) *
       (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p - 30.0));
  } else {
    Torque_Control_Y.TQ_TEMP_sForwordLimitK = 0.0;
  }

  /* End of MATLAB Function: '<S4>/DoorSpdLimitK' */

  /* Switch: '<S4>/Switch11' incorporates:
   *  Constant: '<S4>/Constant1'
   */
  if (Torque_Control_B.TQ_IN_bDoorOpenSigl) {
    tmp_0 = Torque_Control_B.TQ_IN_bDoorUnlockReq;
  } else {
    tmp_0 = 0;
  }

  /* Switch: '<S4>/Switch2' incorporates:
   *  Constant: '<S14>/Constant'
   *  Logic: '<S4>/Logical Operator3'
   *  RelationalOperator: '<S14>/Compare'
   *  Switch: '<S4>/Switch11'
   */
  if (tmp_0 <= 0) {
    Torque_Control_Y.TQ_TEMP_sForwordLimitK =
      ((!Torque_Control_B.TQ_IN_bDoorOpenSigl) ||
       (!(Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p <= 5.0F)));
  }

  /* End of Switch: '<S4>/Switch2' */

  /* Switch: '<S4>/Switch8' incorporates:
   *  Inport: '<Root>/CAL_bEBSUseFlg'
   *  Inport: '<Root>/TQ_IN_bEBSDriveReq'
   *  Logic: '<S4>/Logical Operator13'
   */
  if (Torque_Control_U.TQ_IN_bEBSDriveReq && Torque_Control_U.CAL_bEBSUseFlg) {
    /* Product: '<S4>/Product5' incorporates:
     *  Inport: '<Root>/TQ_IN_sEBSDrivePert'
     */
    rtb_Product3 = Torque_Control_Y.TQ_TEMP_sForwordLimitK *
      Torque_Control_U.TQ_IN_sEBSDrivePert *
      Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_n;

    /* Abs: '<S4>/Abs3' */
    if (rtb_Product3 < 0.0) {
      tmp = (real32_T)-rtb_Product3;
    } else {
      tmp = (real32_T)rtb_Product3;
    }

    /* Switch: '<S4>/Switch8' incorporates:
     *  Abs: '<S4>/Abs3'
     *  Abs: '<S4>/Abs4'
     *  MinMax: '<S4>/Min'
     *  Product: '<S4>/Product1'
     */
    Torque_Control_Y.Check_D_DriveTorque = fminf(tmp, fabsf((real32_T)
      (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_n *
       Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlInp *
       Torque_Control_Y.TQ_TEMP_sForwordLimitK)));
  } else {
    /* Switch: '<S4>/Switch8' incorporates:
     *  Abs: '<S4>/Abs4'
     *  Product: '<S4>/Product1'
     */
    Torque_Control_Y.Check_D_DriveTorque = fabsf((real32_T)
      (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_n *
       Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlInp *
       Torque_Control_Y.TQ_TEMP_sForwordLimitK));
  }

  /* End of Switch: '<S4>/Switch8' */

  /* Road speed limiter (replaces Chart '<S4>/Chart').
   *  Inport:  '<Root>/CAL_sDVeilSpdLimit'  speed limit [km/h]
   *  Inport:  '<Root>/maxRslRegenTrq'      max regen while limiting [Nm]
   *  Speed:   vehicle speed filter output (TmpRTBAtGEAR_D_TorqueControlI_p)
   *  Demand:  Check_D_DriveTorque
   *  Calibration: RSL_Kp, RSL_Ki, RSL_EngBand, RSL_RefRate, RSL_TrqRate,
   *               RSL_LimitMin (RoadSpeedLimiter.c)
   *  Inports Rsl_Kp, Rsl_ki, Rsl_ICont_Max, Rsl_DltaSoftDiff,
   *  Rsl_ReleaseDelta, Rsl_Trq_diff_SMax, Rsl_Trq_diff_PIMax are no longer used.
   *
   *  Outports reused for logging:
   *    RslState        0 = off, 1 = armed, 2 = limiting
   *    Rsl_PCont       proportional term        [Nm]
   *    Rsl_ICont       integral term            [Nm]
   *    Rsl_Pid_TrqDlta speed error vRef - v     [km/h]
   *    TrqSoftDelta    speed reference vRef     [km/h]
   */
  Torque_Control_B.TrqUBound = RSL_Step(&Torque_Control_RSL,
    Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p,
    Torque_Control_U.CAL_sDVeilSpdLimit,
    (real32_T)Torque_Control_Y.Check_D_DriveTorque,
    -fminf(fminf(Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_c,
                 Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_d),
           fabsf((real32_T)Torque_Control_U.maxRslRegenTrq)));
  Torque_Control_Y.RslState = Torque_Control_RSL.state;
  Torque_Control_Y.Rsl_PCont = Torque_Control_RSL.P;
  Torque_Control_Y.Rsl_ICont = Torque_Control_RSL.I;
  Torque_Control_Y.Rsl_Pid_TrqDlta = Torque_Control_RSL.e;
  Torque_Control_Y.TrqSoftDelta = Torque_Control_RSL.vRef;

  /* End of road speed limiter */

  /* MinMax: '<S4>/Max1' incorporates:
   *  Gain: '<S4>/Gain2'
   *  MinMax: '<S4>/Min1'
   */
  Torque_Control_Y.TrqUBound = fmax(-fminf
    (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_c,
     Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_d),
    Torque_Control_B.TrqUBound);

  /* Relay: '<S4>/Relay1' */
  Torque_Control_DW.Relay1_Mode =
    ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 10.0F) ||
     (rtb_Compare_p && Torque_Control_DW.Relay1_Mode));

  /* Logic: '<S4>/Logical Operator6' incorporates:
   *  Constant: '<S13>/Constant'
   *  Inport: '<Root>/TQ_IN_u8RetarderGear'
   *  Logic: '<S4>/NOT'
   *  RelationalOperator: '<S13>/Compare'
   *  Relay: '<S4>/Relay1'
   *  Relay: '<S4>/Relay2'
   */
  Torque_Control_Y.SC_JudgeFlg = (rtb_LogicalOperator4_g_tmp &&
    rtb_LogicalOperator_n_tmp && (!Torque_Control_DW.Relay2_Mode) &&
    Torque_Control_B.TmpRTBAtGEAR_D_TorqueControl_g3 &&
    Torque_Control_DW.Relay1_Mode && (Torque_Control_U.TQ_IN_u8RetarderGear > 0));

  /* Logic: '<S19>/Logical Operator' incorporates:
   *  Constant: '<S29>/Constant'
   *  Constant: '<S30>/Constant'
   *  Constant: '<S31>/Constant'
   *  Constant: '<S33>/Constant'
   *  Inport: '<Root>/CAL_bDCruiseFlg'
   *  Inport: '<Root>/TQ_IN_bAEBSFlg'
   *  Inport: '<Root>/TQ_IN_bCCVS2Flg'
   *  Inport: '<Root>/TQ_IN_bCruiseSW'
   *  Inport: '<Root>/TQ_IN_bESCFlg'
   *  Inport: '<Root>/TQ_IN_u8RetarderGear'
   *  Logic: '<S19>/Logical Operator1'
   *  Logic: '<S19>/Logical Operator2'
   *  Logic: '<S19>/Logical Operator3'
   *  RelationalOperator: '<S29>/Compare'
   *  RelationalOperator: '<S30>/Compare'
   *  RelationalOperator: '<S31>/Compare'
   *  RelationalOperator: '<S33>/Compare'
   */
  Torque_Control_Y.TQ_TEMP_bCruiseJudeg = ((Torque_Control_B.TQ_IN_sAccelPert <=
    0.05F) && Torque_Control_U.CAL_bDCruiseFlg &&
    (Torque_Control_B.TQ_IN_sBrakePert <= 0.05F) &&
    (Torque_Control_U.TQ_IN_u8RetarderGear == 0) &&
    Torque_Control_U.TQ_IN_bCruiseSW && (!Torque_Control_U.TQ_IN_bESCFlg) &&
    (!Torque_Control_U.TQ_IN_bAEBSFlg) && (!Torque_Control_U.TQ_IN_bCCVS2Flg) &&
    (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p > 40.0F));

  /* Chart: '<S19>/Chart1' */
  if (Torque_Control_DW.is_active_c7_Torque_Control == 0) {
    Torque_Control_DW.is_active_c7_Torque_Control = 1U;
    if (Torque_Control_Y.TQ_TEMP_bCruiseJudeg) {
      Torque_Control_DW.is_c7_Torque_Control = Torque_Control_IN_ON;

      /* Outport: '<Root>/TQ_OUT_bCruiseJudeg' */
      Torque_Control_Y.TQ_OUT_bCruiseJudeg = true;

      /* Outport: '<Root>/TQ_OUT_bCruiseOff' */
      Torque_Control_Y.TQ_OUT_bCruiseOff = false;
      Torque_Control_DW.TQ_IN_u16CruiseCnt = 0U;
    } else {
      Torque_Control_DW.is_c7_Torque_Control = Torque_Control_IN_OFFLAST;

      /* Outport: '<Root>/TQ_OUT_bCruiseJudeg' */
      Torque_Control_Y.TQ_OUT_bCruiseJudeg = false;

      /* Outport: '<Root>/TQ_OUT_bCruiseOff' */
      Torque_Control_Y.TQ_OUT_bCruiseOff = false;
      Torque_Control_DW.TQ_IN_u16CruiseCnt = 0U;
    }
  } else {
    switch (Torque_Control_DW.is_c7_Torque_Control) {
     case Torque_Control_IN_OFF:
      if (Torque_Control_DW.TQ_IN_u16CruiseCnt >= 100) {
        Torque_Control_DW.is_c7_Torque_Control = Torque_Control_IN_OFFLAST;

        /* Outport: '<Root>/TQ_OUT_bCruiseJudeg' */
        Torque_Control_Y.TQ_OUT_bCruiseJudeg = false;

        /* Outport: '<Root>/TQ_OUT_bCruiseOff' */
        Torque_Control_Y.TQ_OUT_bCruiseOff = false;
        Torque_Control_DW.TQ_IN_u16CruiseCnt = 0U;
      } else {
        Torque_Control_DW.TQ_IN_u16CruiseCnt++;
      }
      break;

     case Torque_Control_IN_OFFLAST:
      if (Torque_Control_Y.TQ_TEMP_bCruiseJudeg) {
        Torque_Control_DW.is_c7_Torque_Control = Torque_Control_IN_ON;

        /* Outport: '<Root>/TQ_OUT_bCruiseJudeg' */
        Torque_Control_Y.TQ_OUT_bCruiseJudeg = true;

        /* Outport: '<Root>/TQ_OUT_bCruiseOff' */
        Torque_Control_Y.TQ_OUT_bCruiseOff = false;
        Torque_Control_DW.TQ_IN_u16CruiseCnt = 0U;
      }
      break;

     default:
      /* case IN_ON: */
      if (!Torque_Control_Y.TQ_TEMP_bCruiseJudeg) {
        Torque_Control_DW.is_c7_Torque_Control = Torque_Control_IN_OFF;

        /* Outport: '<Root>/TQ_OUT_bCruiseJudeg' */
        Torque_Control_Y.TQ_OUT_bCruiseJudeg = false;

        /* Outport: '<Root>/TQ_OUT_bCruiseOff' */
        Torque_Control_Y.TQ_OUT_bCruiseOff = true;
      }
      break;
    }
  }

  /* End of Chart: '<S19>/Chart1' */

  /* Chart: '<S19>/Chart2' incorporates:
   *  Inport: '<Root>/TQ_IN_bCruiseADD'
   *  Inport: '<Root>/TQ_IN_bCruiseSUB'
   *  Outport: '<Root>/TQ_OUT_bCruiseJudeg'
   */
  if (Torque_Control_DW.is_active_c8_Torque_Control == 0) {
    Torque_Control_DW.is_active_c8_Torque_Control = 1U;
    Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP1;

    /* Outport: '<Root>/STEP_CruiseControl' */
    Torque_Control_Y.STEP_CruiseControl = 0.0;

    /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
    Torque_Control_Y.TQ_OUT_bCruiseControl = false;

    /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
    Torque_Control_Y.TQ_OUT_sCruiseSetSpd = 0.0F;
  } else {
    switch (Torque_Control_DW.is_c8_Torque_Control) {
     case Torque_Control_IN_STEP1:
      /* Outport: '<Root>/STEP_CruiseControl' */
      Torque_Control_Y.STEP_CruiseControl = 0.0;
      if (Torque_Control_Y.TQ_OUT_bCruiseJudeg) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP2;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 1.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p;
      }
      break;

     case Torque_Control_IN_STEP2:
      /* Outport: '<Root>/STEP_CruiseControl' */
      Torque_Control_Y.STEP_CruiseControl = 1.0;
      if (Torque_Control_U.TQ_IN_bCruiseSUB) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP3;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 2.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p - 1.0F;
      } else if (Torque_Control_U.TQ_IN_bCruiseADD) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP4;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 3.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p + 1.0F;
      } else if (!Torque_Control_Y.TQ_OUT_bCruiseJudeg) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 0.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = false;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd = 0.0F;
      }
      break;

     case Torque_Control_IN_STEP3:
      /* Outport: '<Root>/STEP_CruiseControl' */
      Torque_Control_Y.STEP_CruiseControl = 2.0;
      if (!Torque_Control_Y.TQ_OUT_bCruiseJudeg) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 0.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = false;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd = 0.0F;
      } else if (Torque_Control_U.TQ_IN_bCruiseSUB) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP3;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p - 1.0F;
      } else if (Torque_Control_U.TQ_IN_bCruiseADD) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP4;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 3.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p + 1.0F;
      }
      break;

     default:
      /* Outport: '<Root>/STEP_CruiseControl' */
      /* case IN_STEP4: */
      Torque_Control_Y.STEP_CruiseControl = 3.0;
      if (!Torque_Control_Y.TQ_OUT_bCruiseJudeg) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 0.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = false;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd = 0.0F;
      } else if (Torque_Control_U.TQ_IN_bCruiseADD) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP4;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p + 1.0F;
      } else if (Torque_Control_U.TQ_IN_bCruiseSUB) {
        Torque_Control_DW.is_c8_Torque_Control = Torque_Control_IN_STEP3;

        /* Outport: '<Root>/STEP_CruiseControl' */
        Torque_Control_Y.STEP_CruiseControl = 2.0;

        /* Outport: '<Root>/TQ_OUT_bCruiseControl' */
        Torque_Control_Y.TQ_OUT_bCruiseControl = true;

        /* Outport: '<Root>/TQ_OUT_sCruiseSetSpd' */
        Torque_Control_Y.TQ_OUT_sCruiseSetSpd =
          Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p - 1.0F;
      }
      break;
    }
  }

  /* End of Chart: '<S19>/Chart2' */

  /* RelationalOperator: '<S32>/Compare' incorporates:
   *  Outport: '<Root>/TQ_OUT_bCruiseControl'
   */
  rtb_Compare_p = !Torque_Control_Y.TQ_OUT_bCruiseControl;

  /* DiscreteIntegrator: '<S69>/Integrator' */
  if (rtb_Compare_p && (Torque_Control_DW.Integrator_PrevResetState_n <= 0)) {
    Torque_Control_DW.Integrator_DSTATE_h = 0.0F;
  }

  /* Switch: '<S19>/Switch2' incorporates:
   *  Constant: '<S19>/Constant2'
   *  Constant: '<S19>/Constant3'
   *  Outport: '<Root>/TQ_OUT_bCruiseControl'
   *  Outport: '<Root>/TQ_OUT_sCruiseSetSpd'
   *  Switch: '<S19>/Switch3'
   */
  if (Torque_Control_Y.TQ_OUT_bCruiseControl) {
    tmp = Torque_Control_Y.TQ_OUT_sCruiseSetSpd;
    rtb_Abs5 = Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p;
  } else {
    tmp = 0.0F;
    rtb_Abs5 = 0.0F;
  }

  /* Sum: '<S19>/Sum' incorporates:
   *  Switch: '<S19>/Switch2'
   *  Switch: '<S19>/Switch3'
   */
  Torque_Control_Y.TQ_OUT_sCruiseErr = tmp - rtb_Abs5;

  /* Switch: '<S19>/Switch4' incorporates:
   *  Constant: '<S19>/Constant4'
   *  Inport: '<Root>/CAL_sDCruisePID_I'
   *  Outport: '<Root>/TQ_OUT_bCruiseControl'
   */
  if (Torque_Control_Y.TQ_OUT_bCruiseControl) {
    tmp = Torque_Control_U.CAL_sDCruisePID_I;
  } else {
    tmp = 0.0F;
  }

  /* Switch: '<S19>/Switch1' incorporates:
   *  DiscreteIntegrator: '<S69>/Integrator'
   *  Product: '<S74>/PProd Out'
   *  Sum: '<S78>/Sum'
   *  Switch: '<S19>/Switch4'
   */
  Torque_Control_Y.TQ_OUT_sCruiseOutputTorq = Torque_Control_Y.TQ_OUT_sCruiseErr
    * tmp + Torque_Control_DW.Integrator_DSTATE_h;

  /* Saturate: '<S76>/Saturation' */
  if (Torque_Control_Y.TQ_OUT_sCruiseOutputTorq > 3000.0F) {
    /* Switch: '<S19>/Switch1' */
    Torque_Control_Y.TQ_OUT_sCruiseOutputTorq = 3000.0F;
  } else if (Torque_Control_Y.TQ_OUT_sCruiseOutputTorq < -1000.0F) {
    /* Switch: '<S19>/Switch1' */
    Torque_Control_Y.TQ_OUT_sCruiseOutputTorq = -1000.0F;
  }

  /* End of Saturate: '<S76>/Saturation' */

  /* Relay: '<S18>/Relay' */
  Torque_Control_DW.Relay_Mode_p =
    ((Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p >= 6.0F) ||
     ((!(Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p <= 2.0F)) &&
      Torque_Control_DW.Relay_Mode_p));

  /* Logic: '<S18>/Logical Operator' incorporates:
   *  Constant: '<S24>/Constant'
   *  Constant: '<S25>/Constant'
   *  Logic: '<S20>/Logical Operator5'
   *  RelationalOperator: '<S24>/Compare'
   *  RelationalOperator: '<S25>/Compare'
   */
  rtb_LogicalOperator4_g_tmp = (rtb_LogicalOperator4_g_tmp &&
    (Torque_Control_B.TQ_IN_sAccelPert <= 0.05F) && rtb_LogicalOperator_n_tmp &&
    (Torque_Control_B.TQ_IN_sBrakePert <= 0.05F) &&
    Torque_Control_B.TQ_IN_bCmdForw);

  /* Logic: '<S18>/Logical Operator3' incorporates:
   *  Logic: '<S20>/Logical Operator2'
   */
  rtb_LogicalOperator_n_tmp = !Torque_Control_B.TQ_IN_bAirPressLow;

  /* Logic: '<S18>/Logical Operator4' incorporates:
   *  Logic: '<S20>/Logical Operator1'
   */
  rtb_LogicalOperator_i_tmp = !Torque_Control_B.TQ_IN_bHandBrake;

  /* Logic: '<S18>/Logical Operator' incorporates:
   *  Constant: '<S26>/Constant'
   *  Inport: '<Root>/CAL_bDCrawlFlg'
   *  Logic: '<S18>/Logical Operator3'
   *  Logic: '<S18>/Logical Operator4'
   *  RelationalOperator: '<S26>/Compare'
   *  Relay: '<S18>/Relay'
   */
  Torque_Control_Y.TQ_TEMP_bDCrawlFlg = (rtb_LogicalOperator4_g_tmp &&
    Torque_Control_B.TQ_IN_bMCUEnFB && Torque_Control_B.TQ_IN_bReady &&
    rtb_LogicalOperator_n_tmp && rtb_LogicalOperator_i_tmp &&
    (Torque_Control_B.TQ_IN_u8VeilFltLvl <= 2) &&
    (!Torque_Control_DW.Relay_Mode_p) && Torque_Control_U.CAL_bDCrawlFlg);

  /* Chart: '<S18>/Chart' incorporates:
   *  Outport: '<Root>/TQ_OUT_bDCrawlFlt'
   */
  if (Torque_Control_DW.is_active_c1_Torque_Control == 0) {
    Torque_Control_DW.is_active_c1_Torque_Control = 1U;
    Torque_Control_DW.is_c1_Torque_Control = Torque_Control_IN_R_Judge_Creep;

    /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
    Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;
    Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;
  } else {
    guard1 = false;
    switch (Torque_Control_DW.is_c1_Torque_Control) {
     case Torque_Control_IN_R_Judge_Creep:
      if (Torque_Control_Y.TQ_OUT_bDCrawlFlt &&
          ((Torque_Control_B.TQ_IN_sBrakePert > 0.1) ||
           Torque_Control_B.TQ_IN_bHandBrake)) {
        Torque_Control_DW.is_c1_Torque_Control = Torque_Contro_IN_R_Judge_Creep3;

        /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;
        Torque_Control_Y.TQ_OUT_bDCrawlFlt = false;
      } else if (Torque_Control_Y.TQ_TEMP_bDCrawlFlg &&
                 (!Torque_Control_Y.TQ_OUT_bDCrawlFlt)) {
        Torque_Control_DW.is_c1_Torque_Control = Torque_Contro_IN_R_Judge_Creep1;

        /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlg = true;
        Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;
      }
      break;

     case Torque_Contro_IN_R_Judge_Creep1:
      if (!Torque_Control_Y.TQ_TEMP_bDCrawlFlg) {
        Torque_Control_DW.is_c1_Torque_Control = Torque_Control_IN_R_Judge_Creep;

        /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;
        Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;
      } else if ((Torque_Control_B.TQ_IN_sMotSpd < -20.0F) &&
                 (Torque_Control_B.TQ_IN_sMotTorq > (real_T)
                  Torque_Control_B.CAL_i16MaxCrawlTorq * 0.95)) {
        Torque_Control_DW.is_c1_Torque_Control = Torque_Contro_IN_R_Judge_Creep2;
      }
      break;

     case Torque_Contro_IN_R_Judge_Creep2:
      if ((Torque_Control_B.TQ_IN_sMotSpd >= 0.0F) ||
          (Torque_Control_B.TQ_IN_sMotTorq <= (real_T)
           Torque_Control_B.CAL_i16MaxCrawlTorq * 0.95)) {
        Torque_Control_DW.is_c1_Torque_Control = Torque_Contro_IN_R_Judge_Creep1;

        /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlg = true;
        Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;

        /* Outport: '<Root>/TQ_OUT_bDCrawlFlt' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlt = false;
      } else if (Torque_Control_DW.TQ_TEMP_CrawlCnt_o >= 1000.0) {
        /* Outport: '<Root>/TQ_OUT_bDCrawlFlt' */
        Torque_Control_Y.TQ_OUT_bDCrawlFlt = true;
        guard1 = true;
      } else if (!Torque_Control_Y.TQ_TEMP_bDCrawlFlg) {
        guard1 = true;
      } else {
        Torque_Control_DW.TQ_TEMP_CrawlCnt_o++;
      }
      break;

     default:
      /* case IN_R_Judge_Creep3: */
      Torque_Control_DW.is_c1_Torque_Control = Torque_Control_IN_R_Judge_Creep;

      /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
      Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;
      Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;
      break;
    }

    if (guard1) {
      Torque_Control_DW.is_c1_Torque_Control = Torque_Control_IN_R_Judge_Creep;

      /* Outport: '<Root>/TQ_OUT_bDCrawlFlg' */
      Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;
      Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;
    }
  }

  /* End of Chart: '<S18>/Chart' */

  /* Lookup_n-D: '<S4>/DVeilSpd_CrawlTorque' incorporates:
   *  RateTransition generated from: '<Root>/GEAR_D_TorqueControl'
   */
  Torque_Control_Y.TQ_TEMP_sDCrawlTorq = Torque_Control_look1_i_rQYGWmZ3
    (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControlI_p, GearD2_VeilSpd,
     DVeilSpd_CrawlTorque, 7U);

  /* Abs: '<S4>/Abs5' */
  if (Torque_Control_B.CAL_i16MaxCrawlTorq < 0) {
    tmp_0 = (uint16_T)-Torque_Control_B.CAL_i16MaxCrawlTorq;
  } else {
    tmp_0 = (uint16_T)Torque_Control_B.CAL_i16MaxCrawlTorq;
  }

  /* MinMax: '<S4>/MinMax' incorporates:
   *  Abs: '<S4>/Abs2'
   *  Abs: '<S4>/Abs5'
   */
  Torque_Control_Y.Check_D_CrawlTorque = fminf(fabsf
    (Torque_Control_Y.TQ_TEMP_sDCrawlTorq), (real32_T)tmp_0);

  /* Logic: '<S20>/Logical Operator4' incorporates:
   *  Constant: '<S90>/Constant'
   *  Constant: '<S91>/Constant'
   *  Inport: '<Root>/CAL_bDSlopeFlg'
   *  Logic: '<S20>/Logical Operator5'
   *  Logic: '<S20>/Logical Operator9'
   *  Outport: '<Root>/TQ_OUT_bDCrawlFlt'
   *  RelationalOperator: '<S90>/Compare'
   *  RelationalOperator: '<S91>/Compare'
   */
  Torque_Control_Y.TQ_TEMP_bDSlopeFlg = (Torque_Control_Y.TQ_OUT_bDCrawlFlt ||
    (rtb_LogicalOperator4_g_tmp && (!Torque_Control_B.TQ_IN_bCmdNtw) &&
     Torque_Control_B.TQ_IN_bMCUEnFB && Torque_Control_B.TQ_IN_bReady &&
     rtb_LogicalOperator_n_tmp && rtb_LogicalOperator_i_tmp &&
     Torque_Control_U.CAL_bDSlopeFlg && (Torque_Control_B.TQ_IN_u8VeilFltLvl <=
    2) && (Torque_Control_B.TQ_IN_sMotSpd < -20.0F)));

  /* Chart: '<S20>/Chart1' */
  if (Torque_Control_DW.is_active_c5_Torque_Control == 0) {
    Torque_Control_DW.is_active_c5_Torque_Control = 1U;
    Torque_Control_DW.is_c5_Torque_Control = Torque_Control_IN_STEP1;

    /* Outport: '<Root>/TQ_OUT_bDSlopeFlg' */
    Torque_Control_Y.TQ_OUT_bDSlopeFlg = false;

    /* Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg' */
    Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg = false;

    /* Outport: '<Root>/TQ_OUT_sDSmoothTorq' */
    Torque_Control_Y.TQ_OUT_sDSmoothTorq = 0.0F;
    Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = 0U;

    /* Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' */
    /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
    Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 1U;
  } else {
    switch (Torque_Control_DW.is_c5_Torque_Control) {
     case Torque_Control_IN_STEP1:
      if (Torque_Control_Y.TQ_TEMP_bDSlopeFlg) {
        Torque_Control_DW.is_c5_Torque_Control = Torque_Control_IN_STEP2;
      }
      break;

     case Torque_Control_IN_STEP2:
      if ((Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b >
           Torque_Control_U.CAL_u16DSlopeSetTime) ||
          (Torque_Control_B.TQ_IN_sBrakePert > 0.05) ||
          Torque_Control_B.TQ_IN_bHandBrake || Torque_Control_B.TQ_IN_bCmdNtw) {
        Torque_Control_DW.is_c5_Torque_Control = Torque_Control_IN_STEP3;

        /* Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg = true;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = 0U;

        /* Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 3U;
      } else if (((Torque_Control_B.TQ_IN_sAccelPert >= 0.1) && (fabs
                   (Torque_Control_B.TmpRTBAtGEAR_D_TorqueControl_gw -
                    Torque_Control_B.TQ_IN_sMotTorq) < 20.0)) ||
                 ((!Torque_Control_B.TQ_IN_bCmdForw) ||
                  (!Torque_Control_B.TQ_IN_bMCUEnFB) ||
                  (!Torque_Control_B.TQ_IN_bReady) ||
                  Torque_Control_B.TQ_IN_bAirPressLow ||
                  (Torque_Control_B.TQ_IN_u8VeilFltLvl >= 3))) {
        Torque_Control_DW.is_c5_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/TQ_OUT_bDSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeFlg = false;

        /* Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg = false;

        /* Outport: '<Root>/TQ_OUT_sDSmoothTorq' */
        Torque_Control_Y.TQ_OUT_sDSmoothTorq = 0.0F;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = 0U;

        /* Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 1U;
      } else {
        /* Outport: '<Root>/TQ_OUT_bDSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeFlg = true;

        /* Outport: '<Root>/TQ_OUT_sDSmoothTorq' */
        Torque_Control_Y.TQ_OUT_sDSmoothTorq = Torque_Control_B.TQ_IN_sMotTorq;
        tmp_0 = Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b + 1;
        if (Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b + 1 > 65535) {
          tmp_0 = 65535;
        }

        Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = (uint16_T)tmp_0;

        /* Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 2U;
      }
      break;

     default:
      /* case IN_STEP3: */
      if (Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b >= 1000) {
        Torque_Control_DW.is_c5_Torque_Control = Torque_Control_IN_STEP1;

        /* Outport: '<Root>/TQ_OUT_bDSlopeFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeFlg = false;

        /* Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg' */
        Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg = false;

        /* Outport: '<Root>/TQ_OUT_sDSmoothTorq' */
        Torque_Control_Y.TQ_OUT_sDSmoothTorq = 0.0F;
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = 0U;

        /* Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' */
        /* &#x72B6;&#x6001;&#x6807;&#x5FD7;&#x4F4D; */
        Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 1U;
      } else {
        Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b++;
      }
      break;
    }
  }

  /* End of Chart: '<S20>/Chart1' */

  /* Switch: '<S4>/Switch9' incorporates:
   *  Outport: '<Root>/TQ_OUT_bCruiseControl'
   *  Outport: '<Root>/TQ_OUT_bDCrawlFlg'
   *  Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg'
   *  Switch: '<S4>/Switch1'
   *  Switch: '<S4>/Switch12'
   *  Switch: '<S4>/Switch4'
   *  Switch: '<S4>/Switch5'
   *  Switch: '<S4>/Switch6'
   */
  if (Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Outport: '<Root>/TQ_OUT_sDSmoothTorq'
     */
    Torque_Control_Y.TQ_DOUT1 = Torque_Control_Y.TQ_OUT_sDSmoothTorq;
  } else if (Torque_Control_Y.BD_JudgeFlg) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Switch: '<S4>/Switch1'
     */
    Torque_Control_Y.TQ_DOUT1 = Torque_Control_Y.Check_D_BrakeTorque;
  } else if (Torque_Control_Y.DS_JudgeFlg) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  MinMax: '<S4>/Max'
     *  Switch: '<S4>/Switch1'
     *  Switch: '<S4>/Switch4'
     */
    Torque_Control_Y.TQ_DOUT1 = fmin(Torque_Control_Y.TrqUBound,
      Torque_Control_Y.Check_D_DriveTorque);
  } else if (Torque_Control_Y.SC_JudgeFlg) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Switch: '<S4>/Switch1'
     *  Switch: '<S4>/Switch12'
     *  Switch: '<S4>/Switch4'
     */
    Torque_Control_Y.TQ_DOUT1 = Torque_Control_Y.Check_D_SlideTorque;
  } else if (Torque_Control_Y.TQ_OUT_bCruiseControl) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Switch: '<S4>/Switch1'
     *  Switch: '<S4>/Switch12'
     *  Switch: '<S4>/Switch4'
     *  Switch: '<S4>/Switch5'
     */
    Torque_Control_Y.TQ_DOUT1 = Torque_Control_Y.TQ_OUT_sCruiseOutputTorq;
  } else if (Torque_Control_Y.TQ_OUT_bDCrawlFlg) {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Switch: '<S4>/Switch1'
     *  Switch: '<S4>/Switch12'
     *  Switch: '<S4>/Switch4'
     *  Switch: '<S4>/Switch5'
     *  Switch: '<S4>/Switch6'
     */
    Torque_Control_Y.TQ_DOUT1 = Torque_Control_Y.Check_D_CrawlTorque;
  } else {
    /* Switch: '<S4>/Switch9' incorporates:
     *  Switch: '<S4>/Switch1'
     *  Switch: '<S4>/Switch4'
     */
    Torque_Control_Y.TQ_DOUT1 = 0.0;
  }

  /* End of Switch: '<S4>/Switch9' */

  /* Switch: '<S19>/Switch1' incorporates:
   *  Constant: '<S19>/Constant1'
   *  Inport: '<Root>/CAL_sDCruisePID_P'
   *  Outport: '<Root>/TQ_OUT_bCruiseControl'
   */
  if (Torque_Control_Y.TQ_OUT_bCruiseControl) {
    tmp = Torque_Control_U.CAL_sDCruisePID_P;
  } else {
    tmp = 0.0F;
  }

  /* Update for DiscreteIntegrator: '<S69>/Integrator' incorporates:
   *  Product: '<S66>/IProd Out'
   *  Switch: '<S19>/Switch1'
   */
  Torque_Control_DW.Integrator_DSTATE_h += 0.05F *
    (Torque_Control_Y.TQ_OUT_sCruiseErr * tmp);
  Torque_Control_DW.Integrator_PrevResetState_n = (int8_T)rtb_Compare_p;

  /* End of Outputs for SubSystem: '<Root>/GEAR_D_TorqueControl' */

  /* RateTransition generated from: '<Root>/Switch1' */
  Torque_Control_B.TmpRTBAtSwitch1Inport1 = Torque_Control_Y.TQ_DOUT1;
}

/* Model initialize function */
void Torque_Control_initialize(void)
{
  /* Registration code */

  /* Set task counter limit used by the static main program */
  (Torque_Control_M)->Timing.TaskCounters.cLimit[0] = 1;
  (Torque_Control_M)->Timing.TaskCounters.cLimit[1] = 1;

  /* initialize error status */
  rtmSetErrorStatus(Torque_Control_M, (NULL));

  /* block I/O */
  (void) memset(((void *) &Torque_Control_B), 0,
                sizeof(B_Torque_Control_T));

  /* states (dwork) */
  (void) memset((void *)&Torque_Control_DW, 0,
                sizeof(DW_Torque_Control_T));

  /* external inputs */
  (void)memset(&Torque_Control_U, 0, sizeof(ExtU_Torque_Control_T));

  /* external outputs */
  (void)memset(&Torque_Control_Y, 0, sizeof(ExtY_Torque_Control_T));

  /* Start for Probe: '<S114>/Probe' */
  Torque_Control_B.Probe[0] = 0.05F;
  Torque_Control_B.Probe[1] = 0.0F;

  /* InitializeConditions for DiscreteIntegrator: '<S120>/Integrator' */
  Torque_Control_DW.Integrator_PrevResetState = 0;
  Torque_Control_DW.Integrator_IC_LOADING = 1U;

  /* SystemInitialize for Atomic SubSystem: '<Root>/GEAR_D_TorqueControl' */
  /* InitializeConditions for DiscreteIntegrator: '<S69>/Integrator' */
  Torque_Control_DW.Integrator_PrevResetState_n = 2;

  /* SystemInitialize for road speed limiter (replaces Chart '<S4>/Chart') */
  RSL_Init(&Torque_Control_RSL);
  Torque_Control_B.TrqUBound = 0.0;
  Torque_Control_DW.TqSoftMax = 0.0;

  /* InitializeConditions for Outport: '<Root>/RslState' incorporates:
   *  Chart: '<S4>/Chart'
   */
  Torque_Control_Y.RslState = 0.0;

  /* InitializeConditions for Outport: '<Root>/Rsl_ICont' incorporates:
   *  Chart: '<S4>/Chart'
   */
  Torque_Control_Y.Rsl_ICont = 0.0;

  /* InitializeConditions for Outport: '<Root>/Rsl_PCont' incorporates:
   *  Chart: '<S4>/Chart'
   */
  Torque_Control_Y.Rsl_PCont = 0.0;

  /* InitializeConditions for Outport: '<Root>/Rsl_Pid_TrqDlta' incorporates:
   *  Chart: '<S4>/Chart'
   */
  Torque_Control_Y.Rsl_Pid_TrqDlta = 0.0;

  /* InitializeConditions for Outport: '<Root>/TrqSoftDelta' incorporates:
   *  Chart: '<S4>/Chart'
   */
  Torque_Control_Y.TrqSoftDelta = 0.0;

  /* SystemInitialize for Chart: '<S4>/Chart' */
  Torque_Control_DW.is_active_c12_Torque_Control = 0U;
  Torque_Control_DW.is_c12_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bDCrawlFlg' incorporates:
   *  Chart: '<S18>/Chart'
   */
  Torque_Control_Y.TQ_OUT_bDCrawlFlg = false;

  /* SystemInitialize for Chart: '<S18>/Chart' */
  Torque_Control_DW.TQ_TEMP_CrawlCnt_o = 0.0;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bDCrawlFlt' incorporates:
   *  Chart: '<S18>/Chart'
   */
  Torque_Control_Y.TQ_OUT_bDCrawlFlt = false;

  /* SystemInitialize for Chart: '<S18>/Chart' */
  Torque_Control_DW.is_active_c1_Torque_Control = 0U;
  Torque_Control_DW.is_c1_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bCruiseOff' incorporates:
   *  Chart: '<S19>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bCruiseOff = false;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bCruiseJudeg' incorporates:
   *  Chart: '<S19>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bCruiseJudeg = false;

  /* SystemInitialize for Chart: '<S19>/Chart1' */
  Torque_Control_DW.TQ_IN_u16CruiseCnt = 0U;
  Torque_Control_DW.is_active_c7_Torque_Control = 0U;
  Torque_Control_DW.is_c7_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bCruiseControl' incorporates:
   *  Chart: '<S19>/Chart2'
   */
  Torque_Control_Y.TQ_OUT_bCruiseControl = false;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_sCruiseSetSpd' incorporates:
   *  Chart: '<S19>/Chart2'
   */
  Torque_Control_Y.TQ_OUT_sCruiseSetSpd = 0.0F;

  /* SystemInitialize for Chart: '<S19>/Chart2' */
  Torque_Control_DW.is_active_c8_Torque_Control = 0U;
  Torque_Control_DW.is_c8_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bDSlopeFlg' incorporates:
   *  Chart: '<S20>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bDSlopeFlg = false;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_bDSlopeTorqFlg' incorporates:
   *  Chart: '<S20>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bDSlopeTorqFlg = false;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_sDSmoothTorq' incorporates:
   *  Chart: '<S20>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_sDSmoothTorq = 0.0F;

  /* SystemInitialize for Chart: '<S20>/Chart1' */
  Torque_Control_DW.TQ_TEMP_u16SlopeCnt_b = 0U;

  /* InitializeConditions for Outport: '<Root>/TQ_OUT_u8DSlopeStepFlg' incorporates:
   *  Chart: '<S20>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_u8DSlopeStepFlg = 0U;

  /* SystemInitialize for Chart: '<S20>/Chart1' */
  Torque_Control_DW.is_active_c5_Torque_Control = 0U;
  Torque_Control_DW.is_c5_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* SystemInitialize for MATLAB Function: '<S4>/RegenFactor' */
  Torque_Control_DW.RegenState_not_empty = false;

  /* End of SystemInitialize for SubSystem: '<Root>/GEAR_D_TorqueControl' */

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_bRCrawlFlg' incorporates:
   *  Chart: '<S94>/Chart'
   */
  Torque_Control_Y.TQ_OUT_bRCrawlFlg = false;

  /* SystemInitialize for Chart: '<S94>/Chart' */
  Torque_Control_DW.TQ_TEMP_CrawlCnt = 0.0;

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_bRCrawlFlt' incorporates:
   *  Chart: '<S94>/Chart'
   */
  Torque_Control_Y.TQ_OUT_bRCrawlFlt = false;

  /* SystemInitialize for Chart: '<S94>/Chart' */
  Torque_Control_DW.is_active_c3_Torque_Control = 0U;
  Torque_Control_DW.is_c3_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_bRSlopeFlg' incorporates:
   *  Chart: '<S95>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bRSlopeFlg = false;

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_bRSlopeTorqFlg' incorporates:
   *  Chart: '<S95>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_bRSlopeTorqFlg = false;

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_sRSmoothTorq' incorporates:
   *  Chart: '<S95>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_sRSmoothTorq = 0.0F;

  /* SystemInitialize for Chart: '<S95>/Chart1' */
  Torque_Control_DW.TQ_TEMP_u16SlopeCnt = 0U;

  /* SystemInitialize for Outport: '<Root>/TQ_OUT_u8RSlopeStepFlg' incorporates:
   *  Chart: '<S95>/Chart1'
   */
  Torque_Control_Y.TQ_OUT_u8RSlopeStepFlg = 0U;

  /* SystemInitialize for Chart: '<S95>/Chart1' */
  Torque_Control_DW.is_active_c4_Torque_Control = 0U;
  Torque_Control_DW.is_c4_Torque_Control = Torque_Contr_IN_NO_ACTIVE_CHILD;

  /* SystemInitialize for Enabled SubSystem: '<Root>/Subsystem' */
  /* InitializeConditions for Delay: '<S109>/Delay' */
  Torque_Control_DW.icLoad_f = true;

  /* End of SystemInitialize for SubSystem: '<Root>/Subsystem' */

  /* SystemInitialize for Enabled SubSystem: '<Root>/Subsystem1' */
  /* InitializeConditions for Delay: '<S111>/Delay' */
  Torque_Control_DW.icLoad = true;

  /* End of SystemInitialize for SubSystem: '<Root>/Subsystem1' */
}

/* Model terminate function */
void Torque_Control_terminate(void)
{
  /* (no terminate code required) */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
