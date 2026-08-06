/*
 * Fault.c
 *
 *  Created on: 2023-08-24
 *      Author: DELL
 */

#include "Fault.h"

#define Three_Garde    3
#define Two_Garde      2
#define One_Garde      1

#define Prat_VCU       1
#define Prat_MCU       2
#define Prat_BMS       3
#define Prat_AIR       4
#define Prat_OIL       5
#define Prat_DCDC      6
#define Prat_OTHER     7

#define FaultTotalNumber    255               // Total number of fault codes


Word FaultTestFlag = 0, FaultTestLevel = 0;

struct FaultCodeStr FaultRecordCode[FaultTotalNumber];
Word wFaultCnt[FaultTotalNumber];
Word FaultSetTime = 100;                      // Fault confirmation time (cycles)

Word Max_VehicleFaultLevel = 0, Max_VCUFaultLevel = 0;

Word VCUFaultTotalNumber = 0, VCUErrCodeShow = 0, VCUErrCodeShowSerial = 0, FaultCodeSendCnt = 0;

Word VCUSendErrCode = 0;

// CAN communication timeout counters for each node
Word AIRP_CanCheck = 0, BMS_CanCheck = 0, CANFaultJudgeCnt = 0, LDC_CanCheck = 0, MCU_CanCheck = 0, STP_CanCheck = 0,
     ABS_CanCheck = 0, METER_CanCheck = 0;

// Previous life counter values used to detect node silence
Word RxAIRP_LifeCnt_Old = 0, RxBMS_LifeCnt_Old = 0, RxLDC_LifeCnt_Old = 0, RxMCU_LifeCnt_Old = 0, RxSTP_LifeCnt_Old = 0;

// CAN fault flags: set to 1 when node is silent beyond timeout
uint8_t CANFaultCheckFlag = 0, Fault_AIRP_CAN = 0, Fault_BMS_CAN = 0, Fault_LDC_CAN = 0, Fault_MCU_CAN = 0, Fault_STP_CAN = 0,
        Fault_METER_CAN = 0, Fault_ABS_CAN = 0;

// Motor overspeed software detection flags
uint8_t bMotorSpeedOverFault = 0, bMotorSpeedOverFault_Flg = 0, bMotorSpeedOverFault_Cnt = 0;

// Static buffer avoids 510-byte stack allocation on every FaultCodeSend() call
static Word FaultCodeSendRecord[FaultTotalNumber];


/************************************************************************
** Function  : FaultRecordFunction()
** Purpose   : Record or clear a single fault entry
** Params    : FaultNumber  - fault index (0~254)
**             FaultFlag    - 1 = condition active, 0 = condition gone
**             FaultGarde   - severity grade (1/2/3)
**             FaultPart    - faulty component (Prat_xxx)
** Note      : Grade-3 faults latch and will NOT self-clear.
**             Grade-1/2 faults clear when condition is gone.
**
** -------- FaultCode --- Trigger Condition --- Grade --- Part --------
************************************************************************/
void FaultRecordFunction(Word FaultNumber, Word FaultFlag, Word FaultGarde, Word FaultPart)
{
    Word FaultFlag_CntAfter = 0;

    if (1 == FaultFlag) {
        // Count consecutive active cycles; confirm fault after FaultSetTime cycles
        wFaultCnt[FaultNumber]++;
        if (wFaultCnt[FaultNumber] >= FaultSetTime) {
            wFaultCnt[FaultNumber] = FaultSetTime;
            FaultFlag_CntAfter = 1;
        }
    } else {
        // Condition gone - reset counter
        wFaultCnt[FaultNumber] = 0;
        FaultFlag_CntAfter = 0;
    }

    if (FaultFlag_CntAfter == 1) {
        // Fault confirmed - record it
        FaultRecordCode[FaultNumber].Number = FaultNumber;
        FaultRecordCode[FaultNumber].Grade  = FaultGarde;
        FaultRecordCode[FaultNumber].Part   = FaultPart;
    } else {
        if (FaultRecordCode[FaultNumber].Grade < 3) {
            // Grade 1/2: self-clear when condition is gone
            FaultRecordCode[FaultNumber].Number = 0;
            FaultRecordCode[FaultNumber].Grade  = 0;
            FaultRecordCode[FaultNumber].Part   = 0;
        } else {
            // Grade 3: latch - keep fault set until power cycle / external reset
            FaultRecordCode[FaultNumber].Number = FaultNumber;
            FaultRecordCode[FaultNumber].Grade  = FaultGarde;
            FaultRecordCode[FaultNumber].Part   = FaultPart;
        }
    }
}


