function [C,timingfile,userdefined_trialholder] = rh_Airpuff_userloop_add(MLConfig,TrialRecord)
% airpuff_userloop provides information for the next trial rather than
% relying on the conditions file, providing the stimuli and timing files

% Args:
%  - MLConfig: stores the current settings of ML (i.e. screen size)
%  - TrialRecord: stores the variables related to the current trial and 
%    the performance history.Note that the numbers in TrialRecord are 
%    not updated for the next trial until the userloop is finished. 
%    - Example: while in the userloop, TrialRecord.CurrentTrialNumber 
%      is 0 although the trial that we are about to execute is Trial 1.
%
% Returns:
%   - C: taskobjects
%   - timingfile: the timing file name
%   - userdefined_trialholder: the user-defined trialholder name.
    
%% Initializing Task

% default return value
C = [];
timingfile = 'airpuff_runscene.m';
userdefined_trialholder = '';
% path assignment for video files
exp_dir = append(MLConfig.MLPath.ExperimentDirectory,...
                 '/', MLConfig.FormattedName, '/');

fix_list = {'_fix.png'};
image_list = {'_fractal_A', '_fractal_B', '_fractal_C', '_fractal_D'};

% The userloop is called twice before Trial 1 starts: 
%   - once before the pause menu shows up (MonkeyLogic does that, 
%     to retrieve the timingfile name(s))
%   - once immediately before Trial 1

% The very first call to this function is just to retrieve the timing
% filename before the task begins and we don't want to waste our preset
% values for this, so we just return if it is the first call.
persistent timing_filename_returned
if isempty(timing_filename_returned)
    timing_filename_returned = true;
    % assign new TrialRecord field for stim_list 
    TrialRecord.User.stim_list = struct('stim_list', image_list);
    % assign new TrialRecord field for 'n' hotkey
    TrialRecord.User.force_condition_change = 0;
    % assign new TrialRecord field for 'b' hotkey
    TrialRecord.User.force_block_change = 0;
    % assign new TrialRecord field for 1, 2, ... hotkeys
    TrialRecord.User.force_condition_1 = 0;
    TrialRecord.User.force_condition_2 = 0;
    % assign new TrialRecord field for replaying incorrect uninstructed
    TrialRecord.User.replay_uninstructed = 0;
    % assign new TrialRecord field for stimuli selected
    TrialRecord.User.stim_chosen = struct('stimuli', []);
    % assign new TrialRecord field for reward contingency
    TrialRecord.User.reward = struct('reward_prob', [],...
                                     'reward', [],...
                                     'random_num', []);
    TrialRecord.User.airpuff = struct('airpuff_prob', [],...
                                     'airpuff', [],...
                                     'side', [],...
                                     'random_num', []);
    % assign new TrialRecord field for lick rate
    TrialRecord.User.lick_rate = struct('A', [],...
                                        'B', [],...
                                        'C', [],...
                                        'D', []);
    % assign new TrialRecord field for lick rate
    TrialRecord.User.eye_data_x = struct('A', [],...
                                       'B', [],...
                                       'C', [],...
                                       'D', []);
    TrialRecord.User.eye_data_y = struct('A', [],...
                                        'B', [],...
                                        'C', [],...
                                        'D', []);
    TrialRecord.User.blink = struct('A', [],...
                                    'B', [],...
                                    'C', [],...
                                    'D', []);
    return
end

%% Task

% block and trial
block = TrialRecord.CurrentBlock;
condition = TrialRecord.CurrentCondition;
trials_per_block = 250;
num_blocks = 20;

% changing frequency of conditions
ratio_conditions = [1 1]; % ratio of condition 1 to condition 2 (i.e. 3:1)
blockwise_trials = true;

% unchanging frequency of conditions
condition_mod = mod(block, 2) + 1;
if condition_mod == 1
    condition = 1;
else
    condition = 2;
end
% condition = 1;

% Probability of reward/airpuff
reward_prob_100 = 1.0;
reward_prob_high = 1.0;
reward_prob_low = 0.5;
airpuff_prob_100 = 1.0;
airpuff_prob_high = 1;
airpuff_prob_low = 0.5;

% Probability of each fractal
prob_fractal = [1 1 1 1];

% Randomly select reward
random_num = rand();

% Set a new condition
persistent condition_sequence condition_randomized ...
           index_chosen ratio_randomized ratio_stimuli

if blockwise_trials == true
    if isempty(TrialRecord.TrialErrors) % first trial
        ratio_stimuli = prob_fractal;
    end
else
    ratio_stimuli = prob_fractal;
end

if isempty(TrialRecord.TrialErrors)... % first trial
        || TrialRecord.TrialErrors(end)==0 ... % last trial correct
        || TrialRecord.User.force_condition_change==1 % hot key ('n') changes to the next condition
    
    if blockwise_trials == false
        ratio_sequence = [];
        for i=1:numel(ratio_stimuli)
            sequence_copy = ratio_sequence;
            add_vector = ones(1, ratio_stimuli(i))*i;
            ratio_sequence = [sequence_copy add_vector];
        end
    else
        % reset blockwise ratios
        if isequal(ratio_stimuli, [0 0 0 0])
            ratio_stimuli = prob_fractal;
        end
        ratio_sequence = [];
        for i=1:numel(ratio_stimuli)
            sequence_copy = ratio_sequence;
            add_vector = ones(1, ratio_stimuli(i))*i;
            ratio_sequence = [sequence_copy add_vector];
        end
    end
    disp(ratio_stimuli)
    ratio_randomized = ratio_sequence(randperm(length(ratio_sequence)));
    index_chosen = ratio_randomized(1);
    % not a free fix reward trial
