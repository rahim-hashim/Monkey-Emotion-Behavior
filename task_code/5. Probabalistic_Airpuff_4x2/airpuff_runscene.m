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
            107,'Outcome Start',...
            108,'Reward Trigger',...
            109,'Airpuff Trigger',...
            110,'Outcome',...
            111,'Outcome End',...
            112,'Manual Reward',...
            113,'End Trial');  % behavioral codes

%% TrialRecord Variables
condition = TrialRecord.CurrentCondition;
block = TrialRecord.CurrentBlock;
reward = TrialRecord.User.reward.reward(end);
airpuff_struct = TrialRecord.User.airpuff;
airpuff = airpuff_struct.airpuff(end);


%% End Session
if block > 2
    escape_screen()
end

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

stim_name = TrialRecord.User.stim_chosen.stimuli(end);
               
%% Time Intervals (in ms):
wait_for_fix = 50000;  % Time to fixate before timeout: 50000 ms
initial_fix = 500; % Initial central fixation: 500 ms
cs_presentation = 350; % Visual stimulus (CS) on: 350ms
editable('cs_presentation');
trace_interval = 1500; % Trace interval: 1500ms
editable('trace_interval');
iti_time = 2500; % ITI: 1500 ms
set_iti(iti_time);
reward_airpuff_time = 2000; % default = 1000

%% Error Intervals
error_timeout = 2500; % ITI error: 2000 ms
error_color = [0 0.7 0]; % error background color (green)

%% Fixation Window (in degrees):
fix_radius = 2.5;
fractal_radius = 30;
blink_threshold = 10;

%% Reward Parameters:

reward_prob = TrialRecord.User.reward.reward_prob(end);
reward_mag = TrialRecord.User.reward.reward_mag(end);

% large reward
pre_reward_delay = 50;
goodmonkey_num = 8;
editable('goodmonkey_num');
goodmonkey_length = 200;
editable('goodmonkey_length');
goodmonkey_pause = 200; % default = 40
editable('goodmonkey_pause');

% small reward
okmonkey_num = 3;
editable('okmonkey_num');
okmonkey_length = 200;
editable('okmonkey_length');
okmonkey_pause = 200; % default = 40
editable('okmonkey_pause');

% fix reward
fixreward_num = 6;
editable('fixreward_num');
fixreward_length = 150;
editable('fixreward_length');
fixreward_pause = 150; % default = 40
editable('fixreward_pause');

% fix reward
init_num = 1;
init_length = 150;
init_pause = 150; % default = 40

%% Airpuff Parameters:
airpuff_prob = TrialRecord.User.airpuff.airpuff_prob(end);
airpuff_mag = TrialRecord.User.airpuff.airpuff_mag(end);

num_pulses = randi([3,4],1);
large_airpuff_waveform = repmat([0 5 0 0], 1, num_pulses);
small_airpuff_waveform = [0 5 0 0];
airpuff_freq = 10;

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

%% Scene 4: Reward/Airpuff (if applicable)
tc4 = TimeCounter(eye_);
tc4.Duration = reward_airpuff_time;
con4 = Concurrent(tc4);
con4.add(aim);
% pulse airpuff
if airpuff
    airpuff_stim = Stimulator(eye_);
    % large airpuff
    if airpuff_mag == 1
        airpuff_stim.Channel = [1 2]; % both sides
        airpuff_stim.Waveform = [large_airpuff_waveform; large_airpuff_waveform];
        airpuff_struct.L_side(end+1) = 1;
        airpuff_struct.R_side(end+1) = 1;
    % small airpuff
    else
        num_pulses = 1;
        airpuff_random_num = rand();
        if airpuff_random_num > 0.5
            airpuff_stim.Channel = 1;
            airpuff_struct.L_side(end+1) = 1;
            airpuff_struct.R_side(end+1) = 0;
        else
            airpuff_stim.Channel = 2;
            airpuff_struct.L_side(end+1) = 0;
            airpuff_struct.R_side(end+1) = 1;
        end
        airpuff_stim.Waveform = [small_airpuff_waveform];
    end
    airpuff_stim.Frequency = airpuff_freq; % rate of waveform (samples/sec)
    airpuff_stim.WaveformNumber = 1;
    con4.add(airpuff_stim)
else
    num_pulses = 0;
    airpuff_struct.L_side(end+1) = 0;
    airpuff_struct.R_side(end+1) = 0;
end
TrialRecord.User.airpuff.num_pulses(end+1) = num_pulses;
num_pulses_str = horzcat('Num Pulses: ', num2str(num_pulses));
disp(num_pulses_str)
TrialRecord.User.airpuff.L_side = airpuff_struct.L_side;
TrialRecord.User.airpuff.R_side = airpuff_struct.R_side;
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
    init_random_num = rand();
    if init_random_num > 0.5
        init_reward()
    end
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
eventmarker(106);
if reward
    send_reward()
elseif airpuff
    send_airpuff()
else
    send_nothing()
end
eventmarker(113);

disp('############################################')


%% CUSTOM FUNCTIONS
function init_reward()
    goodmonkey(init_length, ...
        'numreward', init_num, ...
        'pausetime', init_pause,...
        'eventmarker', 112,...
        'nonblocking', 1)
end

