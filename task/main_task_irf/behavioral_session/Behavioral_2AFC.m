%% Main code for RT experiment with EyeLink and feedback and arousal modulation (white noise)
% Anne Urai, Feb 2015
% Modified by Olympia Colizoli, March 2015

% D1.01
% cd /Users/test/Documents/Olympia_0422

% Behavioral phases
% phase 1 - baseline period
% (phase 2 only in fMRI version)
% phase 3 - decision period (750 ms)
% phase 4 - stim offset -> response
% phase 5 - response -> feedback
% phase 6 - ITI after feedback

% Behavioral output
% column 1 - coherence
% column 2 - hemifield
% column 3 - direction
% column 4 - response
% column 5 - correct
% column 6 - RT
% column 7 - tone

% https://github.com/neurodebian/psychtoolbox-3-old-gitsvn-based/blob/master/Psychtoolbox/PsychDocumentation/Psychtoolbox3-Slides.pdf

close all; clear all; clc; dbstop if error;

%% SETUP

setup.scanner      = 6;  % 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' Big Mac, 5 = O's laptop, 6 = lab 2.19)
setup.Eye          = false;
setup.feedback     = true;
setup.arouse       = true; % turn on sound noise
setup.fmri         = false; % switches keys at scanner

setup.debug        = false;
setup.example      = false;

setup.localizer    = false; % for EyeLink EDF file names

setup.startatblock = 1;
setup.cancel       = false;
showgraphs         = false; % generate plots
%setup.deviant      = false; % if false, white noise. If true, deviant version

%-------------
% If example, don't record EyeLink data
%-------------
if setup.example
    setup.Eye = false;
    setup.arouse = false;
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
% Ask for run number, default = 0
%-------------
setup.run               = input('Run? ');
if isempty(setup.run)
    setup.run           = 0;
end

%-------------
% window1 settings
%-------------
window1 = define_window(setup);

window1.skipChecks      = 1;
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
Screen('TextColor', window1.h, [255 255 255] );
Screen('DrawText', window1.h, 'Loading...', window1.center(1), window1.center(2));
Screen('Flip', window1.h);
%-------------
% INITIALIZE EXPERIMENTAL PARAMETERS
%-------------
[setup, dots, fix, results, sound, flip] = config_Behavioral_2AFC(setup, window1, audio);
%-------------
% fixation cross colors for feedback
%-------------
white   = [255,255,255];
red     = [255,0,0];
green   = [0,255,0];
yellow  = [255,246,0];
% black   = [0 0 0];
% grey    = [118 118 118];
%Names only are flipped here!
grey   = [0 0 0];
black    = [118 118 118];

color   = white; %fixation cross white
%-------------
% Initialize EyeLink
%-------------
if setup.Eye == true,
    edfFile = ELconfig(window1, setup, setup.run);
    Eyelink ('Message', sprintf('EyeLink configured at %d', GetSecs));           
end 
%-------------
% INITIALIZE DOT COORDINATES
%-------------
stim = nan(setup.nblocks, setup.ntrials, setup.nframes, 2, dots.nDots);
for block = setup.startatblock : setup.nblocks,
    for trial = 1 : setup.ntrials,
        %-------------
        % Preload all the dot coordinates before starting the trial
        %-------------
        stim(block, trial, :, :, :)      = dots_limitedlifetime(setup, window1, dots, block, trial);
        
        if ~ isempty(Screen('windows')), %if there is a window1 open
            Screen('DrawText',window1.h, sprintf('Loading %d percent', ...
                round(sub2ind([setup.ntrials setup.nblocks ], trial, block)/setup.totalntrials*100)), ...
                window1.center(1), window1.center(2));
            Screen('Flip', window1.h);
        end
    end % end loop over trials
end % end loop over blocks

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
outfile3 = sprintf('Data/GeldB_P%d_s%d_r%d.txt',setup.participant, setup.session, setup.run); % name of output file
fid3 = fopen(outfile3,'w');

%% INSTRUCTIONS
%-------------
% Lab keys: left 'z', right 'm'
% fmri keys: left 'e' right 'b'
%-------------
if setup.fmri
    keyL = 'e'; keyR = 'b';
else
    keyL = 'z'; keyR = 'm';
end

% TRIGGER DISABLED FOR RUNNING DURING SCANNING!
DisableKeysForKbCheck('t'); 
%--------------------------

%Screen('FillRect', window1.h, window1.black);
Screen('FillRect', window1.h, [118 118 118]);

