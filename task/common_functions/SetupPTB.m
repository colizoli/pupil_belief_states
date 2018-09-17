function [window1, audio] = SetupPTB(window1, setup)

% unify keycodes
KbName('UnifyKeyNames');

if setup.scanner == 2
    % help BeampositionQueries
    Screen('Preference', 'VBLTimestampingMode', 2); % 1 and 2 work!
%        1 = Use beamposition. Should it fail, switch to use of kernel-level/CoreVideo
%        timestamps. If that fails as well or is unavailable, use noisy
%        stamps.
%        2 = Use beamposition, but cross-check with kernel-level/CoreVideo timestamps.
%        Use noisy stamps if beamposition mode fails. This is for the paranoid
%        to check proper functioning.
%
%        Screen('Preference', 'ConserveVRAM', 4096);
%        This did not help with the timing issue at 7T
end

% skip PTB checks
if window1.skipChecks
    Screen('Preference', 'Verbosity', 0);
    Screen('Preference', 'SkipSyncTests', 1);
    Screen('Preference', 'VisualDebugLevel', 0);
    % suppress warnings to the pput window
    Screen('Preference', 'SuppressAllWarnings', 1);
end

% % find the right screen
% screens = Screen('Screens');
% for s = 1:length(screens),
%    res = Screen('Resolution',screens(s));
%     if res.width == 1024 && res.height == 768 && res.hz == 60,
%         thisScreen = screens(s);
%     end
% end
% 
% res = Screen('Resolution',thisScreen);
% %assert((res.width == 1024 && res.height == 768 && res.hz == 60), 'DID NOT FIND CORRECT SCREEN');

thisScreen = 0;
% in lab D1.09, select the CRT monitor
window1.screenNum = thisScreen;

% get the screen indices for the different colors
window1.white    = WhiteIndex(window1.screenNum);
window1.black    = BlackIndex(window1.screenNum);
window1.gray     = round((window1.white+window1.black)/2); %rounding avoids problem with textures
window1.bgColor  = window1.black;
%window1.bgColor  = window1.white;
window1.res      = Screen('Resolution', window1.screenNum);

% Open the window1
if setup.debug
    [window1.h, window1.rect] =Screen('OpenWindow',window1.screenNum,window1.bgColor, [0 0 750 750]);
else
    [window1.h, window1.rect] = Screen('OpenWindow',window1.screenNum,window1.bgColor);
end

% find out what happens without the blendfunction?
Screen(window1.h,'BlendFunction',GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

% Set the display parameters 'frameRate' and 'resolution'
window1.frameDur = Screen('GetFlipInterval',window1.h); %duration of one frame
window1.frameRate = 1/window1.frameDur; %Hz

[window1.center(1), window1.center(2)] = RectCenter(window1.rect); % [window1.rect(3)/2 window1.rect(4)/2];
% include a slack for Flip 'when' management
window1.slack    = window1.frameDur / 3;

%% now the audio setup
InitializePsychSound(1);  % request low latency mode

audio           = [];
audio.freq      = 48000; % 48000 for Spinoza Roeterseiland, 2 Channel
% open default soundport, in stereo (to match the sound matrix we create)
%audio.h         = PsychPortAudio('Open', [], 1, [], audio.freq, 2, [], []);
    audio.h = PsychPortAudio('Open', [], [], 0, audio.freq, 2);

HideCursor;
commandwindow;

disp('PTB setup complete');

% Show the subject some instructions
Screen('TextSize', window1.h, 20);
Screen('DrawText',window1.h, 'Loading the experiment.....', window1.center(1)*0.60, window1.center(2) , window1.black );
Screen('Flip', window1.h);

end