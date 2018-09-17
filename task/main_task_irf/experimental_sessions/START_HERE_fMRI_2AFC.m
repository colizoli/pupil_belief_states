%% Main code for RT experiment with EyeLink and feedback and arousal modulation (white noise) and fMRI
% Anne Urai, Feb 2015
% Modified by Olympia Colizoli, March 2015

% D1.01
% cd /Users/test/Documents/Olympia_0422

% Phases 
% phase 1 - baseline period ([.5,5] random)
% phase 2 - pre trial period (wait for trigger) (2 s max)
% phase 3 - stimulus on period (750 ms)
% phase 4 - stim offset -> response (2250 ms)
% phase 5 - response -> feedback ([3.5 5.5 7.5 9.5 11.5] uniform)
% phase 6 - ITI after feedback ([3.5 5.5 7.5 9.5 11.5] uniform)

% Behavioral output
% column 1 - coherence
% column 2 - hemifield (-1 left, 1 right)
% column 3 - direction (90 270)
% column 4 - response
% column 5 - correct
% column 6 - RT
% column 7 - tone (1 tone, 2 white noise)

close all; clear all; clc; dbstop if error;

%% SETUP
setup.Eye          = false;
setup.fmri         = false; % waits for pulse before signal on stage
setup.scanner      = 5;  % 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' Big Mac, 5 = O's laptop), 6 = Lab L2.19
setup.arouse       = false; % turn on arousal manipulation

setup.example      = false;
setup.debug        = true;

setup.cancel       = false;
showgraphs         = false; % generate plots

setup.localizer    = false; % work around

%-------------
% If example, don't record EyeLink data
%-------------
if setup.example
    setup.Eye    = false;
    setup.arouse = true;
    setup.fmri   = false;
end
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
[setup, dots, fix, results, sound, flip] = config_fMRI_2AFC(setup, window1, audio);
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
    Eyelink ('Message', sprintf('EyeLink configured at %d', GetSecs));  
    Eyelink('command', 'sample_rate = %d',1000);
    Eyelink('command', 'calibration_type = HV5');
    % you must send this command with value NO for custom calibration
    % you must also reset it to YES for subsequent experiments
    Eyelink('command', 'generate_default_targets = NO');
end 
%-------------
% INITIALIZE DOT COORDINATES
%-------------
stim = nan(setup.nblocks, setup.ntrials, setup.nframes, 2, dots.nDots);
block = 1;
for trial = 1 : setup.ntrials,
    %-------------
    % Preload all the dot coordinates before starting the trial
    %-------------
    stim(block, trial, :, :, :)      = dots_limitedlifetime(setup, window1, dots, block, trial);
    % block, trial, frame?, [x y]?, dots?
    
    if ~ isempty(Screen('windows')), %if there is a window1 open
        Screen('DrawText',window1.h, sprintf('Loading %d percent', ...
        round(sub2ind([setup.ntrials setup.nblocks ], trial, block)/setup.totalntrials*100)), ...
        window1.center(1), window1.center(2));
        Screen('Flip', window1.h);
    end
end % end loop over trials

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
    % GELD
outfile3 = sprintf('Data/Geld_P%d_s%d_r%d.txt',setup.participant, setup.session, setup.run); % name of output file
fid3 = fopen(outfile3,'w');

%% INSTRUCTIONS
%-------------
% Lab keys: left 'z', right 'm'
% fmri keys: left 'e' right 'b'
%-------------
keyL = 'e'; keyR = 'b';
   %keyL = 'z'; keyR = 'm';

%Screen('FillRect', window1.h, window1.black);
Screen('FillRect', window1.h, [118,118,118]);

DrawFormattedText(window1.h, ['Aan het begin van elke trial, verandert het fixatie punt van vorm. \n'...
    'Wacht tot dat het weer verandert voordat je het antwoord geeft. \n\n'...           
     'Wanneer je het goed hebt beantwoord, wordt het fixatie punt GROEN. \n' ...
     'Wanneer je het niet goed hebt beantwoord, wordt het fixatie punt ROOD. \n' ...
     'Als je te langzam bent, dan word het fixatie punt GEEL. \n\n' ...   
     'NIET VERGETEN: KIJK ALTIJD NAAR HET FIXATIE PUNT!'],  window1.center(1)-300, window1.center(2));   
Screen('Flip', window1.h);

WaitSecs(setup.TR*2);    