if setup.feedback
    DrawFormattedText(window1.h, ['Aan het begin van elke trial, verandert het fixatie punt van vorm. \n'...
        'Wacht tot dat het weer verandert voordat je het antwoord geeft. \n\n'...           
         'Wanneer je het goed hebt beantwoord, wordt het fixatie punt GROEN. \n' ...
         'Wanneer je het niet goed hebt beantwoord, wordt het fixatie punt ROOD. \n' ...
         'Als je te langzam bent, dan word het fixatie punt GEEL. \n\n' ...   
         'NIET VERGETEN: KIJK ALTIJD NAAR HET FIXATIE PUNT!'],  window1.center(1)-300, window1.center(2));   
    Screen('Flip', window1.h);
else
    DrawFormattedText(window1.h, ['Aan het begin van elke trial, verandert het fixatie punt van vorm (in plaats van een piepje)! \n \n '...
        'Let dus goed op! Je zal geen pieptonen meer horen. \n\n Verder, stopt de beweging niet meer! \n\n' ...
        'Wacht tot dat het weer verandert voor je het antwoord geeft. \n\n' ...   
        'Als je te langzam bent, dan word het fixatie punt GEEL. \n \n' ...
        'NIET VERGETEN: KIJK ALTIJD NAAR HET FIXATIE PUNT!' ],  'center', 'center');    
    Screen('Flip', window1.h);
end

WaitSecs(.1); KbWait(); WaitSecs(.1); 

if setup.session > 2
    DrawFormattedText(window1.h, 'LET GOED OP!! De knopjes zijn vanaf nu omgedraaid: Links <> Rechts!!!',  window1.center(1)-300, window1.center(2));
    Screen('Flip', window1.h);
    WaitSecs(.1); KbWait(); WaitSecs(.1); 
end

switch setup.counterbalancing
    case 1 %odd participants'  % z = omhoog, m = omlaag
        DrawFormattedText(window1.h, ['Klik met jouw LINKER wijsvinger voor beweging OMHOOG\n \n '...
        'en met je RECHTER wijsvinger voor beweging OMLAAG.'],  'center', 'center');
    case 0 %even participants % m = omhoog, z = omlaag
         DrawFormattedText(window1.h, ['Klik met jouw RECHTER wijsvinger voor beweging OMHOOG\n \n '...
        'en met je LINKER wijsvinger voor beweging OMLAAG.'],  'center', 'center');
end
Screen('Flip', window1.h);

WaitSecs(.1); KbWait(); WaitSecs(.5);

BEGIN  = GetSecs;

