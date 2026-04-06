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

#define FaultTotalNumber    255


Word FaultTestFlag = 0, FaultTestLevel = 0;

struct FaultCodeStr FaultRecordCode[FaultTotalNumber];
Word wFaultCnt[FaultTotalNumber];
Word FaultSetTime = 100;

Word Max_VehicleFaultLevel = 0, Max_VCUFaultLevel = 0;

Word VCUFaultTotalNumber = 0, VCUErrCodeShow = 0, VCUErrCodeShowSerial = 0, FaultCodeSendCnt = 0;

Word VCUSendErrCode = 0;

Word AIRP_CanCheck = 0, BMS_CanCheck = 0, CANFaultJudgeCnt = 0, LDC_CanCheck = 0, MCU_CanCheck = 0, STP_CanCheck = 0,
     ABS_CanCheck = 0, METER_CanCheck = 0;

Word RxAIRP_LifeCnt_Old = 0, RxBMS_LifeCnt_Old = 0, RxLDC_LifeCnt_Old = 0, RxMCU_LifeCnt_Old = 0, RxSTP_LifeCnt_Old = 0;

uint8_t CANFaultCheckFlag = 0, Fault_AIRP_CAN = 0, Fault_BMS_CAN = 0, Fault_LDC_CAN = 0, Fault_MCU_CAN = 0, Fault_STP_CAN = 0,
        Fault_METER_CAN = 0, Fault_ABS_CAN = 0;

uint8_t bMotorSpeedOverFault = 0, bMotorSpeedOverFault_Flg = 0, bMotorSpeedOverFault_Cnt = 0;

/* Global send record buffer (avoids large stack allocation each call) */
static Word FaultCodeSendRecord[FaultTotalNumber];


/************************************************************************
** FaultRecordFunction()
** Records or clears a fault entry.
** Grade-3 faults latch and will not self-clear (require power cycle/reset).
************************************************************************/
void FaultRecordFunction(Word FaultNumber, Word FaultFlag, Word FaultGarde, Word FaultPart)
{
    Word FaultFlag_CntAfter = 0;

    if (1 == FaultFlag) {
        wFaultCnt[FaultNumber]++;
        if (wFaultCnt[FaultNumber] >= FaultSetTime) {
            wFaultCnt[FaultNumber] = FaultSetTime;
            FaultFlag_CntAfter = 1;
        }
    } else {
        wFaultCnt[FaultNumber] = 0;
        FaultFlag_CntAfter = 0;
    }

    if (FaultFlag_CntAfter == 1) {
        FaultRecordCode[FaultNumber].Number = FaultNumber;
        FaultRecordCode[FaultNumber].Grade  = FaultGarde;
        FaultRecordCode[FaultNumber].Part   = FaultPart;
    } else {
        if (FaultRecordCode[FaultNumber].Grade < 3) {
            /* Grade 1/2 faults self-clear when condition is gone */
            FaultRecordCode[FaultNumber].Number = 0;
            FaultRecordCode[FaultNumber].Grade  = 0;
            FaultRecordCode[FaultNumber].Part   = 0;
        } else {
            /* Grade 3 faults latch until reset */
            FaultRecordCode[FaultNumber].Number = FaultNumber;
            FaultRecordCode[FaultNumber].Grade  = FaultGarde;
            FaultRecordCode[FaultNumber].Part   = FaultPart;
        }
    }
}