/************************************************************************
** Function : FaultRecord()
** Purpose  : Fault diagnosis - evaluates all fault conditions each cycle
** Caller   : Fault_C()
** Note     : Called at fixed task rate (20 ms recommended)
************************************************************************/
void FaultRecord(void)
{
    // ==================== Grade 1 Faults (Warning) ====================

    // MCU controller bus overvoltage warning
    FaultRecordFunction(1, (C_MCUA4_ControllerOvervoltageAlarm || C_MCUB4_ControllerOvervoltageAlarm), One_Garde, Prat_MCU);

    // Motor blocking warning
    // FIX: was (C_MCUA4_MotorBlockingAlarm || C_MCUA4_MotorBlockingAlarm) - copy-paste bug, MCU-B was never checked
    FaultRecordFunction(2, (C_MCUA4_MotorBlockingAlarm || C_MCUB4_MotorBlockingAlarm), One_Garde, Prat_MCU);

    // MCU controller / IGBT / control board overtemperature warning
    FaultRecordFunction(3, (C_MCUA4_ControllerIGBTOvertempAlarm || C_MCUA4_ControlBoardOvertempAlarm ||
                            C_MCUB4_ControllerIGBTOvertempAlarm || C_MCUB4_ControlBoardOvertempAlarm), One_Garde, Prat_MCU);

    // MCU controller bus undervoltage warning
    FaultRecordFunction(4, (C_MCUA4_ControllerUndervoltageAlarm || C_MCUB4_ControllerUndervoltageAlarm), One_Garde, Prat_MCU);

    // Drive motor overtemperature warning
    FaultRecordFunction(5, (C_MCUA4_MotorOvertempAlarm || C_MCUB4_MotorOvertempAlarm), One_Garde, Prat_MCU);

    // Drive motor overspeed warning
    FaultRecordFunction(6, (C_MCUA4_MotorOverspeedAlarm || C_MCUB4_MotorOverspeedAlarm), One_Garde, Prat_MCU);

    // Defrost contactor fault (not yet implemented)
    FaultRecordFunction(7, 0, One_Garde, Prat_OTHER);

    // AC contactor fault (not yet implemented)
    FaultRecordFunction(8, 0, One_Garde, Prat_OTHER);

    // AC communication fault (not yet implemented)
    FaultRecordFunction(9, 0, One_Garde, Prat_VCU);

    // AC system fault - any non-zero AC fault code
    FaultRecordFunction(10, ((C_AirCond_FaultCode > 0) ? 1 : 0), One_Garde, Prat_OTHER);

    // Storage battery low voltage - DCDC output < 19 V
    FaultRecordFunction(11, ((C_DCDC_OutVoltage < 19) ? 1 : 0), One_Garde, Prat_VCU);

    // Oil pump temperature sensor fault
    FaultRecordFunction(12, C_STP_TempSensorFault, One_Garde, Prat_OIL);

    // Air pump temperature sensor fault
    FaultRecordFunction(13, C_AIRP_TempSensorFault, One_Garde, Prat_AIR);

    // Handbrake / drive interlock fault - handbrake ON while vehicle speed > 5 km/h
    FaultRecordFunction(14, ((TQM_MIP_HandBrake == 1) && (TQM_MOP_Temp_VehicleSpeed > 5)), One_Garde, Prat_VCU);

    // Battery cooling system fault (not yet implemented)
    FaultRecordFunction(16, 0, One_Garde, Prat_OTHER);

    // DCDC input undervoltage
    FaultRecordFunction(17, C_DCDC_InputVolUnder, One_Garde, Prat_DCDC);

    // DCDC input overvoltage
    FaultRecordFunction(18, C_DCDC_InputVolOver, One_Garde, Prat_DCDC);

    // DCDC output overcurrent
    FaultRecordFunction(19, C_DCDC_OutCurrOver, One_Garde, Prat_DCDC);

    // DCDC module overtemperature
    FaultRecordFunction(20, C_DCDC_OverTemp, One_Garde, Prat_DCDC);

    // DCDC output open-circuit fault
    FaultRecordFunction(21, C_DCDC_OutOpenFault, One_Garde, Prat_DCDC);

    // DCDC CAN communication fault (from life-counter check OR DCDC self-report)
    FaultRecordFunction(22, (Fault_LDC_CAN || C_DCDC_CANFault), One_Garde, Prat_DCDC);

    // DCDC hardware fault - CAN byte[6] bit[3:2]==0 AND (fault grade>0 OR state==error)
    FaultRecordFunction(25, (((VCU_RX_DCDC_BOX[0][6] >> 2) == 0) &&
                             ((C_DCDC_FaultGrade > 0) || (C_DCDC_State == 3))), One_Garde, Prat_DCDC);

    // Accelerator / brake interlock fault
    FaultRecordFunction(28, bBrakeAccelLockFlag, One_Garde, Prat_VCU);

    // Charging gun connected but handbrake not applied
    FaultRecordFunction(33, (C_BMS2_ChargeGunConnect && (C_METER_HardBrake == 0)), One_Garde, Prat_VCU);

    // Air pump continuous run > 20 minutes fault
    FaultRecordFunction(35, AUX_MOP_AirPumpContinueWorkFault, One_Garde, Prat_VCU);

    // OBC communication fault (not yet implemented)
    FaultRecordFunction(37, 0, One_Garde, Prat_OTHER);


    // ==================== Grade 2 Faults (Reduced Performance) ====================

    // Oil pump (STP) CAN communication fault
    FaultRecordFunction(70, (Fault_STP_CAN || C_STP_CANFault), Two_Garde, Prat_VCU);

    // Air pump (AIRP) CAN communication fault
    FaultRecordFunction(71, (Fault_AIRP_CAN || C_AIRP_CANFault), Two_Garde, Prat_VCU);

    // Instrument panel (METER) CAN communication fault
    FaultRecordFunction(72, Fault_METER_CAN, Two_Garde, Prat_VCU);

    // Air pump phase loss fault
    FaultRecordFunction(73, C_AIRP_PhaseFault, Two_Garde, Prat_AIR);

    // Oil pump phase loss fault
    FaultRecordFunction(74, C_STP_PhaseFault, Two_Garde, Prat_OIL);

    // Oil pump temperature sensor fault (Grade 2 escalation of fault #12)
    FaultRecordFunction(75, C_STP_TempSensorFault, Two_Garde, Prat_OIL);

    // ABS CAN communication fault
    FaultRecordFunction(77, Fault_ABS_CAN, Two_Garde, Prat_VCU);

    // Oil pump motor overtemperature
    FaultRecordFunction(80, C_STP_MotorOverTemp, Two_Garde, Prat_OIL);

    // Air pump motor overtemperature
    FaultRecordFunction(81, C_AIRP_MotorOverTemp, Two_Garde, Prat_AIR);

    // Oil pump inverter (DCAC) fault - CAN byte[6]==0 AND (fault grade>0 OR state==error)
    FaultRecordFunction(82, ((VCU_RX_STP_BOX[0][6] == 0) &&
                             ((C_STP_FaultGrade > 0) || (C_STP_DCACState == 3))), Two_Garde, Prat_OIL);

    // Air pump inverter (DCAC) fault - CAN byte[6]==0 AND (fault grade>0 OR state==error)
    FaultRecordFunction(83, ((VCU_RX_AIRP_BOX[0][6] == 0) &&
                             ((C_AIRP_FaultGrade > 0) || (C_AIRP_DCACState == 3))), Two_Garde, Prat_AIR);

    // Air pump inverter overvoltage
    FaultRecordFunction(84, C_AIRP_InputVolOver, Two_Garde, Prat_AIR);

    // Air pump inverter undervoltage
    FaultRecordFunction(85, C_AIRP_InputVolUnder, Two_Garde, Prat_AIR);

    // Air pump inverter overcurrent
    FaultRecordFunction(86, C_AIRP_OutCurrOver, Two_Garde, Prat_AIR);

    // Air pump controller overtemperature
    FaultRecordFunction(87, C_AIRP_ControlOverTemp, Two_Garde, Prat_AIR);

    // Air pump temperature sensor fault (Grade 2 escalation of fault #13)
    FaultRecordFunction(88, C_AIRP_TempSensorFault, Two_Garde, Prat_AIR);

    // Oil pump inverter overvoltage
    FaultRecordFunction(89, C_STP_InputVolOver, Two_Garde, Prat_OIL);

    // Oil pump inverter undervoltage
    FaultRecordFunction(90, C_STP_InputVolUnder, Two_Garde, Prat_OIL);

    // Oil pump inverter overcurrent
    FaultRecordFunction(91, C_STP_OutCurrOver, Two_Garde, Prat_OIL);

    // Oil pump controller overtemperature
    FaultRecordFunction(92, C_STP_ControlOverTemp, Two_Garde, Prat_OIL);

    // Auxiliary device shutdown timeout (steering pump / air pump / DCDC / AC)
    FaultRecordFunction(93, POD_MOP_ClearAUXWorkFail, Two_Garde, Prat_VCU);

    // Accelerator pedal single-channel signal fault (not yet implemented)
    FaultRecordFunction(98, 0, Two_Garde, Prat_VCU);

    // Auxiliary contactor close failure
    FaultRecordFunction(101, POD_MOP_PreContactorCloseFail, Two_Garde, Prat_VCU);


    // ==================== Grade 3 Faults (Shutdown / Latching) ====================

    // MCU self-check failure
    FaultRecordFunction(151, POD_MOP_MCUSelfCheckFail, Three_Garde, Prat_VCU);

    // MCU controller bus overvoltage protection
    FaultRecordFunction(152, (C_MCUA4_ControllerOvervoltageProtection || C_MCUB4_ControllerOvervoltageProtection), Three_Garde, Prat_MCU);

    // MCU phase overcurrent protection (all phase sub-flags OR-ed)
    FaultRecordFunction(153, (C_MCUA4_MotorOvercurrentProtection   || C_MCUA4_MotorOvercurrentProtection_A ||
                              C_MCUA4_MotorOvercurrentProtection_B  || C_MCUA4_MotorOvercurrentProtection_C ||
                              C_MCUB4_MotorOvercurrentProtection    || C_MCUB4_MotorOvercurrentProtection_A ||
                              C_MCUB4_MotorOvercurrentProtection_B  || C_MCUB4_MotorOvercurrentProtection_C), Three_Garde, Prat_MCU);

    // MCU controller / IGBT / control board overtemperature protection
    FaultRecordFunction(154, (C_MCUA4_ControllerIGBT_OvertempProtection || C_MCUA4_ControlBoard_OvertempProtection ||
                              C_MCUB4_ControllerIGBT_OvertempProtection  || C_MCUB4_ControlBoard_OvertempProtection), Three_Garde, Prat_MCU);

    // MCU controller bus undervoltage protection
    FaultRecordFunction(155, (C_MCUA4_ControllerUndervoltageProtection || C_MCUB4_ControllerUndervoltageProtection), Three_Garde, Prat_MCU);

    // Drive motor overtemperature protection (all winding sub-flags OR-ed)
    FaultRecordFunction(156, (C_MCUA4_MotorOvertempProtection   || C_MCUA4_MotorOvertempProtection_A ||
                              C_MCUA4_MotorOvertempProtection_B  || C_MCUB4_MotorOvertempProtection  ||
                              C_MCUB4_MotorOvertempProtection_A  || C_MCUB4_MotorOvertempProtection_B), Three_Garde, Prat_MCU);

    // Resolver / rotary encoder fault
    FaultRecordFunction(157, (C_MCUA4_RotatoryFail || C_MCUA4_HardwareRotationFail ||
                              C_MCUB4_RotatoryFail  || C_MCUB4_HardwareRotationFail), Three_Garde, Prat_MCU);

    // Motor temperature sensor fault (all sensor sub-flags OR-ed)
    FaultRecordFunction(158, (C_MCUA4_MotorTempSensorFail   || C_MCUA4_MotorTempSensorA_fail ||
                              C_MCUA4_MotorTempSensorB_fail  || C_MCUB4_MotorTempSensorFail   ||
                              C_MCUB4_MotorTempSensorA_fail  || C_MCUB4_MotorTempSensorB_fail), Three_Garde, Prat_MCU);

    // MCU shutdown failure / active discharge fault
    FaultRecordFunction(160, (C_MCUA4_ActiveDischargeFail || C_MCUB4_ActiveDischargeFail), Three_Garde, Prat_VCU);

    // Drive motor overspeed - software confirmation over 10 cycles (~200 ms)
    // bMotorSpeedOverFault stays latched until speed drops below 5000 RPM
    if (C_MCUA1_MotorSpeed >= 5000 || C_MCUB1_MotorSpeed >= 5000) {
        bMotorSpeedOverFault_Flg = 1;
    } else {
        bMotorSpeedOverFault_Flg = 0;
        bMotorSpeedOverFault_Cnt = 0;
        bMotorSpeedOverFault     = 0;
    }
    if (bMotorSpeedOverFault_Flg == 1) {
        bMotorSpeedOverFault_Cnt++;
        if (bMotorSpeedOverFault_Cnt >= 10) {
            bMotorSpeedOverFault     = 1;
            bMotorSpeedOverFault_Cnt = 0;  // reset counter after confirmation
        }
    }
    FaultRecordFunction(161, (C_MCUA4_MotorOverspeedProtection || C_MCUB4_MotorOverspeedProtection || bMotorSpeedOverFault), Three_Garde, Prat_MCU);

    // Insulation fault (not yet implemented)
    FaultRecordFunction(162, 0, Three_Garde, Prat_VCU);

    // Load shedding failure (not yet implemented)
    FaultRecordFunction(163, 0, Three_Garde, Prat_VCU);

    // Total negative contactor open timeout (not yet implemented)
    FaultRecordFunction(164, 0, Three_Garde, Prat_VCU);

    // Motor stall fault (not yet implemented)
    FaultRecordFunction(165, 0, Three_Garde, Prat_MCU);

    // MCU IGBT hardware fault (not yet implemented)
    FaultRecordFunction(166, 0, Three_Garde, Prat_MCU);

    // MCU CAN communication fault (life-counter check OR MCU self-report)
    FaultRecordFunction(167, (Fault_MCU_CAN || C_MCUA4_CANCommunicationFail || C_MCUB4_CANCommunicationFail), Three_Garde, Prat_VCU);

    // MCU output phase loss (not yet implemented)
    FaultRecordFunction(168, 0, Three_Garde, Prat_MCU);

    // MCU phase short-circuit fault (not yet implemented)
    FaultRecordFunction(169, 0, Three_Garde, Prat_MCU);

    // MCU bus overcurrent (not yet implemented)
    FaultRecordFunction(170, 0, Three_Garde, Prat_MCU);

    // MCU current surge fault (not yet implemented)
    FaultRecordFunction(171, 0, Three_Garde, Prat_MCU);

    // MCU current filter fault (not yet implemented)
    FaultRecordFunction(172, 0, Three_Garde, Prat_MCU);

    // MCU midpoint voltage fault (not yet implemented)
    FaultRecordFunction(173, 0, Three_Garde, Prat_MCU);

    // MCU voltage surge fault (not yet implemented)
    FaultRecordFunction(174, 0, Three_Garde, Prat_MCU);

    // Motor contactor weld fault (not yet implemented)
    FaultRecordFunction(175, 0, Three_Garde, Prat_VCU);

    // VCU hardware fault (not yet implemented)
    FaultRecordFunction(176, 0, Three_Garde, Prat_VCU);

    // VCU 24V power supply fault (not yet implemented)
    FaultRecordFunction(177, 0, Three_Garde, Prat_VCU);

    // BMS main negative contactor close timeout
    FaultRecordFunction(178, POD_MOP_MainNegContactorCloseFail, Three_Garde, Prat_VCU);

    // Pre-charge contactor weld fault (not yet implemented)
    FaultRecordFunction(179, 0, Three_Garde, Prat_VCU);

    // Gear panel fault - two or more gear signals active simultaneously
    FaultRecordFunction(180, GEAR_MOP_GearFault, Three_Garde, Prat_VCU);

    // Pre-charge contactor close failure
    FaultRecordFunction(181, POD_MOP_PreContactorCloseFail, Three_Garde, Prat_VCU);

    // Gearbox fault (not yet implemented)
    FaultRecordFunction(183, 0, Three_Garde, Prat_VCU);

    // Main positive contactor open timeout / power-off failure / active discharge failure
    FaultRecordFunction(185, POD_MOP_OpenMainPosContactorFail, Three_Garde, Prat_VCU);

    // BMS CAN communication fault
    FaultRecordFunction(186, Fault_BMS_CAN, Three_Garde, Prat_VCU);

    // Controller current sensor fault (not yet implemented)
    FaultRecordFunction(187, 0, Three_Garde, Prat_MCU);

    // Controller temperature sensor fault (not yet implemented)
    FaultRecordFunction(188, 0, Three_Garde, Prat_MCU);

    // Pre-charge / contactor self-check fault
    FaultRecordFunction(191, POD_MOP_ContactorSelfCheckFail, Three_Garde, Prat_VCU);

    // Motor contactor fault (hardware not present on this platform)
    FaultRecordFunction(192, 0, Three_Garde, Prat_VCU);

    // Main positive contactor close failure
    FaultRecordFunction(193, POD_MOP_MainPosContactorCloseFail, Three_Garde, Prat_VCU);

    // Main negative contactor fault (not yet implemented)
    FaultRecordFunction(194, 0, Three_Garde, Prat_VCU);

    // Hardware drive total fault (not yet implemented)
    FaultRecordFunction(195, 0, Three_Garde, Prat_MCU);

    // MCU current detection fault (not yet implemented)
    FaultRecordFunction(196, 0, Three_Garde, Prat_MCU);

    // Hardware overcurrent fault (not yet implemented)
    FaultRecordFunction(197, 0, Three_Garde, Prat_MCU);

    // Accelerator pedal dual-channel signal fault (not yet implemented)
    FaultRecordFunction(198, 0, Three_Garde, Prat_VCU);

    // Active discharge failure fault (not yet implemented)
    FaultRecordFunction(199, 0, Three_Garde, Prat_VCU);

    // Insulation resistance too low (not yet implemented)
    FaultRecordFunction(200, 0, Three_Garde, Prat_VCU);

    // MCU bus voltage too high during power-on (not yet implemented)
    FaultRecordFunction(204, 0, One_Garde, Prat_VCU);

    // Test / diagnostic fault entry - controlled by FaultTestFlag and FaultTestLevel
    FaultRecordFunction(206, FaultTestFlag, FaultTestLevel, Prat_VCU);
}


