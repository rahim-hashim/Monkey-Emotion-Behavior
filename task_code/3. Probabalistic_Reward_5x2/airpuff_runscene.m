%% Trial Start
% clear dashboard
% dashboard(1, ' ')
% check for eye signal
if ~exist('eye_','var'),...
    error('This demo requires eye signal input. Please set it up or try the simulation mode.'); end

%% Remapping Trial Errors/Behavior Codes:
% remap trial error codes
trialerror(1,'No fixation - center',...
           2,'Break fixation - center',...
           3,'Break fixation - CS',...
           4,'Not assigned',...
           5,'Not assigned',...
           6,'Not assigned',...
           7,'Not assigned',...
           8,'Not assigned',...
           9,'Not assigned');
       
% remap behavior codes (universal)
bhv_code(   100,'Start Trial',...
            101,'Fixation On',...
            102,'Fixation Success',...
            103,'CS On',...
            104,'CS Off',...
            105,'Trace Start',...
            106,'Trace End',...
            107,'Not assigned',...
            108,'Not assigned',...
            109,'Not assigned',...
            110,'End Trial',...
            111,'Reward Trigger',...
            112,'Airpuff Trigger',...
            113,'Manual Reward');  % behavioral codes

%% TrialRecord Variables
condition = TrialRecord.CurrentCondition;
block = TrialRecord.CurrentBlock;
reward = TrialRecord.User.reward.reward(end);
airpuff = TrialRecord.User.airpuff.airpuff(end);

%% Hotkeys:
% manual reward
hotkey('r', 'goodmonkey(50, ''eventmarker'', 113, ''nonblocking'', 1);')
% stop task immediately
hotkey('x', 'escape_screen(); assignin(''caller'',''continue_'',false);');
% force next condition
hotkey('n', 'next_condition();');
% force next block
hotkey('b', 'next_block();');
hotkey('c', 'idle(0)');

%% Stimuli:
fixation_point = 1; % fixation point (fix_white_43pix_10mm)
fractal = 2; % fractal 'fractal-X.png' (200x200)
empty_stim = 3; % empty stimuli (0x0)
               
%% Time Intervals (in ms):
wait_for_fix = 50000;  % Time to fixate before timeout: 50000 ms
initial_fix = 1000; % Initial central fixation: 1000 ms
cs_presentation = 300; % Visual stimulus (CS) on: 350ms
editable('cs_presentation');
trace_interval = 1500; % Trace interval: 1500ms
editable('trace_interval');
iti_time = 1000; % ITI: 2000 ms
set_iti(iti_time);
reward_airpuff_time = 1000;
set_iti(reward_airpuff_time);

%% Error Intervals
error_timeout = 2000; % ITI error: 2000 ms
error_color = [0 0.7 0]; % error background color (green)

%% Fixation Window (in degrees):
fix_radius = 2.5;
fractal_radius = 30;

%% Reward Parameters:
pre_reward_delay = 50;
goodmonkey_num = 5;
editable('goodmonkey_num');
goodmonkey_length = 100;
editable('goodmonkey_length');
goodmonkey_pause = 150; % default = 40

%% SCENE BUILDING: 
% background: Analog Input Monitor
aim = AnalogInputMonitor(null_);
aim.Channel = 1;                  % General Input 1
aim.Position = [580 20 200 50];   % [left top width height]
aim.YLim = [0 5];
aim.Title = 'Lick';
aim.UpdateInterval = 1;           % redraw every 1 frame

% pulse camera on
% stim = Stimulator(null_);
% stim.Channel = 1;
% stim.Waveform = [0 5 0];
% stim.Frequency = 100;
% stim.WaveformNumber = 1;

