function lick_plot(TrialRecord)
    hold on
    num_trials = length(TrialRecord.User.reward.random_num);
    x = linspace(1, num_trials, num_trials);
    plot(x, ...
         TrialRecord.User.reward.random_num)
    yticks('auto')
    xticks('auto')
    xlabel('Trial #')
    ylim([0 1])
end