/************************************************************************
** Function : VCUFaultLevelJudge()
** Purpose  : Determine highest active VCU fault grade and overall vehicle
**            fault grade (max of VCU, BMS, and MCU reported levels)
** Caller   : Fault_C()
** Note     : FIX - Max_VCUFaultLevel is reset to 0 at start of each call
**            so the level can decrease when faults clear. Previously it
**            could only rise, never come back down.
************************************************************************/
void VCUFaultLevelJudge(void)
{
    Word i = 0;

    // Reset each cycle so level reflects only currently active faults
    Max_VCUFaultLevel = 0;

    for (i = 0; i < FaultTotalNumber; i++) {
        if (FaultRecordCode[i].Grade != 0) {
            Max_VCUFaultLevel = Judge_MAX(Max_VCUFaultLevel, FaultRecordCode[i].Grade);
        }
    }

    // Vehicle fault level = max of VCU, BMS, and MCU reported levels
    Max_VehicleFaultLevel = Max_VCUFaultLevel;

    if (POD_MIP_BMSFaultLevel > Max_VehicleFaultLevel) {
        Max_VehicleFaultLevel = POD_MIP_BMSFaultLevel;
    }
    if (POD_MIP_MCUFaultLevel > Max_VehicleFaultLevel) {
        Max_VehicleFaultLevel = POD_MIP_MCUFaultLevel;
    }
}