/************************************************************************
** FaultRecord()
** Fault diagnosis — evaluates all fault conditions each cycle.
************************************************************************/
void FaultRecord(void)
{
    /* --- Grade 1 faults (warning) ------------------------------------ */

    /* MCU controller bus overvoltage warning */
    FaultRecordFunction(1, (C_MCUA4_ControllerOvervoltageAlarm || C_MCUB4_ControllerOvervoltageAlarm), One_Garde, Prat_MCU);

    /* Motor blocking warning
     * FIX: was C_MCUA4_MotorBlockingAlarm || C_MCUA4_MotorBlockingAlarm (copy-paste bug — B side never checked) */
    FaultRecordFunction(2, (C_MCUA4_MotorBlockingAlarm || C_MCUB4_MotorBlockingAlarm), One_Garde, Prat_MCU);

    /* MCU controller overtemperature warning */
    FaultRecordFunction(3, (C_MCUA4_ControllerIGBTOvertempAlarm || C_MCUA4_ControlBoardOvertempAlarm ||
                            C_MCUB4_ControllerIGBTOvertempAlarm || C_MCUB4_ControlBoardOvertempAlarm), One_Garde, Prat_MCU);

    /* MCU controller bus undervoltage warning */
    FaultRecordFunction(4, (C_MCUA4_ControllerUndervoltageAlarm || C_MCUB4_ControllerUndervoltageAlarm), One_Garde, Prat_MCU);

    /* Drive motor overtemperature warning */
    FaultRecordFunction(5, (C_MCUA4_MotorOvertempAlarm || C_MCUB4_MotorOvertempAlarm), One_Garde, Prat_MCU);

    /* Drive motor overspeed warning */
    FaultRecordFunction(6, (C_MCUA4_MotorOverspeedAlarm || C_MCUB4_MotorOverspeedAlarm), One_Garde, Prat_MCU);

    /* Defrost contactor fault */
    FaultRecordFunction(7, 0, One_Garde, Prat_OTHER);

    /* AC contactor fault */
    FaultRecordFunction(8, 0, One_Garde, Prat_OTHER);

    /* AC communication fault */
    FaultRecordFunction(9, 0, One_Garde, Prat_VCU);

    /* AC system fault */
    FaultRecordFunction(10, ((C_AirCond_FaultCode > 0) ? 1 : 0), One_Garde, Prat_OTHER);

    /* Storage battery low voltage */
    FaultRecordFunction(11, ((C_DCDC_OutVoltage < 19) ? 1 : 0), One_Garde, Prat_VCU);

    /* Oil pump temperature sensor fault */
    FaultRecordFunction(12, C_STP_TempSensorFault, One_Garde, Prat_OIL);

    /* Air pump temperature sensor fault */
    FaultRecordFunction(13, C_AIRP_TempSensorFault, One_Garde, Prat_AIR);

    /* Handbrake / drive interlock fault */
    FaultRecordFunction(14, ((TQM_MIP_HandBrake == 1) && (TQM_MOP_Temp_VehicleSpeed > 5)), One_Garde, Prat_VCU);

    /* Battery cooling system fault */
    FaultRecordFunction(16, 0, One_Garde, Prat_OTHER);

    /* DCDC input undervoltage */
    FaultRecordFunction(17, C_DCDC_InputVolUnder, One_Garde, Prat_DCDC);

    /* DCDC input overvoltage */
    FaultRecordFunction(18, C_DCDC_InputVolOver, One_Garde, Prat_DCDC);

    /* DCDC output overcurrent */
    FaultRecordFunction(19, C_DCDC_OutCurrOver, One_Garde, Prat_DCDC);

    /* DCDC module overtemperature */
    FaultRecordFunction(20, C_DCDC_OverTemp, One_Garde, Prat_DCDC);

    /* DCDC output open circuit */
    FaultRecordFunction(21, C_DCDC_OutOpenFault, One_Garde, Prat_DCDC);

    /* DCDC CAN communication fault */
    FaultRecordFunction(22, (Fault_LDC_CAN || C_DCDC_CANFault), One_Garde, Prat_DCDC);

    /* DCDC hardware fault */
    FaultRecordFunction(25, (((VCU_RX_DCDC_BOX[0][6] >> 2) == 0) &&
                             ((C_DCDC_FaultGrade > 0) || (C_DCDC_State == 3))), One_Garde, Prat_DCDC);

    /* Accelerator / brake interlock */
    FaultRecordFunction(28, bBrakeAccelLockFlag, One_Garde, Prat_VCU);

    /* Charging gun connected without handbrake */
    FaultRecordFunction(33, (C_BMS2_ChargeGunConnect && (C_METER_HardBrake == 0)), One_Garde, Prat_VCU);

    /* Air pump continuous run >20 min fault */
    FaultRecordFunction(35, AUX_MOP_AirPumpContinueWorkFault, One_Garde, Prat_VCU);

    /* OBC communication fault */
    FaultRecordFunction(37, 0, One_Garde, Prat_OTHER);


    /* --- Grade 2 faults (reduced performance) ------------------------ */

    /* Oil pump CAN communication fault */
    FaultRecordFunction(70, (Fault_STP_CAN || C_STP_CANFault), Two_Garde, Prat_VCU);

    /* Air pump CAN communication fault */
    FaultRecordFunction(71, (Fault_AIRP_CAN || C_AIRP_CANFault), Two_Garde, Prat_VCU);

    /* Instrument panel CAN communication fault */
    FaultRecordFunction(72, Fault_METER_CAN, Two_Garde, Prat_VCU);

    /* Air pump phase loss fault */
    FaultRecordFunction(73, C_AIRP_PhaseFault, Two_Garde, Prat_AIR);

    /* Oil pump phase loss fault */
    FaultRecordFunction(74, C_STP_PhaseFault, Two_Garde, Prat_OIL);

    /* Oil pump temperature sensor fault */
    FaultRecordFunction(75, C_STP_TempSensorFault, Two_Garde, Prat_OIL);

    /* ABS CAN communication fault */
    FaultRecordFunction(77, Fault_ABS_CAN, Two_Garde, Prat_VCU);

    /* Oil pump overtemperature */
    FaultRecordFunction(80, C_STP_MotorOverTemp, Two_Garde, Prat_OIL);

    /* Air pump overtemperature */
    FaultRecordFunction(81, C_AIRP_MotorOverTemp, Two_Garde, Prat_AIR);

    /* Oil pump inverter fault */
    FaultRecordFunction(82, ((VCU_RX_STP_BOX[0][6] == 0) &&
                             ((C_STP_FaultGrade > 0) || (C_STP_DCACState == 3))), Two_Garde, Prat_OIL);

    /* Air pump inverter fault */
    FaultRecordFunction(83, ((VCU_RX_AIRP_BOX[0][6] == 0) &&
                             ((C_AIRP_FaultGrade > 0) || (C_AIRP_DCACState == 3))), Two_Garde, Prat_AIR);

    /* Air pump inverter overvoltage */
    FaultRecordFunction(84, C_AIRP_InputVolOver, Two_Garde, Prat_AIR);

    /* Air pump inverter undervoltage */
    FaultRecordFunction(85, C_AIRP_InputVolUnder, Two_Garde, Prat_AIR);

    /* Air pump inverter overcurrent */
    FaultRecordFunction(86, C_AIRP_OutCurrOver, Two_Garde, Prat_AIR);

    /* Air pump controller overtemperature */
    FaultRecordFunction(87, C_AIRP_ControlOverTemp, Two_Garde, Prat_AIR);

    /* Air pump temperature sensor fault */
    FaultRecordFunction(88, C_AIRP_TempSensorFault, Two_Garde, Prat_AIR);

    /* Oil pump inverter overvoltage */
    FaultRecordFunction(89, C_STP_InputVolOver, Two_Garde, Prat_OIL);

    /* Oil pump inverter undervoltage */
    FaultRecordFunction(90, C_STP_InputVolUnder, Two_Garde, Prat_OIL);

    /* Oil pump inverter overcurrent */
    FaultRecordFunction(91, C_STP_OutCurrOver, Two_Garde, Prat_OIL);

    /* Oil pump controller overtemperature */
    FaultRecordFunction(92, C_STP_ControlOverTemp, Two_Garde, Prat_OIL);

    /* Auxiliary shutdown timeout fault (steering pump, air pump, DCDC, AC) */
    FaultRecordFunction(93, POD_MOP_ClearAUXWorkFail, Two_Garde, Prat_VCU);

    /* Accelerator pedal single-channel signal fault */
    FaultRecordFunction(98, 0, Two_Garde, Prat_VCU);

    /* Auxiliary contactor close failure */
    FaultRecordFunction(101, POD_MOP_PreContactorCloseFail, Two_Garde, Prat_VCU);


    /* --- Grade 3 faults (shutdown / latching) ------------------------ */

    /* MCU self-check failure */
    FaultRecordFunction(151, POD_MOP_MCUSelfCheckFail, Three_Garde, Prat_VCU);

    /* MCU controller bus overvoltage protection */
    FaultRecordFunction(152, (C_MCUA4_ControllerOvervoltageProtection || C_MCUB4_ControllerOvervoltageProtection), Three_Garde, Prat_MCU);

    /* MCU phase overcurrent protection */
    FaultRecordFunction(153, (C_MCUA4_MotorOvercurrentProtection   || C_MCUA4_MotorOvercurrentProtection_A ||
                              C_MCUA4_MotorOvercurrentProtection_B  || C_MCUA4_MotorOvercurrentProtection_C ||
                              C_MCUB4_MotorOvercurrentProtection    || C_MCUB4_MotorOvercurrentProtection_A ||
                              C_MCUB4_MotorOvercurrentProtection_B  || C_MCUB4_MotorOvercurrentProtection_C), Three_Garde, Prat_MCU);

    /* MCU controller overtemperature protection */
    FaultRecordFunction(154, (C_MCUA4_ControllerIGBT_OvertempProtection || C_MCUA4_ControlBoard_OvertempProtection ||
                              C_MCUB4_ControllerIGBT_OvertempProtection || C_MCUB4_ControlBoard_OvertempProtection), Three_Garde, Prat_MCU);

    /* MCU controller bus undervoltage protection */
    FaultRecordFunction(155, (C_MCUA4_ControllerUndervoltageProtection || C_MCUB4_ControllerUndervoltageProtection), Three_Garde, Prat_MCU);

    /* Drive motor overtemperature protection */
    FaultRecordFunction(156, (C_MCUA4_MotorOvertempProtection   || C_MCUA4_MotorOvertempProtection_A ||
                              C_MCUA4_MotorOvertempProtection_B  || C_MCUB4_MotorOvertempProtection  ||
                              C_MCUB4_MotorOvertempProtection_A  || C_MCUB4_MotorOvertempProtection_B), Three_Garde, Prat_MCU);

    /* Resolver fault */
    FaultRecordFunction(157, (C_MCUA4_RotatoryFail || C_MCUA4_HardwareRotationFail ||
                              C_MCUB4_RotatoryFail || C_MCUB4_HardwareRotationFail), Three_Garde, Prat_MCU);

    /* Motor temperature sensor fault */
    FaultRecordFunction(158, (C_MCUA4_MotorTempSensorFail   || C_MCUA4_MotorTempSensorA_fail ||
                              C_MCUA4_MotorTempSensorB_fail  || C_MCUB4_MotorTempSensorFail   ||
                              C_MCUB4_MotorTempSensorA_fail  || C_MCUB4_MotorTempSensorB_fail), Three_Garde, Prat_MCU);

    /* MCU shutdown / active discharge failure */
    FaultRecordFunction(160, (C_MCUA4_ActiveDischargeFail || C_MCUB4_ActiveDischargeFail), Three_Garde, Prat_VCU);

    /* Drive motor overspeed protection
     * Software-side overspeed latch: flag stays set until speed drops below threshold */
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
            bMotorSpeedOverFault_Cnt = 0;
        }
    }
    FaultRecordFunction(161, (C_MCUA4_MotorOverspeedProtection || C_MCUB4_MotorOverspeedProtection || bMotorSpeedOverFault), Three_Garde, Prat_MCU);

    /* Insulation fault */
    FaultRecordFunction(162, 0, Three_Garde, Prat_VCU);

    /* Load shedding failure */
    FaultRecordFunction(163, 0, Three_Garde, Prat_VCU);

    /* Total negative contactor open timeout */
    FaultRecordFunction(164, 0, Three_Garde, Prat_VCU);

    /* Motor stall */
    FaultRecordFunction(165, 0, Three_Garde, Prat_MCU);

    /* MCU IGBT hardware fault */
    FaultRecordFunction(166, 0, Three_Garde, Prat_MCU);

    /* MCU CAN communication fault */
    FaultRecordFunction(167, (Fault_MCU_CAN || C_MCUA4_CANCommunicationFail || C_MCUB4_CANCommunicationFail), Three_Garde, Prat_VCU);

    /* MCU output phase loss */
    FaultRecordFunction(168, 0, Three_Garde, Prat_MCU);

    /* MCU phase short circuit */
    FaultRecordFunction(169, 0, Three_Garde, Prat_MCU);

    /* MCU bus overcurrent */
    FaultRecordFunction(170, 0, Three_Garde, Prat_MCU);

    /* MCU current surge fault */
    FaultRecordFunction(171, 0, Three_Garde, Prat_MCU);

    /* MCU current filter fault */
    FaultRecordFunction(172, 0, Three_Garde, Prat_MCU);

    /* MCU midpoint voltage fault */
    FaultRecordFunction(173, 0, Three_Garde, Prat_MCU);

    /* MCU voltage surge fault */
    FaultRecordFunction(174, 0, Three_Garde, Prat_MCU);

    /* Motor contactor weld fault */
    FaultRecordFunction(175, 0, Three_Garde, Prat_VCU);

    /* VCU hardware fault */
    FaultRecordFunction(176, 0, Three_Garde, Prat_VCU);

    /* VCU 24V supply fault */
    FaultRecordFunction(177, 0, Three_Garde, Prat_VCU);

    /* BMS main negative contactor close timeout */
    FaultRecordFunction(178, POD_MOP_MainNegContactorCloseFail, Three_Garde, Prat_VCU);

    /* Pre-charge contactor weld fault */
    FaultRecordFunction(179, 0, Three_Garde, Prat_VCU);

    /* Gear panel fault (multiple gear signals simultaneously) */
    FaultRecordFunction(180, GEAR_MOP_GearFault, Three_Garde, Prat_VCU);

    /* Pre-charge contactor close failure */
    FaultRecordFunction(181, POD_MOP_PreContactorCloseFail, Three_Garde, Prat_VCU);

    /* Gearbox fault */
    FaultRecordFunction(183, 0, Three_Garde, Prat_VCU);

    /* Main contactor open timeout (main pos open timeout / power-off fail / active discharge fail) */
    FaultRecordFunction(185, POD_MOP_OpenMainPosContactorFail, Three_Garde, Prat_VCU);

    /* BMS CAN communication fault */
    FaultRecordFunction(186, Fault_BMS_CAN, Three_Garde, Prat_VCU);

    /* Controller current sensor fault */
    FaultRecordFunction(187, 0, Three_Garde, Prat_MCU);

    /* Controller temperature sensor fault */
    FaultRecordFunction(188, 0, Three_Garde, Prat_MCU);

    /* Pre-charge fault */
    FaultRecordFunction(191, POD_MOP_ContactorSelfCheckFail, Three_Garde, Prat_VCU);

    /* Motor contactor fault (not present) */
    FaultRecordFunction(192, 0, Three_Garde, Prat_VCU);

    /* Main positive contactor close failure */
    FaultRecordFunction(193, POD_MOP_MainPosContactorCloseFail, Three_Garde, Prat_VCU);

    /* Main negative contactor fault */
    FaultRecordFunction(194, 0, Three_Garde, Prat_VCU);

    /* Hardware drive total fault */
    FaultRecordFunction(195, 0, Three_Garde, Prat_MCU);

    /* MCU current detection fault */
    FaultRecordFunction(196, 0, Three_Garde, Prat_MCU);

    /* Hardware overcurrent fault */
    FaultRecordFunction(197, 0, Three_Garde, Prat_MCU);

    /* Accelerator pedal dual-channel signal fault */
    FaultRecordFunction(198, 0, Three_Garde, Prat_VCU);

    /* Active discharge failure fault */
    FaultRecordFunction(199, 0, Three_Garde, Prat_VCU);

    /* Insulation resistance low fault */
    FaultRecordFunction(200, 0, Three_Garde, Prat_VCU);

    /* MCU voltage too high during power-on */
    FaultRecordFunction(204, 0, One_Garde, Prat_VCU);

    /* Test fault entry */
    FaultRecordFunction(206, FaultTestFlag, FaultTestLevel, Prat_VCU);
}


