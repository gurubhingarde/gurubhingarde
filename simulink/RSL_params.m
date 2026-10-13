% RSL_params.m - tunable calibration for the road speed limiter chart.
% Creates Simulink.Parameter objects in the base workspace (ExportedGlobal,
% single), so the generated code has e.g.  real32_T RSL_Kp = 400.0F;
% Put the values you tuned on the vehicle here.

rslCal = { ...
    'RSL_Kp',       400;   ... % Nm per km/h
    'RSL_Ki',        80;   ... % Nm per km/h per s
    'RSL_EngBand',    5;   ... % km/h, limiter armed from L - EngBand
    'RSL_RefRate',  0.5;   ... % km/h per s, approach rate to the limit
    'RSL_TrqRate',   25;   ... % Nm per 0.05 s step, slew limit
    'RSL_LimitMin',   5 };     % km/h, limit <= this = limiter off

for k = 1:size(rslCal, 1)
    p = Simulink.Parameter(single(rslCal{k, 2}));
    p.DataType = 'single';
    p.CoderInfo.StorageClass = 'ExportedGlobal';
    assignin('base', rslCal{k, 1}, p);
end
clear rslCal k p
