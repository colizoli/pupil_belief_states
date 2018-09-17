 
%% Measure Individual IRF
% To measure the individual impulse response functions of the pupil
% during short audio tones 
% Timing of tones is drawn randomly from a uniform distribution:
% [setup.lower, setup.upper]

% Measure Dummy Pupil Script by Anne Urai, March 2014 
% Adapted by Olympia Colizoli, May 2015
% ----------------------------------------------------------------

clear all; close all; clc;

setup.scanner       = 1;  % 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' bebegBig Mac, 5 = O's laptop, 6 = lab 2.19)

% general setup
setup.Eye           = true; % true if using Eyelink
setup.nbeeps        = 25; % number of trials/tones PER BLOCK
setup.nblocks       = 1; % number of blocks
setup.whitenoise    = true; % white noise or tone if false
setup.lower         = 2; % lower limit for duration in secs
setup.upper         = 6; % upper limit for duration in secs

% work arounds
setup.fmri          = false;
setup.localizer     = 3; % for ELconfig EDF name

setup.debug         = false;

setup.beeps         = NaN(setup.nblocks, setup.nbeeps);
%-------------
% Ask for subject number, default: 0
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

% Setup the PsychToolbox
window1.skipChecks      = 1; % set to 1 to skip VBL tests and avoid warnings
[window1, audio]        = SetupPTB(window1, setup); %load all the psychtoolbox things

sound.dur = .250; %1.4; % duration of tones in seconds
% have to add extra time here, otherwise it doesn't match visual duration, not sure why!

sound.samplerate      = audio.freq; %100000; 
% check SetupPTB for audio.freq!
sound.samples         = sound.dur*sound.samplerate;

% Generate own white noise
% w = ones(1,sound.samples);
% w = awgn(w,1)*10; % increase here if not loud enough in scanner
% sound.wavedata = [w; w];
% if setup.fmri
%     load whitenoise3 % 250 ms (louder)
% else 
%     load whitenoise2 % 250 ms
% end
% figure; 
%   plot(sound.wavedata(1,:));

%% wav file white noise
if setup.scanner == 4 || setup.scanner == 5
    wavfilename = [ pwd '/whitenoise250.wav']; % mac
else
    wavfilename = [ pwd '\whitenoise250.wav']; % windows
end

[y, freq] = wavread(wavfilename);
sound.wavedata = y';
nrchannels = size(sound.wavedata,1); % Number of rows == number of channels.

% Make sure we have always 2 channels stereo output.
% Why? Because some low-end and embedded soundcards
% only support 2 channels, not 1 channel, and we want
% to be robust in our demos.
if nrchannels < 2
    sound.wavedata = [sound.wavedata ; sound.wavedata];    %Need sound vector as row vector, one row per channel.
    nrchannels = 2;
%     noise.data = wavedata;
%     noise.channels = nrchannels;
end

%% Tone
high      = 880; % 880 Hz
low       = 200; % 200 Hz
med       = 440; % 440 Hz

sound.normal = high;
             
%% Create Audio Buffer
[sound.tonebuf, sound.tonepos] = CreateAudioBuffer(CreateTone(sound.normal, sound.dur, audio.freq), sound.wavedata);

% sound 1 is normal
% sound 2 is white noise 
if setup.whitenoise
    s = 2;
else
    s = 1;
end

PsychPortAudio('FillBuffer', audio.h, sound.tonebuf);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% INITIALIZE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

response.beeptime  = NaN(setup.nblocks, setup.nbeeps);
response.keypress  = NaN(setup.nblocks, setup.nbeeps);
response.key       = cell(setup.nblocks, setup.nbeeps);
response.RT        = NaN(setup.nblocks, setup.nbeeps);

% TRIGGER DISABLED FOR RUNNING DURING SCANNING!
DisableKeysForKbCheck('t');

for block = 1:setup.nblocks
    
    % workaround
    %setup.session = block;

    % setup eyelink
    if setup.Eye
        edfFile = ELconfig(window1, setup, block);
    end
    
    DrawFormattedText(window1.h, ['Je zal af en toe een geluid horen. \n \n '...
        'Jouw taak is druk de knopje met je rechter wijsvinger zo snel mogelijk na elk geluid! \n \n' ...
        'Blijf ALTIJD naar het fixatie punt kijken! Get Ready...'],  'center', 'center');
    Screen('Flip', window1.h);
    
    WaitSecs(6);    
    
    % Draw fixation 
    X = window1.center(1);
    Y = window1.center(2);