if setup.session > 2
    DrawFormattedText(window1.h, 'LET GOED OP!! De knopjes zijn vanaf nu omgedraaid: Links <> Rechts!!!',  window1.center(1)-300, window1.center(2));
    Screen('Flip', window1.h);
    WaitSecs(setup.TR*2);  
end

switch setup.counterbalancing
case 1 %odd participants'  % z = omhoog, m = omlaag
    DrawFormattedText(window1.h, ['Klik met je LINKER wijsvinger voor beweging OMHOOG\n \n '...
    'en met je RECHTER wijsvinger voor beweging OMLAAG.'],  window1.center(1)-300, window1.center(2));
case 0 %even participants % m = omhoog, z = omlaag
    DrawFormattedText(window1.h, ['Klik met je RECHTER wijsvinger voor beweging OMHOOG\n \n '...
    'en met je LINKER wijsvinger voor beweging OMLAAG.'],  window1.center(1)-300, window1.center(2));
end
Screen('Flip', window1.h);

%WaitSecs(setup.TR);   

%% -------------
% WAIT FOR FIRST PULSE TO START
% ---------------

if setup.fmri 
    % First pulse timing
    BEGIN = KbTriggerWait(KbName('t'));
else 
    BEGIN = GetSecs;
end

if setup.Eye
    Eyelink ('Message', sprintf('measuring started at %d', BEGIN));           
end

results.timing.start = BEGIN; %will be first pulse if in fmri mode
          
block = 1;
           
%% -------------
% BOLD BASELINE 1
%-------------
% START with an epoch of BOLD baseline
% Show only fixation cross
%-------------           
%TimingCnt = GetSecs + window1.frameDur - window1.slack;

if setup.Eye
    Eyelink ('Message', sprintf('block -1 started at %d', GetSecs));
end
fprintf('block -1 started at %d \n', GetSecs-BEGIN);
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
    Eyelink ('Message', sprintf('block -1 ended at %d', GetSecs));           
