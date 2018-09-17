function [setup, fix, dots, feedback, results, flip] = config_feedback(setup, window1)
    % Configuration of the Feedback Reponse control experiment
    % control_task.m
    % O.Colizoli June 2017, adapted from A. Urai

    % counterbalancing
    % hemifield [1 2 2 1]

    %-------------------
    % Thresholds, Trials, Blocks, Conditions
    %-------------------

    totalntrials = 25; %25!!

    setup.totalntrials      = totalntrials; %50; % number of trials for this whole experiment
    setup.nblocks           = 1; % 1 %number of blocks (only one single block for each fmri run)
    setup.ntrials           = setup.totalntrials/setup.nblocks; % total number of trials per block
    
    %-------------------
    % Hemifield counterbalancing
    %-------------------
    % If setup.hemifieldfirst = 1, 
        % ODD Sessions: ODD Runs = LEFT, EVEN Runs = RIGHT
        % EVEN Session: ODD Runs = RIGHT, EVEN Runs = LEFT
    % If setup.hemifieldfirst = 0, 
        % ODD Sessions: ODD Runs = RIGHT, EVEN Runs = LEFT
        % EVEN Session: ODD Runs = LEFT, EVEN Runs = RIGHT
    % see setupDots.m
    hemicondition = repmat([1 2 2 1], 1,250); % to prevent confounds with button conditions and feedback conditions
    if setup.participant > 0
        setup.hemifieldfirst    = hemicondition(setup.participant);
    else
        setup.hemifieldfirst    = 1;
    end

    %-------------------
    % Timing!
    %-------------------
   
    setup.boldbase  = 3; % for fmri, the seconds of pre and post baseline for BOLD (fixation cross only)

    % baseline pupil should be 2 seconds for fmri as the baseline period, and locked to TR 
    setup.fixtime                 = transpose((3-1).*rand(setup.ntrials,1)+1) ;     %2*ones(setup.nblocks, setup.ntrials); 
    setup.pupilreboundtime2       = transpose((6-3).*rand(setup.ntrials,1)+3) ;
    % ITIs
%     fisi    = [3.5 5.5 7.5 9.5 11.5]; % draw equally from this vector
%     nin     = floor(setup.ntrials/length(fisi)); % number divisible by ntrials
%     nleft   = mod(setup.ntrials,length(fisi)); % numbers left over after division by ntrials
%     m       = repmat(fisi, setup.nblocks, nin); % repeat fisi  
%     m(:,size(m,2)+1:size(m,2)+nleft) = repmat(fisi(1:nleft), setup.nblocks, 1); % for trials not divisible equally by 5, add extra isi's

    % Pupil rebound time AFTER feedback = ITI!!
    % shuffle each row separately
%     for i = 1:size(m,1)
%         setup.pupilreboundtime2(i,:) = m(i,randperm(size(m,2)));  
%     end
    
    %-------------------
    % Dots 
    %-------------------
    % preallocate dots structure
    [dots, fix]     = setupDots(window1, setup);

    %-------------------
    % Feedback Color 
    %-------------------
    feedback.color          = repmat([1 2]', [setup.ntrials setup.nblocks])';
    feedback.color          = feedback.color(1:setup.nblocks,1:setup.ntrials);
    for i = 1:size(feedback.color,1) % shuffle
        feedback.color(i,:) = feedback.color(i,randperm(size(feedback.color,2)));  
    end  


    %-------------------
    % Output Structures
    %-------------------
    results.timing                  = NaN(setup.nblocks, 2); % begin and end of block
    results.outputPhase             = NaN(setup.ntrials, 2); % for phases timing output
    results.output                  = NaN(setup.ntrials, 3); % for behavioral output (hemifield, ITI, feedback color)

    % preallocate a full flip structure to store the output of every dynamic flip
    flip.fix.VBL                = nan(ceil(max(setup.fixtime * window1.frameRate)), setup.ntrials);
    flip.fix.StimOns            = flip.fix.VBL;
    flip.fix.FlipTS             = flip.fix.VBL;
    flip.fix.Missed             = flip.fix.VBL;
    flip.fix.beampos            = flip.fix.VBL;
    
    flip.pupilrebound2.VBL        = nan(ceil(max(setup.pupilreboundtime2 * window1.frameRate)), setup.ntrials);
    flip.pupilrebound2.StimOns    = flip.pupilrebound2.VBL;
    flip.pupilrebound2.FlipTS     = flip.pupilrebound2.VBL;
    flip.pupilrebound2.Missed     = flip.pupilrebound2.VBL;
    flip.pupilrebound2.beampos    = flip.pupilrebound2.VBL;

    flip.bold1.VBL        = nan(1, 1);
    flip.bold1.StimOns    = flip.bold1.VBL;
    flip.bold1.FlipTS     = flip.bold1.VBL;
    flip.bold1.Missed     = flip.bold1.VBL;
    flip.bold1.beampos    = flip.bold1.VBL;

    flip.bold2.VBL        = nan(1, 1);
    flip.bold2.StimOns    = flip.bold2.VBL;
    flip.bold2.FlipTS     = flip.bold2.VBL;
    flip.bold2.Missed     = flip.bold2.VBL;
    flip.bold2.beampos    = flip.bold2.VBL;

    disp('configExperiment completed successfully')

end % end of the configExperiment function
