%% Control Feedback Response with EyeLink
% Anne Urai, Feb 2015
% Modified by Olympia Colizoli, June 2017

% Participants don't have to respond
% Fixation only, while dot motion and visual 'feedback' is presented (red
% or green)

% Phases 
% phase 1 - baseline period ([.5,5] random)
% phase 2 - feedback and ITI after feedback

% Behavioral output
% column 1 - hemifield (-1 left, 1 right)
% column 2 - ITI
% column 3 - feedback (1 green, 2 red)

close all; clear all; clc; dbstop if error;

%% SETUP
setup.Eye          = true;
setup.scanner      = 1;  % 1 = Psychophysics lab UKE, 5 = O's laptop
setup.debug        = false;

setup.localizer    = false; % work around

%-------------
% Ask for subject number, default = 0
%-------------
setup.participant       = input('Participant number? ');
if isempty(setup.participant)
    setup.participant   = 100; %test
end
%-------------
% Ask for session number, default = 0
%-------------
setup.session           = input('Session? ');
if isempty(setup.session)
    setup.session       = 0; %test
end
%-------------
% Ask for fmri run number, default = 0
%-------------
setup.run               = input('Run? ');
if isempty(setup.run)
    setup.run           = 0;
end

%-------------
% window1 settings
%-------------
window1 = define_window(setup);

window1.skipChecks      = 0;
[window1, audio]        = SetupPTB(window1, setup); %load all the psychtoolbox things

%-------------
% REFRESH RATE
%-------------
window1 = define_refresh(setup, window1);

%-------------
% Present loading text on the screen
%-------------
Screen('TextSize', window1.h, 15);
Screen('TextFont', window1.h, 'Trebuchet');
Screen('TextColor', window1.h, [255 255 255] ); %white
%Screen('TextColor', window1.h, [0 0 0] );
Screen('DrawText', window1.h, 'Loading...', window1.center(1), window1.center(2));
Screen('Flip', window1.h);
%-------------
% INITIALIZE EXPERIMENTAL PARAMETERS
%-------------
[setup, fix, dots, feedback, results, flip] = config_feedback(setup, window1);
%-------------
% fixation cross colors for feedback
%-------------
white   = [255,255,255];
red     = [255,0,0];
green   = [0,255,0];
yellow  = [255,246,0];
% black   = [0 0 0];
% grey    = [118 118 118];
% switch black/grey names
grey   = [0 0 0];
black    = [118 118 118];
color   = white; %fixation cross white
%-------------
% Initialize EyeLink
%-------------
if setup.Eye
    edfFile = ELconfig(window1, setup, setup.run);
    Eyelink ('Message', sprintf('EyeLink configured at %.2f', GetSecs));  
    Eyelink('command', 'sample_rate = %d',1000);
    Eyelink('command', 'calibration_type = HV5');
    % you must send this command with value NO for custom calibration
    % you must also reset it to YES for subsequent experiments
    Eyelink('command', 'generate_default_targets = NO');
end 


%% -------------
% OUTPUT FILE
%-------------
% Get Time Stamp
setup.datetime = datestr(now, 'yyyy-mm-dd_HH-MM-SS');
outfile1 = sprintf('Data/Phases_P%d_s%d_r%d_%s.txt',setup.participant, setup.session, setup.run , setup.datetime); % name of output file
fid1 = fopen(outfile1,'w');
% Conditions and Behavior
outfile2 = sprintf('Data/Behav_P%d_s%d_r%d_%s.txt',setup.participant, setup.session, setup.run , setup.datetime); % name of output file
fid2 = fopen(outfile2,'w');

%% INSTRUCTIONS
%-------------

Screen('FillRect', window1.h, [118,118,118]);

DrawFormattedText(window1.h, ['You do not have to respond. Continue to look at the fixation point.'],  window1.center(1)-300, window1.center(2));   
Screen('Flip', window1.h);

WaitSecs(3);    

Screen('Flip', window1.h);

%% -------------
% WAIT FOR FIRST PULSE TO START
% ---------------

BEGIN = GetSecs;

if setup.Eye
    Eyelink ('Message', sprintf('measuring started at %.2f', BEGIN));           
end

results.timing.start = BEGIN; %will be first pulse if in fmri mode
          
block = 1;
           
%% -------------
% BOLD BASELINE 1
%-------------
% START with an epoch of BOLD baseline
% Show only fixation cross
%-------------           
if setup.Eye
    Eyelink ('Message', sprintf('block -1 started at %.2f', GetSecs));
