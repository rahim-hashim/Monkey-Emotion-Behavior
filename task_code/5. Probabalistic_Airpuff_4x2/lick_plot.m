function [A_lick_rolling_avg, B_lick_rolling_avg, C_lick_rolling_avg, D_lick_rolling_avg] = lick_plot(TrialRecord)
    trial_avg = 5; % rolling avg of last N trials
    lick_rate_struct = TrialRecord.User.lick_rate;
    blink_rate_struct = TrialRecord.User.blink;
    len_elements = structfun(@numel,lick_rate_struct); % length of all struct fields
    if min(len_elements) >= trial_avg
        % fractal A
        A_lick_rolling_avg = movmean(lick_rate_struct.A, [trial_avg 0]); % trailing moving average
        A_blink_rolling_avg = movmean(blink_rate_struct.A, [trial_avg 0]); % trailing moving average
        % fractal B
        B_lick_rolling_avg = movmean(lick_rate_struct.B, [trial_avg 0]);
        B_blink_rolling_avg = movmean(blink_rate_struct.B, [trial_avg 0]);
        % fractal C
        C_lick_rolling_avg = movmean(lick_rate_struct.C, [trial_avg 0]);
        C_blink_rolling_avg = movmean(blink_rate_struct.C, [trial_avg 0]);
        % fractal D
        D_lick_rolling_avg = movmean(lick_rate_struct.D, [trial_avg 0]);
        D_blink_rolling_avg = movmean(blink_rate_struct.D, [trial_avg 0]);
    end
    hold on
    if min(len_elements) >= trial_avg
        figs = findall(groot,'Type','figure');
        % disp('fig names'); disp(cellstr([figs.Name])); disp('');
        % close all figures (not including native MonkeyLogic windows)
        figs(arrayfun(@(x)(contains(x.Name,{'airpuff','MonkeyLogic'})),figs)) = [];
        close(figs);
        figure('units','normalized','position',[0 0 .25 .25]);
        
        % x-axis for fractals
        A_x = linspace(1, numel(A_lick_rolling_avg), numel(A_lick_rolling_avg));
        B_x = linspace(1, numel(B_lick_rolling_avg), numel(B_lick_rolling_avg));
        C_x = linspace(1, numel(C_lick_rolling_avg), numel(C_lick_rolling_avg));
        D_x = linspace(1, numel(D_lick_rolling_avg), numel(D_lick_rolling_avg));

        % Plot 1
        % plot lick data
        subplot(2,1,1);
        hold on
        plot(A_x, A_lick_rolling_avg, 'r', 'DisplayName','A')
        plot(B_x, B_lick_rolling_avg, 'b', 'DisplayName','B')
        plot(C_x, C_lick_rolling_avg, 'g', 'DisplayName','C')
        plot(D_x, D_lick_rolling_avg, 'm', 'DisplayName','D')
        %customize plot
        yticks('auto')
        xticks('auto')
        xlabel('Trial #')
        ylabel('Avg Lick')
        ylim([0 5]) 
        legend({'A', 'B', 'C', 'D'}, 'Location', 'bestoutside')

        % Plot 2
        % plot blink data
        subplot(2,1,2);
        hold on
        plot(A_x, A_blink_rolling_avg, 'r', 'DisplayName','A')      
        plot(B_x, B_blink_rolling_avg, 'b', 'DisplayName','B')
        plot(C_x, C_blink_rolling_avg, 'g', 'DisplayName','C')
        plot(D_x, D_blink_rolling_avg, 'm', 'DisplayName','D')
        % customize plot
        yticks('auto')
        xticks('auto')
        xlabel('Trial #')
        ylabel('Avg Blink Prob')
        ylim([0 1])

    end
    
end