%     fix = [window1.rect(3)*.03,window1.rect(4)*.03];
% 
%     r1 = [0 0 fix(1) fix(1)]; % outside
%     r2 = [0 0 fix(2) fix(2)]; % inside

    r1 = [0 0 96 72];
    r2 = [0 0 72 48];

    r1 = r1./3;
    r2 = r2./3;

    r1 = CenterRectOnPoint(r1,X,Y);
    r2 = CenterRectOnPoint(r2,X,Y);

    Screen('FillRect', window1.h, [0 0 0], r1); % outside
    Screen('FillRect', window1.h, [118 118 118], r2); % inside

    Screen('Flip', window1.h);

    %% Present sounds at random intervals

    % random uniform distribution on interval = [noise.lower,noise.upper]
    setup.beeps(block,:) = setup.lower + (setup.upper-setup.lower)*rand(setup.nbeeps,1); 
    %setup.beeps(block,:) = randi([setup.lower setup.upper],[1 setup.nbeeps]);

    response.BEGIN = GetSecs;

    if setup.Eye
        Eyelink ('Message', sprintf('measuring started at %d', response.BEGIN));           
    end     

    WaitSecs(3); % for extrapolation
    
    for i=1:size(setup.beeps,2)
        
        WaitSecs(setup.beeps(block,i));
        
        % change tone here:
        PsychPortAudio('SetLoop',audio.h, sound.tonepos(s,1), sound.tonepos(s,2)); % s: 1 = tone, 2 = white noise
        response.beeptime(block, i) = PsychPortAudio('Start', audio.h, 1, [], 1, [], []); %like flip 
        
            if setup.Eye, Eyelink ('Message', sprintf('sound at %d', response.beeptime(block, i))); end
            %fprintf('sound %i at %d \n', i, response.beeptime(block, i) - response.BEGIN);
                
        % check all keypad devices, wait for single key stroke, wait 2 seconds if no response
                %[secs, keyCode, deltaSecs] = KbWait([deviceNumber][, forWhat=0][, untilTime=inf])
        [response.keypress(block, i), response.key{block,i}, dsecs]  = KbWait(-3 , 2 , response.beeptime(block, i)+2); 

            if setup.Eye, Eyelink ('Message', sprintf('response at %d', response.keypress(block, i))); end
            %fprintf('response %i at %d \n', i, response.keypress(block, i) - response.BEGIN);
        
        response.RT(block, i) = response.keypress(block, i) - response.beeptime(block, i);        
    end % i loop
    
    response.RT(response.RT>2) = NaN; % to distinguish from hitting ceiling times

    WaitSecs(3); % for extrapolation

    if setup.Eye
        Eyelink ('Message', sprintf('measuring ended at %d', GetSecs));           
    end  
       
    DrawFormattedText(window1.h, 'Klaar met deze block',  'center', 'center');
    Screen('Flip', window1.h);
   

    %% save the EL file for this block

    if setup.Eye
        setup.datetime = datestr(now, 'yyyy-mm-dd_HH-MM-SS');
        %  fprintf('Receiving data file ''%s''\n', edfFile );
        setup.eyefilename = sprintf('Data/IRF_P%d_s%d_r%d_b%d_%s.edf', setup.participant, setup.session, setup.run, block, setup.datetime);
        status = Eyelink('ReceiveFile', edfFile, setup.eyefilename); %this collects the file from the eyelink
        disp(status);
        disp(['File ' setup.eyefilename ' saved to disk']);
        % close the eyelink
        Eyelink('StopRecording');
        Eyelink('CloseFile');
        %-------------
        % Create subject specific file and save - add unique datestring to avoid any overwriting of files
        %-------------

        setup.filename = sprintf('Data/IRF_P%d_s%d_r%d_b%d_%s.mat', setup.participant, setup.session, setup.run, block, setup.datetime);
        save(setup.filename, '-mat', 'sound', 'window1', 'audio', 'setup', 'response');
    end
    
end % loop over blocks

disp('done!'); Screen('CloseAll'); ShowCursor;
PsychPortAudio('Stop', audio.h);
sca;