end
fprintf('block -1 started at %.2f \n', GetSecs-BEGIN);
results.timing.bold1start = GetSecs-BEGIN;

window1      = drawFixation(window1, dots, fix); % fixation
Screen('DrawingFinished', window1.h); % helps with managing the flip performance
         
            [flip.bold1.VBL(1, 1), ...
                flip.bold1.StimOns(1, 1), ...
                flip.bold1.FlipTS(1, 1), ...
                flip.bold1.Missed(1, 1), ...
                flip.bold1.beampos(1, 1)] = Screen('Flip', window1.h);
                %flip.bold1.beampos(1, 1)] = Screen('Flip', window1.h, TimingCnt);
            %TimingCnt = flip.bold1.VBL(1, 1) + window1.frameDur - window1.slack;
            
WaitSecs(setup.boldbase);
        
if setup.Eye
    Eyelink ('Message', sprintf('block -1 ended at %.2f', GetSecs));           
end
fprintf('block -1 ended at %.2f \n', GetSecs-BEGIN);
results.timing.bold1end = GetSecs-BEGIN;
    
%% LOOP OVER TRIALS
for trial = 1 : setup.ntrials
    %% PUPIL BASELINE STAGE 
    %-------------
    % PHASE 1
    % Dot motion: only noise
    % [.5 5] (change in: setup.fixtime)
    %-------------

    if trial == 1
        TimingCnt = GetSecs + window1.frameDur - window1.slack;
    else 
        TimingCnt = TimingCnt + window1.frameDur - window1.slack;
    end
    %-------------
    % [.5 5] second fixation interval before stim onset
    %-------------

    if setup.Eye
        Eyelink ('Message', sprintf('trial %i started at %.2f', trial-1, GetSecs)); WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i phase 1 started at %.2f trigger None', trial-1, GetSecs));          
    end
    fprintf('trial %i phase 1 started at %.2f \n', trial, GetSecs-BEGIN);
    
    %-------------
    % loop stimuli over frames
    %------------- 
    for frameNum = 1:ceil(setup.fixtime(block, trial)*window1.frameRate)
        window1      = dots_noise(window1, dots);
        window1      = drawFixation(window1, dots, fix); % fixation
        Screen('DrawingFinished', window1.h); % helps with managing the flip performance
            
            [flip.fix.VBL(frameNum, trial), ...
                flip.fix.StimOns(frameNum, trial), ...
                flip.fix.FlipTS(frameNum, trial), ...
                flip.fix.Missed(frameNum, trial), ...
                flip.fix.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.fix.VBL(frameNum, trial) + window1.frameDur - window1.slack;
    end % frames
    
    % phase 1
    results.outputPhase(trial, 1) = flip.fix.StimOns(1, trial);
    
        
    %% ITI (FEEDBACK and ITI)   
    %-------------
    % PHASE 2
    % Dot motion: noise
    % Rebound time AFTER feedback: setup.pupilreboundtime2 
    %-------------

    if setup.Eye
        Eyelink ('Message', sprintf('trial %i phase 2 started at %.2f trigger None', trial-1, GetSecs));          
    end
    fprintf('trial %i phase 2 started at %.2f \n', trial, GetSecs-BEGIN);
        
    %-------------
    % FEEDBACK
    %-------------
    % CORRECT
    if feedback.color(block,trial) == 1 
        fix.color1 = green; fix.color2 = green;
    % INCORRECT
    elseif feedback.color(block,trial) == 2 
        fix.color1 = red; fix.color2 = red;
    end
    
    %-------------
    % Loop stimuli over frames
    %-------------
    for frameNum = 1:ceil(setup.pupilreboundtime2(block, trial)*window1.frameRate),       
        window1      = dots_noise(window1, dots);
        if frameNum > 50 % 830 ms at 60 Hz
            fix.color1 = grey; fix.color2 = black; % take off color feedback
        end
        window1      = drawFixation(window1, dots, fix); % fixation
        
        Screen('DrawingFinished', window1.h); % helps with managing the flip performance
            
        [flip.pupilrebound2.VBL(frameNum, trial), ...
                flip.pupilrebound2.StimOns(frameNum, trial), ...
                flip.pupilrebound2.FlipTS(frameNum, trial), ...
                flip.pupilrebound2.Missed(frameNum, trial), ...
                flip.pupilrebound2.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);             
            TimingCnt = flip.pupilrebound2.VBL(frameNum, trial) + window1.frameDur - window1.slack;            
    end % for setup.pupilreboundtime2
    
    % phase 6
    results.outputPhase(trial, 2) = flip.pupilrebound2.StimOns(1, trial);     

    %-------------
    % Send EyeLink trial info
    %-------------       
    if setup.Eye %d
        Eyelink ('Message', sprintf('trial %i parameter hemifield : %.2f ', trial-1, dots.hemi));                WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter fixation : %.2f ', trial-1, setup.fixtime(trial)));      WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter ITI : %.2f ', trial-1, setup.pupilreboundtime2(trial))); WaitSecs(.0005); 
        Eyelink ('Message', sprintf('trial %i parameter feedback : %.2f ', trial-1, feedback.color(trial))); WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i stopped at %.2f trigger None ', trial-1, GetSecs));
    end
    % for output file
    results.output(trial, 1) = dots.hemi;
    results.output(trial, 2) = setup.pupilreboundtime2(block, trial);
    results.output(trial, 3) = feedback.color(block, trial);
    
    results.outputPhaseSecs = results.outputPhase-BEGIN;
    dlmwrite(outfile1,results.outputPhase-BEGIN,'\t');     
    dlmwrite(outfile2,results.output,'\t');     
        