end
fprintf('block -1 ended at %d \n', GetSecs-BEGIN);
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
        Eyelink ('Message', sprintf('trial %i phase 1 started at %d trigger None', trial, GetSecs));          
    end
    fprintf('trial %i phase 1 started at %d \n', trial, GetSecs-BEGIN);
    
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
    
    %% WAIT FOR TRIGGER
    %-------------
    % PHASE 2
    % Wait for trigger before next phase
    %-------------
        
    if setup.Eye
        Eyelink ('Message', sprintf('trial %i phase 2 started at %d trigger None', trial, GetSecs));
    end
    fprintf('trial %i phase 2 started at %d \n', trial, GetSecs-BEGIN);

    %-------------
    % In fMRI mode, wait for pulse ('t') before stimulus onset starts
    % Show noise dots until pulse
    %-------------        
        %-------------
        % loop stimuli over frames
        %-------------
        for frameNum = 1:ceil(setup.TR*window1.frameRate)
                      
            window1      = dots_noise(window1, dots);
            window1      = drawFixation(window1, dots, fix); % fixation
            Screen('DrawingFinished', window1.h); % helps with managing the flip performance
            
                    [flip.trigger.VBL(frameNum, trial), ...
                        flip.trigger.StimOns(frameNum, trial), ...
                        flip.trigger.FlipTS(frameNum, trial), ...
                        flip.trigger.Missed(frameNum, trial), ...
                        flip.trigger.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);
                    TimingCnt = flip.trigger.VBL(frameNum, trial) + window1.frameDur - window1.slack;
                                
            %-------------
            % Check for t from scanner as keyboard press
            %-------------
            [keyIsDown, secs, keyCode] = KbCheck();            
            if keyIsDown,
                keypressed = KbName(keyCode);
                if ischar(keypressed) && strcmp(keypressed, 't') || ischar(keypressed) && strcmp(keypressed, 'T')
                    % only break if keypressed is a char - avoids crashes when two keys are pressed at the same time (keypressed will be a cell)
                    %-------------
                    break % exit the for loop
                    %-------------
                end % ischar & strcmp
             end % keyIsDown
        end % for

        % phase 2
        results.outputPhase(trial, 2) = flip.trigger.StimOns(1, trial);  
        
    %% STIMULUS ON (DECISION BEGINS) 
    %-------------
    % PHASE 3
    % Dot motion: coherence + noise
    % 750 ms
    % Onset is time-locked to TR for fmri mode
    %-------------     
        
    if setup.Eye
       Eyelink ('Message', sprintf('trial %i phase 3 started at %d trigger None', trial, GetSecs));          
    end
    fprintf('trial %i phase 3 started at %d \n', trial, GetSecs-BEGIN);

    %-------------
    % PRESENT STIMULUS for a fixed duration
    %-------------
     
    % fixation cross colors
    fix.color1 = black;
    fix.color2 = grey;
    %fix.flip   = 1; % flip fixation
    
    %-------------
    % Play arousal tone at signal onset
    %-------------
    if setup.arouse
        tone = sound.tones(block,trial);
        PsychPortAudio('SetLoop',audio.h, sound.tonepos(tone,1), sound.tonepos(tone,2));
    end
   
    %-------------
    % loop stimuli over frames
    %-------------       
    for frameNum = 1:setup.nframes
       %-------------
       % Draw all dots at once
       %-------------
       window1  = drawAllDots(window1, dots, block, trial, stim, frameNum);
       %-------------
       % Draw the fixation and flip
       %-------------
       if frameNum == 1 && setup.arouse
           PsychPortAudio('Start', audio.h, 1, TimingCnt); %like flip 
           if setup.Eye
                Eyelink ('Message', sprintf('sound %i at %d', tone, GetSecs));  
           end
       elseif frameNum == setup.nframes
           fix.color1 = grey;
           fix.color2 = black;
           fix.flip   = 0; % end flip
       end
            
       window1  = drawFixation(window1, dots, fix); % fixation
       Screen('DrawingFinished', window1.h); % helps with managing the flip performance           
            
            [flip.stim.VBL(frameNum, trial), ...
                flip.stim.StimOns(frameNum, trial), ...
                flip.stim.FlipTS(frameNum, trial), ...
                flip.stim.Missed(frameNum, trial), ...
                flip.stim.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.stim.VBL(frameNum, trial) + window1.frameDur - window1.slack;
            
    end % stim frames
    
    % phase 3    
    results.outputPhase(trial, 3) = flip.stim.StimOns(1, trial);
    
    %% DELAY PERIOD (stim offset, until response)        
    %-------------
    % PHASE 4
    % Dot motion: random 
    % Until a response is made
    %-------------
    
    if setup.Eye
        Eyelink ('Message', sprintf('trial %i phase 4 started at %d trigger None', trial, GetSecs));          
    end
    fprintf('trial %i phase 4 started at %d \n', trial, GetSecs-BEGIN);
    
    %-------------
    % loop stimuli over frames
    %------------- 
    logpulse = true;    
    for frameNum = 1:ceil(setup.maxRT*window1.frameRate)
        window1      = dots_noise(window1, dots);
        window1      = drawFixation(window1, dots, fix); % fixation
        Screen('DrawingFinished', window1.h); % helps with managing the flip performance
                
                [flip.waitRT.VBL(frameNum, trial), ...
                    flip.waitRT.StimOns(frameNum, trial), ...
                    flip.waitRT.FlipTS(frameNum, trial), ...
                    flip.waitRT.Missed(frameNum, trial), ...
                    flip.waitRT.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);
                TimingCnt = flip.waitRT.VBL(frameNum, trial) + window1.frameDur - window1.slack;      
    
        %-------------
        % Check for response given
        %-------------
        [keyIsDown, secs, keyCode] = KbCheck();

        if keyIsDown % either key press or pulse
            keypressed = KbName(keyCode);
            if ischar(keypressed) && ~strcmp(keypressed, 't') || ischar(keypressed) && ~strcmp(keypressed, 'T') % NOT A PULSE
                %-------------
                % Only break if NOT pulse ('t') from scanner key
                % Only break if keypressed is a char - avoids crashes when two keys are pressed at the same time (keypressed will be a cell)
                %-------------
                if setup.Eye                        
                    Eyelink ('Message', sprintf('trial %i event <EVENT(2-KeyDown {scancode:?, key: %i, unicode:ut, mod: 0})> at %d', trial, find(keyCode==1), secs));
                end
             %-------------
             % Log responses in Results
             %-------------       
                %-------------
                % Calculate RT
                %-------------
                results.RT(block, trial)    = secs - flip.stim.VBL(block,trial, 1);
                %-------------
                % Record the actual button press
                %-------------
                results.key{block, trial}   = keypressed;
                %-------------
                % Record the answer
                %-------------
                switch keypressed
                case keyL % 'z', 'e'
                    switch setup.counterbalancing
                    case 1 %odd participants
                        results.response(block, trial) = 90;
                    case 0
                        results.response(block, trial) = 270;
                    end
                case keyR % 'm', 'b'
                    switch setup.counterbalancing,
                    case 1
                        results.response(block, trial) = 270;
                    case 0
                        results.response(block, trial) = 90;
                    end
                case 'ESCAPE', % if escape is pressed, exit the experiment
                    disp('ESCAPE key pressed')
                    setup.cancel = true;
                    results.response(block, trial) = NaN;
                case 'esc', % if escape is pressed, exit the experiment
                    disp('esc key pressed')
                    setup.cancel = true;
                    results.response(block, trial) = NaN;
                otherwise % if any other key was pressed, fill in a NaN
                    disp('other key pressed')
                    results.response(block, trial) = NaN;
                end % end switch                
                %-------------
                % CODE CORRECT RESPONSE
                %-------------  
                if results.response(block, trial) == dots.direction(block,trial), % correct
                    results.correct(block,trial) = true;
                elseif isnan(results.response(block, trial)), % missed
                    results.correct(block,trial) = NaN;
                    results.RT(block,trial) = NaN; %set RT to NaN to easily filter out trials without a response
                else
                    results.correct(block,trial) = false; % incorrect
                end
                %-------------
                % Exit the loop over frames if a response is made
                break     
                %-------------                  
            else
                results.response(block, trial)  = NaN;
                results.RT(block, trial)        = NaN;
            end %ischar & strcmp
        else
            keypressed = [];
        end % keyisdown           
    end % for setup.maxRT
    
    % phase 4
    results.outputPhase(trial, 4) = flip.waitRT.StimOns(1, trial);        
                    
    %% DELAY PERIOD (after response, before feedback)   
    %-------------
    % PHASE 5
    % Dot motion: noise
    % Rebound time BEFORE feedback: setup.pupilreboundtime1 
    %-------------
    
    if setup.Eye
        Eyelink ('Message', sprintf('trial %i phase 5 started at %d trigger None', trial, GetSecs));          
    end
    fprintf('trial %i phase 5 started at %d \n', trial, GetSecs-BEGIN);

    %-------------    
    % Loop stimuli over frames
    %-------------
    for frameNum = 1:ceil(setup.pupilreboundtime1(block, trial)*window1.frameRate),
        window1      = dots_noise(window1, dots);
        window1      = drawFixation(window1, dots, fix); % fixation
        Screen('DrawingFinished', window1.h); % helps with managing the flip performance
    
            [flip.pupilrebound1.VBL(frameNum, trial), ...
                flip.pupilrebound1.StimOns(frameNum, trial), ...
                flip.pupilrebound1.FlipTS(frameNum, trial), ...
                flip.pupilrebound1.Missed(frameNum, trial), ...
                flip.pupilrebound1.beampos(frameNum, trial)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.pupilrebound1.VBL(frameNum, trial) + window1.frameDur - window1.slack;  
    end % for setup.pupilroundtime 
    
    % phase 5
    results.outputPhase(trial, 5) = flip.pupilrebound1.StimOns(1, trial);
        
    %% ITI (FEEDBACK and ITI)   
    %-------------
    % PHASE 6
    % Dot motion: noise
    % Rebound time AFTER feedback: setup.pupilreboundtime2 
    %-------------

    if setup.Eye
        Eyelink ('Message', sprintf('trial %i phase 6 started at %d trigger None', trial, GetSecs));          
    end
    fprintf('trial %i phase 6 started at %d \n', trial, GetSecs-BEGIN);
        
    %-------------
    % FEEDBACK
    %-------------
    % CORRECT
    if results.correct(block,trial) == true 
        fix.color1 = green; fix.color2 = green;
    % INCORRECT
    elseif results.correct(block,trial) == false
        fix.color1 = red; fix.color2 = red;
    % MISSED
    elseif isnan(results.correct(block,trial)), % always show!
        fix.color1 = yellow; fix.color2 = yellow;
    % No feedback
    else 
        fix.color1 = grey; fix.color2 = black;
    end % feedback                        

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
    results.outputPhase(trial, 6) = flip.pupilrebound2.StimOns(1, trial);     
    
    %-------------
    % Break out of all trials if ESC was pressed
    %-------------
    if setup.cancel
        break
        warning('experiment was manually terminated');
    end
    %-------------
    % Send EyeLink trial info
    %-------------       
    if setup.Eye
        Eyelink ('Message', sprintf('trial %i parameter coherence %d ', trial, dots.coherence(block,trial)));    WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter hemifield %d ', trial, dots.hemi));                      WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter direction %d ', trial, dots.direction(block, trial)));   WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter answer %d ', trial, results.response(block, trial)));    WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter correct %d ', trial, results.correct(block, trial)));    WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter RT %d ', trial, results.RT(block, trial)));              WaitSecs(.0005);
        Eyelink ('Message', sprintf('trial %i parameter arousal %d ', trial, sound.tones(block, trial)));        WaitSecs(.0005);          
        Eyelink ('Message', sprintf('trial %i stopped at %d trigger None ', trial, GetSecs));
    end
    % for output file
    results.output(trial, 1) = dots.coherence(block,trial);
    results.output(trial, 2) = dots.hemi;
    results.output(trial, 3) = dots.direction(block,trial);
    results.output(trial, 4) = results.response(block,trial);
    results.output(trial, 5) = results.correct(block,trial);
    results.output(trial, 6) = results.RT(block,trial);
    results.output(trial, 7) = sound.tones(block,trial);
    
    dlmwrite(outfile1,results.outputPhase-BEGIN,'\t');     
    dlmwrite(outfile2,results.output,'\t');     
        
