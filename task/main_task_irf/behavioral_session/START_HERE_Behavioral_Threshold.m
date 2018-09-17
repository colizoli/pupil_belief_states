%% Code to determine a subject's threshold before starting the real training
% Anne Urai, Feb 2015
% Olympia Colizoli, May 2015
% -----------------------------------------------------------------

clear all; close all; clc;

setup.scanner          = 6; % 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' Big Mac, 5 = O's laptop, 6 = lab 2.19)
setup.Eye              = false;
setup.feedback         = true;
setup.debug            = false;
setup.startAtBlock     = 1;

% work arounds (should leave false)
setup.fmri             = false;
setup.localizer        = false;

% general setup
% ask for subject number, default: 0
setup.participant       = input('Participant number? ');
if isempty(setup.participant)
    setup.participant   = 100; %test
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


% present loading text on the screen
Screen('TextSize', window1.h, 15);
Screen('TextFont', window1.h, 'Trebuchet');
Screen('TextColor', window1.h, [255 255 255] );
Screen('DrawText', window1.h, 'Loading...', window1.center(1)*0.60, window1.center(2)*0.75);
Screen('Flip', window1.h);

% fixation cross colors for feedback
white   = [255,255,255];
red     = [255,0,0];
green   = [0,255,0];
yellow  = [255,246,0];
% black   = [0 0 0];
% grey    = [118 118 118];
% switch grey/black names only!
grey   = [0 0 0];
black    = [118 118 118];
color   = white; %fixation cross white

%% Initialize setup
% the function configuration contains all the important experimental
% design parameters

if setup.startAtBlock > 1
    load(sprintf('Data/P%d_thresholdMOCS_Backup.mat',setup.participant));
else
    [setup, dots, fix, results, flip, sound] = config_Behavioral_Threshold(window1, setup, audio);        
    % preload all the dot coordinates
    stim = nan(setup.nblocks, setup.ntrials, setup.nframes, 2, dots.nDots);
    % only one
    for block = 1:setup.nblocks,
            dots.hemi = -1*dots.hemi;
        for trial = 1:setup.ntrials,
            % preload all the dot coordinates before starting the trial
            stim(block, trial, :, :, :)      = dots_limitedlifetime(setup, window1, dots, block, trial, '');
            Screen('DrawText',window1.h, sprintf('Loading %.1f percent', round(sub2ind([setup.ntrials setup.nblocks ], trial, block)/setup.totalntrials*100)), window1.center(1)*0.60, window1.center(2)*0.75 , [255 255 255] );
            Screen('Flip', window1.h);
        end
    end
end

% lab keys: left 'z', right 'm'
% fmri keys: left 'e' right 'b'

if setup.fmri
   keyL = 'e'; keyR = 'b';
else
   keyL = 'z'; keyR = 'm';
end