/************************************************************************
** Function : FaultCodeSend()
** Purpose  : Cycle through active fault codes and send one every 100 cycles
** Caller   : Fault_C()
** Note     : FIX - boundary check changed from > to >= to prevent
**            out-of-bounds read when serial index equals total count.
**            FIX - send record buffer moved to static global to avoid
**            510-byte stack allocation on every call.
************************************************************************/
void FaultCodeSend(void)
{
    Word i = 0, j = 0;

    // Collect all currently active fault codes into send record
    for (i = 0; i < FaultTotalNumber; i++) {
        if (FaultRecordCode[i].Number != 0) {
            FaultCodeSendRecord[j] = FaultRecordCode[i].Number;
            j++;
        }
    }
    VCUFaultTotalNumber = j;   // total active faults this cycle

    // Send one fault code every 100 cycles (~2 s at 20 ms task rate)
    FaultCodeSendCnt++;
    if (FaultCodeSendCnt >= 100) {
        FaultCodeSendCnt = 0;
        VCUErrCodeShow = FaultCodeSendRecord[VCUErrCodeShowSerial];
        VCUErrCodeShowSerial++;
    }

    // FIX: was '>' - allowed serial == total, causing out-of-bounds read next cycle
    if (VCUErrCodeShowSerial >= VCUFaultTotalNumber) {
        VCUErrCodeShowSerial = 0;
    }
}