end % END LOOP OVER TRIALS
    
%% -------------
% BOLD BASELINE 2
% -------------

if setup.Eye
    Eyelink ('Message', sprintf('block -2 started at %d', GetSecs));
end
fprintf('block -2 started at %d \n', GetSecs-BEGIN);
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
    Eyelink ('Message', sprintf('block -2 ended at %d', GetSecs));           
end
fprintf('block -2 ended at %d \n', GetSecs-BEGIN);
results.timing.bold2end = GetSecs-BEGIN;

%% END OF RUN
    
ENDED = GetSecs; 
results.timing.end = ENDED; %end of experiment
    
%-------------
% End of pupil time course
%-------------
if setup.Eye
    Eyelink ('Message', sprintf('measuring ended at %d', GetSecs));           
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
%-------------
% Break out of all trials if ESC was pressed
%-------------
if setup.cancel,
    break
    warning('experiment was manually terminated');
end

%-------------
% Calculate money on this run
%------------
G = linspace(0,10,51);
C = zeros([1 49]);
E = [C G];

PCORR = floor(nansumOly(results.correct(block,:))/setup.ntrials*100);
if PCORR == 0, PCORR = 1; end
results.geld = E(PCORR);
if isempty(results.geld)
    results.geld = 0;
end

if setup.run > 1
    try
        previous = load(sprintf('Data/Geld_P%d_s%d_r%d.txt',setup.participant, setup.session, setup.run-1));
        results.geld = mean([results.geld, previous]);
    catch error;
    end