function send_reward()
    eventmarker(107);
    data_print()
    if reward_mag == 1
        goodmonkey(goodmonkey_length, ...
            'numreward', goodmonkey_num, ...
            'pausetime', goodmonkey_pause,...
            'eventmarker', 108,...
            'nonblocking', 2)
        TrialRecord.User.reward.drops(end+1) = goodmonkey_num;
        TrialRecord.User.reward.length(end+1) = goodmonkey_length;
    else
        goodmonkey(okmonkey_length, ...
        'numreward', okmonkey_num, ...
        'pausetime', okmonkey_pause,...
        'eventmarker', 108,...
        'nonblocking', 2)
        TrialRecord.User.reward.drops(end+1) = okmonkey_num;
        TrialRecord.User.reward.length(end+1) = okmonkey_length;
    end
    run_scene(scene4, 110);
    eventmarker(111);
    trialerror(0); % correct
end

function send_nothing()
    eventmarker(107);
    data_print()
    TrialRecord.User.reward.drops(end+1) = 0;
    TrialRecord.User.reward.length(end+1) = 0;
    run_scene(scene4, 110);
    eventmarker(111);
    trialerror(0); % correct
end

function send_airpuff()
    eventmarker(107);
    data_print()
    TrialRecord.User.reward.drops(end+1) = 0;
    TrialRecord.User.reward.length(end+1) = 0;
    run_scene(scene4, 109);
    eventmarker(111);
    trialerror(0); % correct
end


function error_outcome(error_code)
    TrialRecord.User.reward.drops(end+1) = 0;
    TrialRecord.User.reward.length(end+1) = 0;
    idle(error_timeout,error_color);
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

function data_print()
    % prints lick and blink data
    % getting the last <mean_window> elements of lick/blink array
    % before trial outcome (reward, airpuff, nothing)
    mean_window = 1000;

    % lick data
    lick_data = get_analog_data('gen1', mean_window);
    lick_data_avg = mean(lick_data);
    lick_data_avg_str = horzcat('Avg Lick: ', num2str(lick_data_avg));
    disp(lick_data_avg_str)
    stim_chosen = TrialRecord.User.stim_chosen.stimuli(end);
    if stim_chosen == 1
        TrialRecord.User.lick_rate.A(end+1) = lick_data_avg;
    elseif stim_chosen == 2
        TrialRecord.User.lick_rate.B(end+1) = lick_data_avg;
    elseif stim_chosen == 3
        TrialRecord.User.lick_rate.C(end+1) = lick_data_avg;
    elseif stim_chosen == 4
        TrialRecord.User.lick_rate.D(end+1) = lick_data_avg;
    end
    % eye data
    eye_data = get_analog_data('eye', mean_window);
    eye_data_avg = mean(eye_data);

    blink_any = any(abs(eye_data(:)) > blink_threshold);

    eye_data_avg_str = horzcat('Avg Eye X: ', num2str(eye_data_avg(1)),...
                                    ' | Y: ', num2str(eye_data_avg(2)));
    disp(eye_data_avg_str)
    blink_any_str = horzcat('Blink: ', num2str(blink_any));
    disp(blink_any_str)
    stim_chosen = TrialRecord.User.stim_chosen.stimuli(end);
    if stim_chosen == 1
        TrialRecord.User.eye_data_x.A(end+1) = eye_data_avg(1);
        TrialRecord.User.eye_data_y.A(end+1) = eye_data_avg(2);
        TrialRecord.User.blink.A(end+1) = blink_any;
    elseif stim_chosen == 2
        TrialRecord.User.eye_data_x.B(end+1) = eye_data_avg(1);
        TrialRecord.User.eye_data_y.B(end+1) = eye_data_avg(2);
        TrialRecord.User.blink.B(end+1) = blink_any;
    elseif stim_chosen == 3
        TrialRecord.User.eye_data_x.C(end+1) = eye_data_avg(1);
        TrialRecord.User.eye_data_y.C(end+1) = eye_data_avg(2);
        TrialRecord.User.blink.C(end+1) = blink_any;
    elseif stim_chosen == 4
        TrialRecord.User.eye_data_x.D(end+1) = eye_data_avg(1);
        TrialRecord.User.eye_data_y.D(end+1) = eye_data_avg(2);
        TrialRecord.User.blink.D(end+1) = blink_any;
    end

    avg_fractal_str_A = horzcat('  Fractal A Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate.A)),... 
                                   '  Eye X: ', num2str(mean(TrialRecord.User.eye_data_x.A)),...
                                    ' | Y: ', num2str(mean(TrialRecord.User.eye_data_y.A)),...
                                    ' blink: ', num2str(mean(TrialRecord.User.blink.A)));
    disp(avg_fractal_str_A)
    avg_fractal_str_B = horzcat('  Fractal B Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate.B)),... 
                                   '  Eye X: ', num2str(mean(TrialRecord.User.eye_data_x.B)),...
                                    ' | Y: ', num2str(mean(TrialRecord.User.eye_data_y.B)),...
                                    ' blink: ', num2str(mean(TrialRecord.User.blink.B)));
    disp(avg_fractal_str_B)
    avg_fractal_str_C = horzcat('  Fractal C Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate.C)),... 
                                   '  Eye X: ', num2str(mean(TrialRecord.User.eye_data_x.C)),...
                                    ' | Y: ', num2str(mean(TrialRecord.User.eye_data_y.C)),...
                                    ' blink: ', num2str(mean(TrialRecord.User.blink.C)));
    disp(avg_fractal_str_C)
    avg_fractal_str_D = horzcat('  Fractal D Avg Lick: ', num2str(mean(TrialRecord.User.lick_rate.D)),... 
                                   '  Eye X: ', num2str(mean(TrialRecord.User.eye_data_x.D)),...
                                    ' | Y: ', num2str(mean(TrialRecord.User.eye_data_y.D)),...
                                    ' blink: ', num2str(mean(TrialRecord.User.blink.D)));
    disp(avg_fractal_str_D)

end