for block = setup.startAtBlock:setup.nblocks
    
    dots.hemi = -1*dots.hemi;
    
    %Screen('FillRect', window1.h, window1.black);
    Screen('FillRect', window1.h, [118 118 118]);
        
    switch setup.counterbalancing
         case 1 %odd participants'  % z = omhoog, m = omlaag
            DrawFormattedText(window1.h, ['Klik met jouw LINKER wijsvinger voor beweging OMHOOG\n \n '...
                'en met je RECHTER wijsvinger voor beweging OMLAAG.'],  'center', 'center');
        case 0 %even participants % m = omhoog, z = omlaag
            DrawFormattedText(window1.h, ['Klik met jouw RECHTER wijsvinger voor beweging OMHOOG\n \n '...
                'en met je LINKER wijsvinger voor beweging OMLAAG.'],  'center', 'center');
    end
    Screen('Flip', window1.h);

    KbWait(); %after windowing the introductory text, wait for a keypress
    WaitSecs(.3); 

    DrawFormattedText(window1.h, ['Kijk ALTIJD naar het fixatie punt! \n \n '...
        'Geef pas antwoord nadat het fixatie punt weer verandert is! \n\n' ...
        'Klik om te beginnen.' ],  'center', 'center');
    Screen('Flip', window1.h);
    
    KbWait(); %after windowing the introductory text, wait for a keypress
    WaitSecs(.3);
    
    %% start the loop over trials
    for trial = 1:setup.ntrials
                
        if trial == 1
            TimingCnt = GetSecs + window1.frameDur - window1.slack;
            fix.feedback1          = grey; % outside 
            fix.feedback2          = black; % inside
        end
        
        % variable fixation interval before stim onset        
        for frameNum = 1:ceil(setup.fixtime(block, trial)*window1.frameRate)
            window1      = dots_noise(window1, dots);
            
            if frameNum > 30 && frameNum < 60% 830 ms at 60 Hz
                fix.color1 = fix.feedback1; fix.color2 = fix.feedback2; % show feedback color!
            elseif frameNum > 60
                fix.color1 = grey; fix.color2 = black; % take off color feedback
            end
            window1      = drawFixation(window1, dots, fix); % fixation
            
            [flip.fix.VBL(block, trial, frameNum), ...
                flip.fix.StimOns(block, trial, frameNum), ...
                flip.fix.FlipTS(block, trial, frameNum), ...
                flip.fix.Missed(block, trial, frameNum), ...
                flip.fix.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.fix.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
            
            if setup.Eye && frameNum == 1,
                Eyelink ('Message', sprintf('block%d_trial%d_fix', block, trial));
            elseif ~setup.Eye && frameNum == 1,
                fprintf('block%d_trial%d_fix \n', block, trial);
            end
        end
        
        % play reference stimulus onset tone
        PsychPortAudio('SetLoop',audio.h, sound.tonepos(1,1), sound.tonepos(1,2));

        fix.color1          = black; % outside 
        fix.color2          = grey; % inside
        
        % PRESENT STIMULUS for a fixed duration
        for frameNum = 1:setup.nframes            
            %Draw all dots at once
            window1  = drawAllDots(window1, dots, block, trial, stim, frameNum);
            %Draw the fixation and Flip           
            window1      = drawFixation(window1, dots, fix); % fixation
            Screen('DrawingFinished', window1.h);
            
            if frameNum == 1         % play reference stimulus onset tone
                PsychPortAudio('Start', audio.h, 1, TimingCnt); %like flip
            end
            
            [flip.stim.VBL(block, trial, frameNum), ...
                flip.stim.StimOns(block, trial, frameNum), ...
                flip.stim.FlipTS(block, trial, frameNum), ...
                flip.stim.Missed(block, trial, frameNum), ...
                flip.stim.beampos(block, trial, frameNum)] = Screen('Flip', window1.h, TimingCnt);
            TimingCnt = flip.stim.VBL(block, trial, frameNum) + window1.frameDur - window1.slack;
            
            if setup.Eye && frameNum == 1
                Eyelink ('Message', sprintf('\n block%d_trial%d_stim_dir%d \n', block, trial, dots.direction(block, trial)));
            end
        end % frames
        
        fix.color1          = grey; % outside 
        fix.color2          = black; % inside
        
        % play reference stimulus offset tone
        %PsychPortAudio('SetLoop',audio.h, sound.tonepos(1,1), sound.tonepos(1,2));
        %PsychPortAudio('Start', audio.h); %like flip
        
        %% collect response
            
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
                     
            % while GetSecs-flip.stim.VBL(block,trial,frameNum) < setup.resptime && isnan(results.response(block, trial)),
            % when no response has been given, and the maximum
            % response time hasnt been reached
            [keyIsDown, secs, keyCode]  = KbCheck();
            keypressed = KbName(keyCode);
            
            if keyIsDown %&& ~strcmp(keypressed(1), 't'), % to prevent pulses from logging as decisions
                try
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
                            setup.cancel = true;
                            results.response(block, trial) = NaN;
                        case 'esc', % if escape is pressed, exit the experiment
                            setup.cancel = true;
                            results.response(block, trial) = NaN;
                        otherwise % if any other key was pressed, fill in a NaN
                            results.response(block, trial) = NaN;
                    end
                catch % in case it doesnt understand the input. for example when two keys are pressed at the same time
                    results.response(block, trial) = NaN;
                end
                
                % calculate reaction time (even if no button was pressed)
                results.key{block, trial}   = KbName(keyCode);
                results.RT(block, trial)    = secs - flip.stim.VBL(block,trial,1); %from the FIRST frame, stim onset
               
                %-------------
                % FEEDBACK
                %-------------
                % code for correct responses
                % this bit of the code needs to be edited so that the
                % correct flag is applied when response matches stimulus
                % (eg. up down)
                if results.response(block, trial) == dots.direction(block,trial) %whether motion is stronger than 50% or not
                    results.correct(block,trial) = true;  % CORRECT          
                    fix.feedback1 = green; fix.feedback2 = green;
                    %PsychPortAudio('SetLoop',audio.h, sound.tonepos(2,1), sound.tonepos(2,2));
                    %PsychPortAudio('Start', audio.h);               
                elseif isnan(results.response(block, trial)) % Wrong key or two keys!
                    results.correct(block,trial) = NaN;                       
                    results.RT(block,trial) = NaN; %set RT to NaN to easily filter out trials without a response
                    fix.feedback1 = yellow; fix.feedback2 = yellow;                        
                    %PsychPortAudio('SetLoop',audio.h, sound.tonepos(4,1), sound.tonepos(4,2));
                    %PsychPortAudio('Start', audio.h);     
                else   
                    results.correct(block,trial) = false; % INCORRECT
                    fix.feedback1 = red; fix.feedback2 = red;                     
                    %PsychPortAudio('SetLoop',audio.h, sound.tonepos(3,1), sound.tonepos(3,2));
                    %PsychPortAudio('Start', audio.h);                                                                                   
                end
                
                if setup.Eye,
                    Eyelink ('Message', sprintf('\n block%d_trial%d_resp%d_correct%d_RT%.3f \n', block, trial, results.response(block, trial), results.correct(block, trial), results.RT(block, trial)));
                elseif ~setup.Eye,
                    fprintf('\n block%d_trial%d_resp%d_correct%d_RT%.3f \n', block, trial, results.response(block, trial), results.correct(block, trial), results.RT(block, trial));
                end
                                
                % BREAK OUT OF NOISE LOOP IS RESPONSE IS MADE
                break
            else % MISSED TRIAL
                results.response(block, trial) = NaN; %if no key was pressed, NaN
            end % key is down
        end %frame number
        
        if isnan(results.response(block, trial)) % MISSED TRIAL 
            results.RT(block,trial) = NaN; %set RT to NaN to easily filter out trials without a response
            fix.feedback1 = yellow; fix.feedback2 = yellow;   
            PsychPortAudio('SetLoop',audio.h, sound.tonepos(4,1), sound.tonepos(4,2));
            PsychPortAudio('Start', audio.h);               
        end
        
        % break out of all trials if ESC was pressed
        if setup.cancel,
            break
            warning('experiment was manually terminated');
        end
        
    end %end trial loop
    
    %% break text
    WaitSecs(1);

    Screen('DrawText',window1.h, sprintf('Klaar met blok %d van de %d!', block, setup.nblocks) , ...
        window1.center(1), window1.center(2)*0.40 , [255 255 255] );
    
    if block < setup.nblocks,
        Screen('DrawText',window1.h, 'Neem even pauze, en klik om verder te gaan.', window1.center(1), window1.center(2));
    else % finish
        Screen('DrawText',window1.h, 'Roep de proefleider.', window1.center(1), window1.center(2));
    end
    
    Screen('Flip', window1.h);
    KbWait();     WaitSecs(.3);

     % present some useful into to the experimenter
    fprintf('\n !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n');
    fprintf('\n Finished block %d out of %d! \n', block, setup.nblocks)
    % compute the overall binary accuracy
    fprintf('\n Binary choice accuracy = %.2f percent \n \n', 100*nanmean(results.correct(block, :)));
    fprintf('\n Binary choice RT = %.2f s \n \n', nanmean(results.RT(block, :)));
    fprintf('\n !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! \n');
    
    % save config in case of errors
    % create subject specific file and save - add unique datestring to avoid any overwriting of files
    setup.filename = sprintf('Data/P%d_thresholdMOCS_Backup.mat', setup.participant);
    save(setup.filename, '-mat', 'setup', 'window1', 'stim', 'dots', 'fix', 'results', 'flip');
    
    % break out of all 1s if ESC was pressed
    if setup.cancel == true,
        warning('experiment was manually terminated');
        break
    end
end %block

% wrap up and save
setup.datetime = datestr(now, 'yyyy-mm-dd_HH-MM-SS');
% create subject specific file and save - add unique datestring to avoid any overwriting of files
setup.filename = sprintf('Data/P%d_thresholdMOCS_%s.mat', setup.participant, setup.datetime);
save(setup.filename, '-mat', 'setup', 'window1', 'stim', 'dots', 'fix', 'results', 'flip');

% !! important, make sure all the variables of interest are saved to
% possibly recreate the exact experiment later.

% exit gracefully
disp('done!');
Screen('CloseAll'); ShowCursor;
PsychPortAudio('Stop', audio.h);
sca;

% take all results and plot the full psychometric extravaganza
[datapoints1, datapoints2, datapoints3, fit1, fit2, fit3] = FitThreshold(setup.filename, 'fit', 'bootstrap');

save(sprintf('Data/P%d_threshold.mat', setup.participant), 'fit1');