end

geldstring = ['Klaar met run ' num2str(setup.run) '! \n \n '...
    'Je had ' num2str(nansumOly(results.correct(block,:)))  ' out of ' num2str(setup.ntrials) ' (' num2str(PCORR) '%) trials correct \n \n '...
    'Je antwoordde in gemiddeld ' num2str(nanmeanOly(results.RT(block,:))) ' seconden. \n \n '...
    'JE STAAT NU ' num2str(results.geld) ' EUROS TE VERDIENEN!!'];

DrawFormattedText(window1.h, geldstring, window1.center(1)-300, window1.center(2));
Screen('Flip', window1.h);

WaitSecs(4);

% Also show this info in the command window1
fprintf(['Finished run %d! \n \n You had %d out of %d trials correct, \n \n and your average reaction time was %.2f seconds. \n \n JE STAAT NU %d XTRA EUROS TE VERDIENEN!! '], block, nansumOly(results.correct(block,:)), setup.ntrials, nanmeanOly(results.RT(block,:)), results.geld);

%-------------
% Exit gracefully
%-------------
disp('done!');
Screen('CloseAll'); ShowCursor;
PsychPortAudio('Stop', audio.h);
sca;

%-------------
% Create subject specific file and save - add unique datestring to avoid any overwriting of files
%-------------
    if ~setup.debug
        if ~setup.example
        %-------------
        % OUTPUT files!
        %-------------
        % MAT file
        setup.filename = sprintf('Data/P%d_s%d_r%d_%s.mat', setup.participant, setup.session, setup.run , setup.datetime); % setup.run
        save(setup.filename, '-mat', 'setup', 'window1', 'stim', 'dots', 'fix', 'results', 'audio', 'sound', 'flip');
        end
    end

    fclose(fid1);        
    fclose(fid2);
    % GELD
    dlmwrite(outfile3,results.geld,'\t');     
    fclose(fid3);

%% Graphs

if showgraphs
    showFlipGraphs(setup, results, flip);
end % showgraphs