%     num_correct_trials = sum(TrialRecord.TrialErrors(:) == 0);
%     if mod(num_correct_trials,2) == 0
%         % fractal 4 is always free reward
%         index_chosen = 4;
%     else
    ratio_stimuli(index_chosen) = ratio_stimuli(index_chosen) - 1;
% 
%     end

    % override random selection and select condition
    TrialRecord.User.force_condition_change=0;
    if TrialRecord.User.force_condition_1==1, condition=1; end 
    TrialRecord.User.force_condition_1=0;
    if TrialRecord.User.force_condition_2==1, condition=2; end
    TrialRecord.User.force_condition_2=0;
    
    % Increase the block number after trials_per_block correct trials
    correct_trial_count = sum(TrialRecord.TrialErrors==0);
    block = mod(floor(correct_trial_count/trials_per_block),num_blocks)+1;
    if TrialRecord.User.force_block_change==1
        if block + 1 > num_blocks
            block = block + 1;
        end
        TrialRecord.User.force_block_change = 0;
    end
end

%% Set the stimuli
fix = fix_list{1};
stim = image_list{index_chosen};
C = {sprintf('pic(%s,0,0)',fix), ...
    sprintf('pic(%s,0,0,500,500)',stim), ...
    sprintf('crc(0.001,[0 0 0],0,0,0)')
    };

%% Assigning reward/airpuff conditions
if condition == 1
    if index_chosen == 1
        reward_cond = 1;
        airpuff_cond = 0;
        reward_prob_selected = reward_prob_100;
    elseif index_chosen == 2
        reward_cond = 1;
        airpuff_cond = 0;
        reward_prob_selected = reward_prob_low;
    elseif index_chosen == 3
        reward_cond = 0;
        airpuff_cond = 1;
        airpuff_prob_selected = airpuff_prob_low;
    elseif index_chosen == 4
        reward_cond = 0;
        airpuff_cond = 1;
        airpuff_prob_selected = airpuff_prob_100;
    end
elseif condition == 2
    if index_chosen == 1
        reward_cond = 0;
        airpuff_cond = 1;
        airpuff_prob_selected = airpuff_prob_100;
    elseif index_chosen == 2
        reward_cond = 0;
        airpuff_cond = 1;
        airpuff_prob_selected = airpuff_prob_low;
    elseif index_chosen == 3
        reward_cond = 1;
        airpuff_cond = 0;
        reward_prob_selected = reward_prob_low;
    elseif index_chosen == 4
        reward_cond = 1;
        airpuff_cond = 0;
        reward_prob_selected = reward_prob_high;
    end
end

% Assinging reward/airpuff
if reward_cond == 1
    if random_num <= reward_prob_selected
        reward_given = 1;
    else
        reward_given = 0;
    end
    airpuff_given = 0;
    airpuff_prob_selected = 0;
elseif airpuff_cond == 1
    if random_num <= airpuff_prob_selected
        airpuff_given = 1;
    else
        airpuff_given = 0;
    end
    reward_given = 0;
    reward_prob_selected = 0;
end

% %% Displaying Trial Parameters
% block_no = horzcat('Block: ', num2str(block));
% disp(block_no)
% trial_no = horzcat('Trial: ', num2str(TrialRecord.CurrentTrialNumber+1));
% disp(trial_no)
% current_condition = horzcat('Condition: ', num2str(condition));
% disp(current_condition)
% ratio_array = horzcat('Condition Ratio ', mat2str(ratio_randomized));
% disp(ratio_array)
current_stim = horzcat('Fractal: ', stim);
disp(current_stim)
random_val_str = horzcat('Random Number: ', num2str(random_num));
disp(random_val_str)
reward_prob_str = horzcat('  Reward Prob: ', num2str(reward_prob_selected));
disp(reward_prob_str)
reward_str = horzcat('  Reward: ', num2str(reward_given));
disp(reward_str)
airpuff_prob_str = horzcat('  Airpuff Prob: ', num2str(airpuff_prob_selected));
disp(airpuff_prob_str)
airpuff_str = horzcat('  Airpuff: ', num2str(airpuff_given));
disp(airpuff_str)

%% Add to TrialRecord
% stim container
stim_container = TrialRecord.User.stim_chosen;
stim_container.stimuli(end+1) = index_chosen;
TrialRecord.User.stim_chosen = stim_container;

% reward_cond container
reward_container = TrialRecord.User.reward;
reward_container.reward(end+1) = reward_given;
reward_container.reward_prob(end+1) = reward_prob_selected;
reward_container.random_num(end+1) = random_num;
TrialRecord.User.reward = reward_container;

% airpuff_cond container
airpuff_container = TrialRecord.User.airpuff;
airpuff_container.airpuff(end+1) = airpuff_given;
airpuff_container.airpuff_prob(end+1) = airpuff_prob_selected;
airpuff_container.random_num(end+1) = random_num;
TrialRecord.User.airpuff = airpuff_container;

%%
% Set the block number and the condition number of the next trial. Since
% this userloop function provides the list of TaskObjects and timingfile
% names, ML does not need the block/condition number. They are just for
% your reference.
% However, if TrialRecord.NextBlock is -1, the task ends immediately
% without running the next trial.
TrialRecord.NextBlock = block;
TrialRecord.NextCondition = condition;
