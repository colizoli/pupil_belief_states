function [setup, dots, fix, results, sound, flip] = config_fMRI_2AFC(setup, window1, audio)
    % Configuration of the fMRI 2AFC random dot motion experiment
    % fMRI_2AFC.m
    % O.Colizoli June 2015, adapted from A. Urai

    % counterbalancing
    % up/down   [1 2 1 2]
    % hemifield [1 2 2 1]
    % sounds    [1 1 2 2]

    %-------------------
    % Thresholds, Trials, Blocks, Conditions
    %-------------------

    try
        load(sprintf('Data/P%d_threshold.mat', setup.participant), 'fit1');
        [hard, easy] = define_coherence(setup);
        setup.cohlevel1 = fit1.x(dsearchn(fit1.y', hard)); % HARD take the coherence level that leads to a bit lower than 70% correct
        setup.cohlevel2 = fit1.x(dsearchn(fit1.y', easy)); % EASY take the coherence level that leads to a bit lower than 85% correct
    catch
        %setup.cohlevel1     = .20;
        %setup.cohlevel2     = .40;
        warning('no file found, using canonical threshold of 20-40%');
    end

    if setup.example
        totalntrials = 20; %26 must be divisible by nblocks
    else 
        totalntrials = 25; %25!!
    end

    setup.directions        = [90 270]; % up or down
    setup.totalntrials      = totalntrials; %50; % number of trials for this whole experiment
    setup.nblocks           = 1; % 1 %number of blocks (only one single block for each fmri run)
    setup.ntrials           = setup.totalntrials/setup.nblocks; % total number of trials per block
    setup.counterbalancing  = mod(setup.participant,2); % alternates even, odd for participant numbers in order 1:N [ 0 1 ]
    % SWITCH RESPONSE MAPPINGS HALF WAY!!!
    if setup.session > 2
        if setup.counterbalancing == true
            setup.counterbalancing = false;
        elseif setup.counterbalancing == false
            setup.counterbalancing = true;
        end
    end
    
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
    if setup.example || setup.debug
        setup.boldbase  = 1;
    else        
        setup.boldbase  = 12; % for fmri, the seconds of pre and post baseline for BOLD (fixation cross only)
    end
    setup.TR            = 2; % to calculate frames for fmri mode (waiting for trigger to proceed)
    % baseline pupil should be 2 seconds for fmri as the baseline period, and locked to TR 
    setup.fixtime       = transpose(.5 + (5-1)*rand(setup.ntrials,1)) ;     %2*ones(setup.nblocks, setup.ntrials); 
    % Stimulus onset duration
    setup.viewingtime   = .75; %.75 %want 750 ms for real experiment; % maximum viewing duration in seconds
    setup.maxRT         = 3 - setup.viewingtime; % maximum time after stim offset for a response in seconds
    setup.nframes       = ceil(setup.viewingtime * window1.frameRate); %number of frames the stimulus is displayed

    % ITIs
    fisi    = [3.5 5.5 7.5 9.5 11.5]; % draw equally from this vector
    nin     = floor(setup.ntrials/length(fisi)); % number divisible by ntrials
    nleft   = mod(setup.ntrials,length(fisi)); % numbers left over after division by ntrials
    m       = repmat(fisi, setup.nblocks, nin); % repeat fisi  
    m(:,size(m,2)+1:size(m,2)+nleft) = repmat(fisi(1:nleft), setup.nblocks, 1); % for trials not divisible equally by 5, add extra isi's

    %  Pupil rebound time BEFORE feedback
    for i = 1:size(m,1)
        setup.pupilreboundtime1(i,:) = m(i,randperm(size(m,2)));  
    end

    % Pupil rebound time AFTER feedback = ITI!!
    % shuffle each row separately
    for i = 1:size(m,1)
        setup.pupilreboundtime2(i,:) = m(i,randperm(size(m,2)));  
    end

    %-------------------
    % Dots 
    %-------------------
    % preallocate dots structure
    [dots, fix]     = setupDots(window1, setup);

    % !! this is very important, since it will determine which is the correct
    % response on each individual trial
    dots.direction          = repmat(setup.directions', [setup.ntrials setup.nblocks])';
    dots.direction          = dots.direction(1:setup.nblocks,1:setup.ntrials); % get right number of trials
    for i = 1:size(dots.direction,1) % shuffle
        dots.direction(i,:) = dots.direction(i,randperm(size(dots.direction,2)));  
    end

    % coherence levels, 2/3 hard, 1/3 easy
    nhard                   = floor(.67*setup.ntrials);
    neasy                   = setup.ntrials-nhard;
    dots.coherence          = repmat([ones(1,nhard)*setup.cohlevel1 ones(1,neasy)*setup.cohlevel2], [setup.nblocks 1]);
    for i = 1:size(dots.coherence,1) % shuffle
        dots.coherence(i,:) = dots.coherence(i,randperm(size(dots.coherence,2)));  
    end

    %-------------------
    % Audio
    %-------------------
    % 1/2 trials
    sound                = setupSounds(audio, setup);
    sound.tones          = repmat([1 2]', [setup.ntrials setup.nblocks])';
    sound.tones          = sound.tones(1:setup.nblocks,1:setup.ntrials);
    for i = 1:size(sound.tones,1) % shuffle
        sound.tones(i,:) = sound.tones(i,randperm(size(sound.tones,2)));  
    end   

    %-------------------
    % Output Structures
    %-------------------
    results.response                = NaN(setup.nblocks,setup.ntrials);
    results.correct                 = NaN(setup.nblocks,setup.ntrials);
    results.RT                      = NaN(setup.nblocks,setup.ntrials);
%    results.stimonset               = NaN(setup.nblocks,setup.ntrials,setup.nframes);
    results.timing                  = NaN(setup.nblocks,2); % begin and end of block
%     results.trialtiming             = NaN(setup.nblocks,setup.ntrials,2); % trial begin, trial end times
    results.outputPhase             = NaN(setup.ntrials, 6); % for phases timing output
    results.output                  = NaN(setup.ntrials, 7); % for behavioral output

    % logs scanner pulses
%     results.scannerpulses.key       = NaN(1,1000);
%     results.scannerpulses.trialtime = NaN(1,1000); % for pulse logging
%     results.scannerpulses.seconds   = NaN(1,1000);
%     results.pulsecount              = 0;
%     % in case they press a button by accident
%     results.nonpulse.key            = cell(1,1000);
%     results.nonpulse.trialtime      = NaN(1,1000); 
%     results.nonpulse.seconds        = NaN(1,1000); 
%     results.presscount              = 0;

    % preallocate a full flip structure to store the output of every dynamic flip
    flip.fix.VBL                = nan(ceil(max(setup.fixtime * window1.frameRate)), setup.ntrials);
    flip.fix.StimOns            = flip.fix.VBL;
    flip.fix.FlipTS             = flip.fix.VBL;
    flip.fix.Missed             = flip.fix.VBL;
    flip.fix.beampos            = flip.fix.VBL;
    
    flip.trigger.VBL            = nan(ceil(max(setup.TR * window1.frameRate)), setup.ntrials);
    flip.trigger.StimOns        = flip.trigger.VBL;
    flip.trigger.FlipTS         = flip.trigger.VBL;
    flip.trigger.Missed         = flip.trigger.VBL;
    flip.trigger.beampos        = flip.trigger.VBL;

    flip.stim.VBL               = nan(ceil(max(setup.viewingtime * window1.frameRate)), setup.ntrials);
    flip.stim.StimOns           = flip.stim.VBL;
    flip.stim.FlipTS            = flip.stim.VBL;
    flip.stim.Missed            = flip.stim.VBL;
    flip.stim.beampos           = flip.stim.VBL;

    flip.waitRT.VBL               = nan(ceil(max(setup.maxRT * window1.frameRate)), setup.ntrials);
    flip.waitRT.StimOns           = flip.waitRT.VBL;
    flip.waitRT.FlipTS            = flip.waitRT.VBL;
    flip.waitRT.Missed            = flip.waitRT.VBL;
    flip.waitRT.beampos           = flip.waitRT.VBL;

    flip.pupilrebound1.VBL        = nan(ceil(max(setup.pupilreboundtime1 * window1.frameRate)), setup.ntrials);
    flip.pupilrebound1.StimOns    = flip.pupilrebound1.VBL;
    flip.pupilrebound1.FlipTS     = flip.pupilrebound1.VBL;
    flip.pupilrebound1.Missed     = flip.pupilrebound1.VBL;
    flip.pupilrebound1.beampos    = flip.pupilrebound1.VBL;

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