/************************************************************************
** Function : CANFaultJudge()
** Purpose  : Detect loss-of-communication for each CAN node by monitoring
**            life counters. Fault is set after node-specific timeout.
** Caller   : Fault_C()
** Note     : FIX (all 7 nodes) - counter was reset to 0 inside the
**            threshold else-branch, so it bounced 0->1->0 forever and
**            never reached the threshold. Counter now only resets when
**            the node resumes (life count changes). RxXxx_LifeCnt_Old
**            is updated in the life-count-changed branch only.
************************************************************************/
void CANFaultJudge(void)
{
    // Wait 50 cycles (~1 s) after key-ON before starting CAN checks
    // This avoids false faults during boot-up / node initialisation
    if (1 == G_Key_ON) {
        CANFaultJudgeCnt++;
        if (CANFaultJudgeCnt >= 50) {
            CANFaultJudgeCnt  = 50;
            CANFaultCheckFlag = 1;
        }
    } else {
        CANFaultJudgeCnt  = 0;
        CANFaultCheckFlag = 0;
    }

    if (CANFaultCheckFlag == 1) {

        // BMS CAN - timeout 1 s (50 cycles x 20 ms)
        if (C_BMS1_LifeCnt == RxBMS_LifeCnt_Old) {
            BMS_CanCheck++;                        // life count unchanged -> node silent
        } else {
            BMS_CanCheck      = 0;                 // life count changed  -> node alive, reset counter
            RxBMS_LifeCnt_Old = C_BMS1_LifeCnt;
        }
        if (BMS_CanCheck >= 50) {
            BMS_CanCheck  = 50;                    // cap counter
            Fault_BMS_CAN = 1;
        } else {
            Fault_BMS_CAN = 0;
        }

        // MCU CAN - timeout 200 ms (10 cycles x 20 ms)
        if (C_MCUA1_LifeCnt == RxMCU_LifeCnt_Old) {
            MCU_CanCheck++;
        } else {
            MCU_CanCheck      = 0;
            RxMCU_LifeCnt_Old = C_MCUA1_LifeCnt;
        }
        if (MCU_CanCheck >= 10) {
            MCU_CanCheck  = 10;
            Fault_MCU_CAN = 1;
        } else {
            Fault_MCU_CAN = 0;
        }

        // Oil pump (STP / DCAC) CAN - timeout 1.2 s (60 cycles x 20 ms)
        if (C_STP_LifeCnt == RxSTP_LifeCnt_Old) {
            STP_CanCheck++;
        } else {
            STP_CanCheck      = 0;
            RxSTP_LifeCnt_Old = C_STP_LifeCnt;
        }
        if (STP_CanCheck >= 60) {
            STP_CanCheck  = 60;
            Fault_STP_CAN = 1;
        } else {
            Fault_STP_CAN = 0;
        }

        // Air pump (AIRP / DCAC) CAN - timeout 1.2 s (60 cycles x 20 ms)
        if (C_AIRP_LifeCnt == RxAIRP_LifeCnt_Old) {
            AIRP_CanCheck++;
        } else {
            AIRP_CanCheck      = 0;
            RxAIRP_LifeCnt_Old = C_AIRP_LifeCnt;
        }
        if (AIRP_CanCheck >= 60) {
            AIRP_CanCheck  = 60;
            Fault_AIRP_CAN = 1;
        } else {
            Fault_AIRP_CAN = 0;
        }

        // DCDC (LDC) CAN - timeout 1.2 s (60 cycles x 20 ms)
        if (C_DCDC_LifeCnt == RxLDC_LifeCnt_Old) {
            LDC_CanCheck++;
        } else {
            LDC_CanCheck      = 0;
            RxLDC_LifeCnt_Old = C_DCDC_LifeCnt;
        }
        if (LDC_CanCheck >= 60) {
            LDC_CanCheck  = 60;
            Fault_LDC_CAN = 1;
        } else {
            Fault_LDC_CAN = 0;
        }

        // ABS CAN - timeout 1 s (50 cycles x 20 ms); uses RX flag, not life counter
        if (VCU_RX_ABS_FLAG[0] == 0) {
            ABS_CanCheck++;
        } else {
            ABS_CanCheck = 0;
        }
        if (ABS_CanCheck >= 50) {
            ABS_CanCheck  = 50;
            Fault_ABS_CAN = 1;
        } else {
            Fault_ABS_CAN = 0;
        }

        // Instrument panel (METER) CAN - timeout 1 s (50 cycles x 20 ms); uses RX flag
        if (VCU_RX_METER_FLAG[0] == 0) {
            METER_CanCheck++;
        } else {
            METER_CanCheck = 0;
        }
        if (METER_CanCheck >= 50) {
            METER_CanCheck  = 50;
            Fault_METER_CAN = 1;
        } else {
            Fault_METER_CAN = 0;
        }
    }
}


/************************************************************************
** Function : Fault_C()
** Purpose  : Main fault management entry point - call once per task cycle
************************************************************************/
void Fault_C(void)
{
    CANFaultJudge();        // Step 1: detect CAN node timeouts
    FaultRecord();          // Step 2: evaluate all fault conditions
    VCUFaultLevelJudge();   // Step 3: determine highest active fault level
    FaultCodeSend();        // Step 4: send active fault codes to display
}