end % END LOOP OVER TRIALS
    
%% -------------
% BOLD BASELINE 2
% -------------

if setup.Eye
    Eyelink ('Message', sprintf('block -2 started at %.2f', GetSecs));
end
fprintf('block -2 started at %.2f \n', GetSecs-BEGIN);
results.timing.bold2start = GetSecs-BEGIN;

window1      = drawFixation(window1, dots, fix); % fixation
Screen('DrawingFinished', window1.h); % helps with managing the flip performance
         
            [flip.bold2.VBL(1, 1), ...
                flip.bold2.StimOns(1, 1), ...
                flip.bold2.FlipTS(1, 1), ...
                flip.bold2.Missed(1, 1), ...
                flip.bold2.beampos(1, 1)] = Screen('Flip', window1.h);            
                %flip.bold2.beampos(1, 1)] = Screen('Flip', window1.h, TimingCnt);
            %TimingCnt = flip.bold2.VBL(1, 1) + window1.frameDur - window1.slack;
            
WaitSecs(setup.boldbase);

if setup.Eye
    Eyelink ('Message', sprintf('block -2 ended at %.2f', GetSecs));           
end
fprintf('block -2 ended at %.2f \n', GetSecs-BEGIN);
results.timing.bold2end = GetSecs-BEGIN;

%% END OF RUN
    
ENDED = GetSecs; 
results.timing.end = ENDED; %end of experiment
    
%-------------
% End of pupil time course
%-------------
if setup.Eye
    Eyelink ('Message', sprintf('measuring ended at %.2f', GetSecs));           
end

%-------------    
% save the EL file for this run
%-------------
if setup.Eye
    %  fprintf('Receiving data file ''%s''\n', edfFile );
    mkdir('Data', ['P' num2str(setup.participant) '_'  setup.datetime]);
    eyefilename         = sprintf('P%d_s%d_r%d.edf', setup.participant, setup.session, setup.run);
    setup.eyefilename   = ['Data/P' num2str(setup.participant) '_'  setup.datetime '/' eyefilename];             
    Eyelink('command', 'generate_default_targets = YES');
    Eyelink('Command', 'set_idle_mode');
    WaitSecs(0.5);
    Eyelink('CloseFile');
    Eyelink('WaitForModeReady', 500);
    try
        status              = Eyelink('ReceiveFile', edfFile, setup.eyefilename); %this collects the file from the eyelink
        disp(status);
        disp(['File ' setup.eyefilename ' saved to disk']);
    catch
        warning(['File ' setup.eyefilename ' not saved to disk']);
    end
    % Close EyeLink
    Eyelink('StopRecording');
    % msgbox('DO NOT FORGET TO MEASURE DUMMY PUPIL!');
end

Screen('Flip', window1.h);

WaitSecs(2);

%-------------
% Exit gracefully
%-------------
disp('done!');
Screen('CloseAll'); ShowCursor;
% PsychPortAudio('Stop', audio.h);
sca;

%-------------
% Create subject specific file and save - add unique datestring to avoid any overwriting of files
%-------------
%-------------
% OUTPUT files!
%-------------
% MAT file
setup.filename = sprintf('Data/P%d_s%d_r%d_%s.mat', setup.participant, setup.session, setup.run , setup.datetime); % setup.run
save(setup.filename, '-mat', 'setup', 'window1', 'dots', 'fix', 'results', 'feedback','flip');

fclose(fid1);        
fclose(fid2);

