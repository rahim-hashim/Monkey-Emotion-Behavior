function [A_rolling_avg, B_rolling_avg, C_rolling_avg, D_rolling_avg] = lick_plot(TrialRecord)
    trial_avg = 3; % rolling avg of last N trials
    if TrialRecord.CurrentCondition == 1
        lick_rate_struct = TrialRecord.User.lick_rate;
    elseif TrialRecord.CurrentCondition == 2
        lick_rate_struct = TrialRecord.User.lick_rate;
    end
    len_elements = structfun(@numel,lick_rate_struct); % length of all struct fields
    if min(len_elements) > trial_avg
        A_rolling_avg = movmean(lick_rate_struct.A, [trial_avg 0]); % trailing moving average
        B_rolling_avg = movmean(lick_rate_struct.B, [trial_avg 0]);
        C_rolling_avg = movmean(lick_rate_struct.C, [trial_avg 0]);
        D_rolling_avg = movmean(lick_rate_struct.D, [trial_avg 0]);
    end
    hold on
    if min(len_elements) > trial_avg
        A_x = linspace(1, numel(A_rolling_avg), numel(A_rolling_avg));
        plot(A_x, A_rolling_avg, 'r', 'DisplayName','A')
        B_x = linspace(1, numel(B_rolling_avg), numel(B_rolling_avg));
        plot(B_x, B_rolling_avg, 'b', 'DisplayName','B')
        C_x = linspace(1, numel(C_rolling_avg), numel(C_rolling_avg));
        plot(C_x, C_rolling_avg, 'g', 'DisplayName','C')
        D_x = linspace(1, numel(D_rolling_avg), numel(D_rolling_avg));
        plot(D_x, D_rolling_avg, 'y', 'DisplayName','D')
    end
    yticks('auto')
    xticks('auto')
    xlabel('Trial #')
    ylim([0 5])
end