%% Scene 1: Central Fixation
fix1 = SingleTarget(eye_);          % We use eye signals (eye_) for tracking. The SingleTarget adapter
fix1.Target = fixation_point;       % checks if the gaze is in the Threshold window around the Target.
fix1.Threshold = fix_radius;        % The Target can be either TaskObject# or [x y] (in degrees).
wth1 = WaitThenHold(fix1);          % The WaitThenHold adapter waits for WaitTime until the fixation
wth1.WaitTime = wait_for_fix;       % is acquired and then checks if the fixation is held for HoldTime.
wth1.HoldTime = initial_fix;        % Since WaitThenHold gets the fixation status from SingleTarget,
con1 = Concurrent(wth1);
con1.add(aim);
% con1.add(stim);
scene1 = create_scene(con1,fixation_point);  % In this scene, we will present the fixation_point (TaskObject #1)
                                             % and detect the eye movement indicated by the above parameters.

%% Scene 2 (CS Presentation)     
fix2 = SingleTarget(eye_);
fix2.Target = fixation_point;
fix2.Threshold = fix_radius;
wth2 = WaitThenHold(fix2);
wth2.WaitTime = 0;
wth2.HoldTime = cs_presentation;
con2 = Concurrent(wth2);
con2.add(aim);
scene2stim = horzcat(fixation_point, fractal);
scene2 = create_scene(con2,scene2stim);

%% Scene 3: Trace                                        
tc3 = TimeCounter(eye_);
tc3.Duration = trace_interval;
con3 = Concurrent(tc3);
con3.add(aim);
scene3 = create_scene(con3);

%% Scene 4: Airpuff (if applicable)
tc4 = TimeCounter(eye_);
tc4.Duration = reward_airpuff_time;
con4 = Concurrent(tc4);
con4.add(aim);
% pulse airpuff
if airpuff
    airpuff_stim = Stimulator(eye_);
    airpuff_stim.Channel = 2;
    airpuff_stim.Waveform = [0 5 0];
    airpuff_stim.Frequency = 10;
    airpuff_stim.WaveformNumber = 1;
    con4.add(airpuff_stim)
end
scene4 = create_scene(con4);

%% TASK:

% Scene 1
eventmarker(100);         % Start task (eventmarker 100)
run_scene(scene1,101);     % Fixation on (eventmaker 101)
if ~wth1.Success          % If the WithThenHold failed, (either fixation is not acquired or broken during hold)
    idle(0);              % Clear the screen
    if wth1.Waiting       % Check if we were waiting for fixation.
        error_outcome(1); % If so, fixation was never made and this is the "no fixation (4)" error.
    else
        error_outcome(2);  % If we were not waiting, it means that fixation was acquired but not held,
    end                    % so it is the "break fixation (2)" error.
    return
else
    eventmarker(102)       % WaitThenHold Success
end

% Scene 2
run_scene(scene2,103);      % CS Presentation
if ~wth2.Success
    error_outcome(3);
    return
end
eventmarker(104);           % CS Off 

% Scene 3
run_scene(scene3,105);     % Trace Interval
trialerror(0); % correct
eventmarker(106);
if reward
    send_reward()
elseif airpuff
    send_airpuff()
else
    send_nothing()
end

disp('############################################')


%% CUSTOM FUNCTIONS
function send_reward()
    eventmarker(110);
    lick_data_print()
    goodmonkey(goodmonkey_length, ...
        'numreward', goodmonkey_num, ...
        'pausetime', goodmonkey_pause,...
        'eventmarker', 111,...
        'nonblocking', 2)
    run_scene(scene4, 112); 
end

function send_airpuff()
    disp('Sending airpuff')
    eventmarker(110);
    lick_data_print()
    run_scene(scene4, 112); 
end

function send_nothing()
    eventmarker(110);
    lick_data_print()
    run_scene(scene4, 112);
end

function error_outcome(error_code)
    idle(iti_time,error_color);
    trialerror(error_code); % see line 8 (trialerror mapping)
end

function next_condition()
    TrialRecord.User.force_condition_change=1;
    dashboard(4,'Next condition')
end

function next_block()
    TrialRecord.User.force_block_change=1;
    dashboard(4,'Next block')
end

function replay_condition()
    TrialRecord.User.replay_uninstructed=1;
    dashboard(4,'Replay condition as instructed')

end

function lick_data_print()
    lick_data = get_analog_data('gen1', 500);
    lick_data_avg = mean(lick_data);
    lick_data_avg_str = horzcat('Avg Lick: ', num2str(lick_data_avg));
    disp(lick_data_avg_str)
    stim_chosen = TrialRecord.User.stim_chosen.stimuli(end);
    if condition == 1
        lick_rate_struct = TrialRecord.User.lick_rate_1;
    else
        lick_rate_struct = TrialRecord.User.lick_rate_2;
    end
    if stim_chosen == 1
        lick_rate_struct.A(end+1) = lick_data_avg;
    elseif stim_chosen == 2
        lick_rate_struct.B(end+1) = lick_data_avg;
    elseif stim_chosen == 3
        lick_rate_struct.C(end+1) = lick_data_avg;
    elseif stim_chosen == 4
        lick_rate_struct.D(end+1) = lick_data_avg;
    elseif stim_chosen == 5
        lick_rate_struct.E(end+1) = lick_data_avg;
    end
    if condition == 1
        TrialRecord.User.lick_rate_1 = lick_rate_struct;
    else
        TrialRecord.User.lick_rate_2 = lick_rate_struct;
    end
    disp('Condition 1')
    lick_data_avg_fractal_str_A = horzcat('  Fractal A Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_1.A)));
    disp(lick_data_avg_fractal_str_A)
    lick_data_avg_fractal_str_B = horzcat('  Fractal B Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_1.B)));
    disp(lick_data_avg_fractal_str_B)
    lick_data_avg_fractal_str_C = horzcat('  Fractal C Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_1.C)));
    disp(lick_data_avg_fractal_str_C)
    lick_data_avg_fractal_str_D = horzcat('  Fractal D Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_1.D)));
    disp(lick_data_avg_fractal_str_D)
    lick_data_avg_fractal_str_E = horzcat('  Fractal E Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_1.E)));
    disp(lick_data_avg_fractal_str_E)
    disp('Condition 2')
    lick_data_avg_fractal_str_A = horzcat('  Fractal A Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_2.A)));
    disp(lick_data_avg_fractal_str_A)
    lick_data_avg_fractal_str_B = horzcat('  Fractal B Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_2.B)));
    disp(lick_data_avg_fractal_str_B)
    lick_data_avg_fractal_str_C = horzcat('  Fractal C Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_2.C)));
    disp(lick_data_avg_fractal_str_C)
    lick_data_avg_fractal_str_D = horzcat('  Fractal D Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_2.D)));
    disp(lick_data_avg_fractal_str_D)
    lick_data_avg_fractal_str_E = horzcat('  Fractal E Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate_2.E)));
    disp(lick_data_avg_fractal_str_E)
end