/************************************************************************
** VCUFaultLevelJudge()
** Determines the highest active VCU fault grade and the overall vehicle
** fault grade (max of VCU, BMS, MCU reported levels).
**
** FIX: Max_VCUFaultLevel is now reset to 0 at the start of each call so
**      the level can decrease when faults clear.
************************************************************************/
void VCUFaultLevelJudge(void)
{
    Word i = 0;

    /* Reset each cycle so the level tracks current active faults */
    Max_VCUFaultLevel = 0;

    for (i = 0; i < FaultTotalNumber; i++) {
        if (FaultRecordCode[i].Grade != 0) {
            Max_VCUFaultLevel = Judge_MAX(Max_VCUFaultLevel, FaultRecordCode[i].Grade);
        }
    }

    /* Compare VCU level against BMS and MCU reported levels */
    Max_VehicleFaultLevel = Max_VCUFaultLevel;

    if (POD_MIP_BMSFaultLevel > Max_VehicleFaultLevel) {
        Max_VehicleFaultLevel = POD_MIP_BMSFaultLevel;
    }
    if (POD_MIP_MCUFaultLevel > Max_VehicleFaultLevel) {
        Max_VehicleFaultLevel = POD_MIP_MCUFaultLevel;
    }
}


/************************************************************************
** FaultCodeSend()
** Cycles through active fault codes and sends one code every 100 cycles.
**
** FIX: FaultCodeSendRecord moved to static global (avoids 510-byte stack
**      allocation on every call).
** FIX: boundary check changed from > to >= to prevent out-of-bounds read.
************************************************************************/
void FaultCodeSend(void)
{
    Word i = 0, j = 0;

    for (i = 0; i < FaultTotalNumber; i++) {
        if (FaultRecordCode[i].Number != 0) {
            FaultCodeSendRecord[j] = FaultRecordCode[i].Number;
            j++;
        }
    }
    VCUFaultTotalNumber = j;

    FaultCodeSendCnt++;
    if (FaultCodeSendCnt >= 100) {
        FaultCodeSendCnt = 0;
        VCUErrCodeShow = FaultCodeSendRecord[VCUErrCodeShowSerial];
        VCUErrCodeShowSerial++;
    }

    /* FIX: was '>' — allowed VCUErrCodeShowSerial == VCUFaultTotalNumber,
     *      causing an out-of-bounds read on the next cycle. */
    if (VCUErrCodeShowSerial >= VCUFaultTotalNumber) {
        VCUErrCodeShowSerial = 0;
    }
}


