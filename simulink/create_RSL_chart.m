function create_RSL_chart(subsysPath)
% create_RSL_chart  Add the new road speed limiter chart to the model.
%
%   create_RSL_chart('Torque_Control/GEAR_D_TorqueControl')
%
% Adds a Stateflow chart 'RSL_Chart' next to the old '<S4>/Chart'.
% The old chart is NOT touched: rewire its signals to RSL_Chart, then
% delete the old chart yourself (see wiring table printed at the end).

if nargin < 1
    error('Give the subsystem path, e.g. ''Torque_Control/GEAR_D_TorqueControl''.');
end

model = strtok(subsysPath, '/');
load_system(model);
evalin('base', 'RSL_params');            % calibration parameters

blk = [subsysPath '/RSL_Chart'];
if getSimulinkBlockHandle(blk) ~= -1
    error('%s already exists. Delete it first to re-create.', blk);
end

load_system('sflib');
add_block('sflib/Chart', blk, 'Position', [100 600 320 820]);

rt = sfroot;
ch = rt.find('-isa', 'Stateflow.Chart', 'Path', blk);
ch.ActionLanguage = 'MATLAB';
ch.Description = ['Road speed limiter, GEAR D. Constant speed hold at full ' ...
                  'throttle. Replaces old Idle/SoftLanding/PIDGoverning chart.'];

% ---- inputs (port order 1..6), type inherited from the wired signal ----
inNames = {'v', 'L', 'DrvTrq', 'BrakeAllow', 'SlideAllow', 'maxRslRegenTrq'};
for k = 1:numel(inNames)
    addData(ch, inNames{k}, 'Input', 'Inherit: Same as Simulink');
end

% ---- outputs (port order 1..6), double like the old chart ----
outNames = {'TrqUBound', 'RslState', 'Rsl_PCont', 'Rsl_ICont', ...
            'Rsl_Pid_TrqDlta', 'TrqSoftDelta'};
for k = 1:numel(outNames)
    addData(ch, outNames{k}, 'Output', 'double');
end

% ---- local data (single precision for Cortex-M4 FPU) ----
locNames = {'vRef', 'Iacc', 'Tprev', 'vs', 'Ls', 'D', 'MinT', 'Pc', ...
            'Vdif', 'stp', 'u', 'T'};
for k = 1:numel(locNames)
    addData(ch, locNames{k}, 'Local', 'single');
end

% ---- tunable parameters (resolve to the Simulink.Parameter objects) ----
parNames = {'RSL_Kp', 'RSL_Ki', 'RSL_EngBand', 'RSL_RefRate', ...
            'RSL_TrqRate', 'RSL_LimitMin'};
for k = 1:numel(parNames)
    addData(ch, parNames{k}, 'Parameter', 'single');
end

% ---- the single state and its default transition ----
here = fileparts(mfilename('fullpath'));
label = fileread(fullfile(here, 'RSL_chart_state.txt'));
label = strrep(label, sprintf('\r\n'), newline);

s = Stateflow.State(ch);
s.Position = [60 60 700 1000];
s.LabelString = strtrim(label);

t = Stateflow.Transition(ch);
t.Destination = s;
t.DestinationOClock = 0;
x = s.Position(1) + s.Position(3) / 2;
y = s.Position(2) - 30;
t.SourceEndpoint = [x y];
t.MidPoint = [x y + 15];

fprintf('\nCreated %s\n\n', blk);
fprintf('Wire it like this, then delete the old <S4>/Chart:\n');
fprintf('  IN  1 v              <- vehicle speed (aTQ_TEMP_sVeilSpd_, same as old chart)\n');
fprintf('  IN  2 L              <- CAL_sDVeilSpdLimit\n');
fprintf('  IN  3 DrvTrq         <- <S4>/Switch8 output (Check_D_DriveTorque)\n');
fprintf('  IN  4 BrakeAllow     <- signal into <S4>/Min1 input 1 (VeilAllowBrakeTorq)\n');
fprintf('  IN  5 SlideAllow     <- signal into <S4>/Min1 input 2 (VeilAllowSlideTorq)\n');
fprintf('  IN  6 maxRslRegenTrq <- inport maxRslRegenTrq\n');
fprintf('  OUT 1 TrqUBound      -> <S4>/Max1 (where old chart TrqUBound went)\n');
fprintf('  OUT 2..6             -> outports RslState, Rsl_PCont, Rsl_ICont,\n');
fprintf('                          Rsl_Pid_TrqDlta, TrqSoftDelta\n');
fprintf('  Old inports Rsl_Kp, Rsl_ki, Rsl_ICont_Max, Rsl_DltaSoftDiff,\n');
fprintf('  Rsl_ReleaseDelta, Rsl_Trq_diff_SMax, Rsl_Trq_diff_PIMax -> Terminator\n\n');
end

function d = addData(ch, name, scope, type)
d = Stateflow.Data(ch);
d.Name = name;
d.Scope = scope;
d.DataType = type;
end