%% LOOP OVER BLOCKS
for block = setup.startatblock : setup.nblocks,
    %-------------
    % Initialize EyeLink (if more than one block)
    %-------------
    if setup.Eye
        if block > 1
            edfFile = ELconfig(window1, setup, block);
        end
        % beginning of pupil time course
        Eyelink ('Message', sprintf('measuring started at %d', GetSecs));           
        %WaitSecs(2);
    end 
    
    %% LOOP OVER TRIALS
    for trial = 1 : setup.ntrials
     %-------------
     % BASELINE STAGE BEGINS
     % PHASE 1
     %-------------        
        if setup.Eye 
            Eyelink ('Message', sprintf('trial %i phase 1 started at %d trigger None', trial, GetSecs));
        end
        fprintf('trial %i phase 1 started at %d \n', trial, GetSecs-BEGIN);
        
        if trial == 1
            TimingCnt = GetSecs + window1.frameDur - window1.slack;
        else 
            TimingCnt = flip.pupilrebound2.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
        end
        
        for frameNum = 1:ceil(setup.fixtime(block, trial)*window1.frameRate),
            window1      = dots_noise(window1, dots);
            window1      = drawFixation(window1, dots, fix); % fixation
            Screen('DrawingFinished', window1.h); % helps with managing the flip performance
            
            [flip.fix.VBL(block, trial, frameNum), ...
                flip.fix.StimOns(block, trial, frameNum), ...
                flip.fix.FlipTS(block, trial, frameNum), ...
                flip.fix.Missed(block, trial, frameNum), ...
                flip.fix.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.fix.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;

        end % frames
        
        % phase 1
        results.outputPhase(trial, 1) = flip.fix.StimOns(block, trial, 1);  
     %-------------
     % PHASE 2
     % WAIT FOR TRIGGER ONLY IN fMRI VERSION!
     %-------------       
        % phase 2
        results.outputPhase(trial, 2) = NaN;  
        
     %% DECISION STAGE BEGINS 
     %-------------
     % PHASE 3
     % Dot motion: coherence + noise
     % 750 ms
     %-------------     
     
        if setup.Eye
           Eyelink ('Message', sprintf('trial %i phase 3 started at %d trigger None', trial, GetSecs));          
        end
        fprintf('trial %i phase 3 started at %d \n', trial, GetSecs-BEGIN);

        %-------------
        % PRESENT STIMULUS for a fixed duration or until RT
        %-------------
        TimingCnt = flip.fix.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
        
        fix.color1 = black;
        fix.color2 = grey;
%         fix.flip   = 1; % flip fixation
        
        %-------------
        % Play arousal tone at signal onset
        %-------------
        if setup.arouse
            tone = sound.tones(block,trial);
            PsychPortAudio('SetLoop',audio.h, sound.tonepos(tone,1), sound.tonepos(tone,2));
        end
   
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
            
            [flip.stim.VBL(block, trial, frameNum), ...
                flip.stim.StimOns(block, trial, frameNum), ...
                flip.stim.FlipTS(block, trial, frameNum), ...
                flip.stim.Missed(block, trial, frameNum), ...
                flip.stim.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.stim.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
        end % stim frames
        
        % phase 3
        results.outputPhase(trial, 3) = flip.stim.StimOns(block, trial, 1);  
        
    %% DELAY PERIOD (stim offset - before response)        
     %-------------
     % PHASE 4
     % random dot motion until a response is made
     %-------------
        
        if setup.Eye
            Eyelink ('Message', sprintf('trial %i phase 4 started at %d trigger None', trial, GetSecs));          
        end
        fprintf('trial %i phase 4 started at %d \n', trial, GetSecs-BEGIN);

        TimingCnt = flip.stim.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
    
        for frameNum = 1:ceil(setup.maxRT*window1.frameRate)
                window1      = dots_noise(window1, dots);
                window1      = drawFixation(window1, dots, fix); % fixation
                Screen('DrawingFinished', window1.h); % helps with managing the flip performance
                
                [flip.waitRT.VBL(block, trial, frameNum), ...
                    flip.waitRT.StimOns(block, trial, frameNum), ...
                    flip.waitRT.FlipTS(block, trial, frameNum), ...
                    flip.waitRT.Missed(block, trial, frameNum), ...
                    flip.waitRT.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
                TimingCnt = flip.waitRT.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;      
    
                %-------------
                % Check for response given
                %-------------
                [keyIsDown, secs, keyCode] = KbCheck();

                if keyIsDown %&& isnan(results.RT(block,trial)) % if they did not already respond during the stimulus
                    keypressed = KbName(keyCode);
                    if ischar(keypressed)
                        %-------------
                        % Only break if keypressed is a char - avoids crashes when two keys are pressed at the same time (keypressed will be a cell)
                        %-------------
                        if setup.Eye                        
                            Eyelink ('Message', sprintf('trial %i event <EVENT(2-KeyDown {scancode:?, key: %i, unicode:ut, mod: 0})> at %d', trial, find(keyCode==1), secs));
                        end
                        %-------------
                        % Log responses in Results
                        %-------------       
                            if ~isempty(keypressed) 
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

                            else %if keypressed is empty, the maximum response time was reached and no response recorded
                                results.response(block, trial) = NaN;
                                results.RT(block, trial)    = NaN;
                            end % if keypressed & not pulse
                        %-------------
                        % CODE CORRECT RESPONSE
                        %-------------  
                        if results.response(block, trial) == dots.direction(block,trial), % correct
                            results.correct(block,trial) = true;
                        elseif isnan(results.response(block, trial)), % missed
                            results.correct(block,trial) = NaN;
                            results.RT(block,trial) = NaN; %set RT to NaN to easily filter out trials without a response
                        else
                            results.correct(block,trial) = false; % wrong trial
                        end
                        %-------------
                        % Exit the loop over frames if a response is made
                        %-------------  
                        break                              
                    elseif ischar(keypressed) && strcmp(keypressed, 't'), 
                        %-------------
                        % log pulse timing
                        %-------------
                        pressedCodes                                        = find(keyCode == 1);
                        results.pulsecount                                  = results.pulsecount + 1;
                        results.scannerpulses.key(results.pulsecount)       = KbName(pressedCodes);
                        results.scannerpulses.trialtime(results.pulsecount) = secs - BEGIN;
                        results.scannerpulses.seconds(results.pulsecount)   = secs;
                        if setup.Eye                        
                            Eyelink ('Message', sprintf('trial %i event <EVENT(2-KeyDown {scancode:17, key: 116, unicode:ut, mod: 0})> at %d', trial, results.scannerpulses.seconds(results.pulsecount)));
                        end
                    end %ischar & strcmp
                elseif ~isnan(results.RT(block,trial))
                    % already responded, so break loop
                    % disp('breaking at frame '); disp(frameNum);
                    break
                else
                    keypressed = [];
                end % keyisdown           
        end % for setup.maxRT
        
        % phase 4
        results.outputPhase(trial, 4) = flip.waitRT.StimOns(block, trial, 1);    
       
    %% DELAY PERIOD (before feedback)  
    % Rebound time BEFORE feedback: setup.pupilreboundtime 
    % Rebound time AFTER feedback: setup.pupilreboundtime2
    %-------------
    % PHASE 5
    % Dot motion: noise
    % Rebound time BEFORE feedback: setup.pupilreboundtime
    %-------------
    
        if setup.Eye
            Eyelink ('Message', sprintf('trial %i phase 5 started at %d trigger None', trial, GetSecs));          
        end
        fprintf('trial %i phase 5 started at %d \n', trial, GetSecs-BEGIN);

        TimingCnt = flip.waitRT.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
        %-------------    
        % Wait for the pupil to return to baseline AFTER decision and BEFORE feedback
        %-------------
        for frameNum = 1:ceil(setup.pupilreboundtime(block, trial)*window1.frameRate),
            window1      = dots_noise(window1, dots);
            window1      = drawFixation(window1, dots, fix); % fixation
            Screen('DrawingFinished', window1.h); % helps with managing the flip performance
    
            [flip.pupilrebound1.VBL(block, trial, frameNum), ...
                flip.pupilrebound1.StimOns(block, trial, frameNum), ...
                flip.pupilrebound1.FlipTS(block, trial, frameNum), ...
                flip.pupilrebound1.Missed(block, trial, frameNum), ...
                flip.pupilrebound1.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.pupilrebound1.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;  

        end % for setup.pupilroundtime 
        
        % phase 5
        results.outputPhase(trial, 5) = flip.pupilrebound1.StimOns(block, trial, 1);    
        
        
        %% ITI (including and after feedback)   
        %-------------
        % PHASE 6
        % Dot motion: noise
        % Rebound time AFTER feedback: setup.pupilreboundtime2
        %-------------
        %-------------
        % Present feedback if setup.feedback
        %-------------
            %-------------
            % Correct
            %-------------
            if results.correct(block,trial) == true && setup.feedback, 
                fix.color1 = green; fix.color2 = green;
            %-------------
            % Incorrect
            %-------------
            elseif results.correct(block,trial) == false && setup.feedback, 
                fix.color1 = red; fix.color2 = red;
            %-------------
            % Missed
            %-------------                        
            elseif isnan(results.correct(block,trial)), % always show!
                fix.color1 = yellow; fix.color2 = yellow;
            %-------------
            % No feedback
            %-------------    
            else 
                fix.color1 = grey; fix.color2 = black;
            end % feedback                        

        if setup.Eye
            Eyelink ('Message', sprintf('trial %i phase 6 started at %d trigger None', trial, GetSecs));          
        end
        fprintf('trial %i phase 6 started at %d \n', trial, GetSecs-BEGIN);

        %-------------
        % Waits for the pupil to return to baseline AFTER feedback (equal to the ITI)
        %-------------
        TimingCnt = flip.pupilrebound1.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;  

        for frameNum = 1:ceil(setup.pupilreboundtime2(block, trial)*window1.frameRate),       
            window1      = dots_noise(window1, dots);
            if frameNum > 21
                fix.color1 = grey; fix.color2 = black;
            end
            window1      = drawFixation(window1, dots, fix); % fixation
            Screen('DrawingFinished', window1.h); % helps with managing the flip performance

            [flip.pupilrebound2.VBL(block, trial, frameNum), ...
                flip.pupilrebound2.StimOns(block, trial, frameNum), ...
                flip.pupilrebound2.FlipTS(block, trial, frameNum), ...
                flip.pupilrebound2.Missed(block, trial, frameNum), ...
                flip.pupilrebound2.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.pupilrebound2.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
        end % for setup.pupilreboundtime2

        %-------------
        % Trial end time
        %-------------
        % phase 6
        results.outputPhase(trial, 6) = flip.pupilrebound2.StimOns(block, trial, 1);  
        
        trialend = GetSecs;
        fprintf('trial %i ended at %d \n', trial, trialend-BEGIN);
        %-------------
        % Break out of all trials if ESC was pressed
        %-------------
        if setup.cancel,
            break
            warning('experiment was manually terminated');
        end
        %-------------
        % Send EyeLink trial info
        %-------------       
         if setup.Eye
           Eyelink ('Message', sprintf('trial %i parameter coherence %d ', trial, dots.coherence(block, trial)));   WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter hemifield %d ', trial, dots.hemi));                      WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter direction %d ', trial, dots.direction(block, trial)));   WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter answer %d ', trial, results.response(block, trial)));    WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter correct %d ', trial, results.correct(block, trial)));    WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter RT %d ', trial, results.RT(block, trial)));              WaitSecs(.0005);
           Eyelink ('Message', sprintf('trial %i parameter arousal %d ', trial, sound.tones(block, trial)));        WaitSecs(.0005);         
           Eyelink ('Message', sprintf('trial %i stopped at %d trigger None ', trial, trialend));
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
    
    ENDED = GetSecs; % block
    
    %-------------
    % Log Timing
    %-------------   
    results.timing(block, 1) = BEGIN;
    results.timing(block, 2) = ENDED; 
        
    %-------------
    % End of pupil time course
    %-------------
    if setup.Eye
        Eyelink ('Message', sprintf('measuring ended at %d', GetSecs));           
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
            previous = load(sprintf('Data/GeldB_P%d_s%d_r%d.txt',setup.participant, setup.session, setup.run-1));
            results.geld = mean([results.geld, previous]);
        catch error;
        end
    end

    geldstring = ['Klaar met run ' num2str(setup.run) '! \n \n '...
        'Je had ' num2str(nansumOly(results.correct(block,:)))  ' out of ' num2str(setup.ntrials) ' (' num2str(PCORR) '%) trials correct \n \n '...
        'Je antwoordde in gemiddeld ' num2str(nanmeanOly(results.RT(block,:))) ' seconden. \n \n '...
        'JE STAAT NU ' num2str(results.geld) ' EUROS TE VERDIENEN!!'];

    DrawFormattedText(window1.h, geldstring, window1.center(1), window1.center(2));
    Screen('Flip', window1.h);

    WaitSecs(4);

    % Also show this info in the command window1
    fprintf(['Finished run %d! \n \n You had %d out of %d trials correct, \n \n and your average reaction time was %.2f seconds. \n \n JE STAAT NU %d XTRA EUROS TE VERDIENEN!! '], block, nansumOly(results.correct(block,:)), setup.ntrials, nanmeanOly(results.RT(block,:)), results.geld);


    %-------------    
    % save the EL file for this block
    %-------------
    if setup.Eye == true,
        %  fprintf('Receiving data file ''%s''\n', edfFile );
        mkdir('Data', ['P' num2str(setup.participant) '_'  setup.datetime]);
        eyefilename = sprintf('P%d_s%d_r%d.edf', setup.participant, setup.session, setup.run);
        setup.eyefilename = ['Data/P' num2str(setup.participant) '_'  setup.datetime '/' eyefilename];      
        
        Eyelink('CloseFile');
        Eyelink('WaitForModeReady', 500);
        try
            status              = Eyelink('ReceiveFile', edfFile, setup.eyefilename); %this collects the file from the eyelink
            disp(status);
            disp(['File ' setup.eyefilename ' saved to disk']);
        catch
            warning(['File ' setup.eyefilename ' not saved to disk']);
        end
    end
    %-------------
    % Break out of all trials if ESC was pressed
    %-------------
    if setup.cancel,
        break
        warning('experiment was manually terminated');
    end

    %-------------
    % !! Important, make sure all the variables of interest are saved to
    % possibly recreate the exact experiment later.
    %-------------
    
    %-------------
    % OUTPUT files!
    %-------------
    % MAT file
    if ~setup.example
        setup.filename = sprintf('Data/P%d_s%d_r%d_b%d_%s.mat', setup.participant, setup.session, setup.run, block , setup.datetime); % setup.run
        save(setup.filename, '-mat', 'setup', 'window1', 'stim', 'dots', 'fix', 'results', 'audio', 'sound', 'flip');
    end
    
    fclose(fid1);        
    fclose(fid2);
    dlmwrite(outfile3,results.geld,'\t');     
    fclose(fid3);
    
end % END LOOP OVER BLOCKS

%-------------
% Exit gracefully
%-------------
disp('done!');
Screen('CloseAll'); ShowCursor;
PsychPortAudio('Stop', audio.h);
sca;

%-------------
% Close the eyelink
%-------------
if setup.Eye == true,
    Eyelink('StopRecording');
    Eyelink('CloseFile');
    % msgbox('DO NOT FORGET TO MEASURE DUMMY PUPIL!');
end

%% Graphs

if showgraphs
    showFlipGraphs(setup, results, flip);
end % showgraphs