/************************************************************************
** CANFaultJudge()
** Detects loss-of-communication for each CAN node by monitoring life
** counters. Fault is set after the node-specific timeout elapses.
**
** FIX (all nodes): the counter was reset to 0 inside the threshold-check
**   else-branch, preventing it from ever reaching the threshold. The
**   counter now only resets when the node resumes communication (life
**   count changes), and RxXxx_LifeCnt_Old is updated there instead.
************************************************************************/
void CANFaultJudge(void)
{
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

        /* BMS CAN — timeout 1 s (50 × 20 ms) */
        if (C_BMS1_LifeCnt == RxBMS_LifeCnt_Old) {
            BMS_CanCheck++;
        } else {
            BMS_CanCheck        = 0;
            RxBMS_LifeCnt_Old   = C_BMS1_LifeCnt;
        }
        if (BMS_CanCheck >= 50) {
            BMS_CanCheck  = 50;
            Fault_BMS_CAN = 1;
        } else {
            Fault_BMS_CAN = 0;
        }

        /* MCU CAN — timeout 200 ms (10 × 20 ms) */
        if (C_MCUA1_LifeCnt == RxMCU_LifeCnt_Old) {
            MCU_CanCheck++;
        } else {
            MCU_CanCheck        = 0;
            RxMCU_LifeCnt_Old   = C_MCUA1_LifeCnt;
        }
        if (MCU_CanCheck >= 10) {
            MCU_CanCheck  = 10;
            Fault_MCU_CAN = 1;
        } else {
            Fault_MCU_CAN = 0;
        }

        /* Oil pump (STP) CAN — timeout 1.2 s (60 × 20 ms) */
        if (C_STP_LifeCnt == RxSTP_LifeCnt_Old) {
            STP_CanCheck++;
        } else {
            STP_CanCheck        = 0;
            RxSTP_LifeCnt_Old   = C_STP_LifeCnt;
        }
        if (STP_CanCheck >= 60) {
            STP_CanCheck  = 60;
            Fault_STP_CAN = 1;
        } else {
            Fault_STP_CAN = 0;
        }

        /* Air pump (AIRP) CAN — timeout 1.2 s (60 × 20 ms) */
        if (C_AIRP_LifeCnt == RxAIRP_LifeCnt_Old) {
            AIRP_CanCheck++;
        } else {
            AIRP_CanCheck       = 0;
            RxAIRP_LifeCnt_Old  = C_AIRP_LifeCnt;
        }
        if (AIRP_CanCheck >= 60) {
            AIRP_CanCheck  = 60;
            Fault_AIRP_CAN = 1;
        } else {
            Fault_AIRP_CAN = 0;
        }

        /* DCDC (LDC) CAN — timeout 1.2 s (60 × 20 ms) */
        if (C_DCDC_LifeCnt == RxLDC_LifeCnt_Old) {
            LDC_CanCheck++;
        } else {
            LDC_CanCheck        = 0;
            RxLDC_LifeCnt_Old   = C_DCDC_LifeCnt;
        }
        if (LDC_CanCheck >= 60) {
            LDC_CanCheck  = 60;
            Fault_LDC_CAN = 1;
        } else {
            Fault_LDC_CAN = 0;
        }

        /* ABS CAN — timeout 1 s (50 × 20 ms) */
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

        /* Instrument panel (METER) CAN — timeout 1 s (50 × 20 ms) */
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


void Fault_C(void)
{
    CANFaultJudge();
    FaultRecord();
    VCUFaultLevelJudge();
    FaultCodeSend();
}
