function [] = showFlipGraphs(setup, results, flip)
    %-------------
    % Show a measure of flip performance
    %-------------
    figure;
    for b = 1:setup.nblocks,
        for t = 1:setup.ntrials,      
        plot(diff(squeeze(flip.stim.VBL(b,t,:))));
        if any(diff(squeeze(flip.stim.VBL(b,t,:))) < 0.01),
            fprintf('weird fliptime block %d, trial %d \n', b, t);
        end
        hold on;
        end
    end
    axis tight;  title('flip performance'); xlabel('frames'); ylabel('frameDur');
    %-------------
    % Show some performance graphs
    %-------------
    figure;
    subplot(221); 
    hist(results.RT((results.correct==1)), setup.totalntrials);
    title('correct responses'); xlabel('RT'); ylabel('count');
    subplot(222); 
    hist(results.RT((results.correct==0)), setup.totalntrials);
    title('error responses'); xlabel('RT'); ylabel('count');

end