function [noise] = arousalCheckVolume(repetitions, wavfilename)
% BasicSoundOutputDemo([repetitions=0][, wavfilename])
%
% Demonstrates very basic usage of the new Psychtoolbox sound output driver
% PsychPortAudio(). PsychPortAudio is a completely new sound output driver
% for Psychtoolbox, meant as a better, more reliable, more accurate
% replacement for the old Psychtoolbox SND() function and other means of
% sound output in Matlab like sound(), soundsc(), wavplay(), audioplayer()
% etc.
%
% PsychPortAudio is currently only available for OS/X on Intel based
% Macintosh computers and for Microsoft Windows. OS/X PowerPC and Linux
% will follow in the foreseeable future. The driver is in early beta stage,
% fine-tuning, testing and validation will take some time. If you need
% sound output, give it a try but don't be disappointed if it doesn't work
% perfect, instead report issues to the forum. We don't expect any trouble
% on OS/X, but given the huge variability on the Windows platform (and the
% low quality of many sound drivers on Windows), that may need some tweaking,
% so please provide feedback!
%
% This demo only demonstrates normal operation, not the low-latency mode,
% extra demos and tests for low-latency and high precision timing output will
% follow soon. If you need low-latency, make sure to read "help
% InitializePsychSound" carefully or contact the forum.
% Our preliminary testing for low-latency mode showed that sub-millisecond
% accurate sound onset and << 10 msecs latency are possible on OS/X and on
% some specially configured M$-Windows setups.
%
%
% Optional arguments:
%
% repetitions = Number of repetitions of the sound. Zero = Repeat forever
% (until stopped by keypress), 1 = Play once, 2 = Play twice, ....
%
% wavfilename = Name of a .wav sound file to load and playback. Otherwise
% the good ol' handel.mat file (part of Matlab) is used.
%
% The demo just loads and plays the soundfile, waits for a keypress to stop
% it, then quits.

% History:
% 06/07/2007 Written (MK)

% Running on PTB-3? Abort otherwise.
AssertOpenGL;

if nargin < 1
    repetitions = [];
end

if isempty(repetitions)
    repetitions = 0;
end

% Filename provided?
if nargin < 2
    wavfilename = [];
end

% if isempty(wavfilename)
%     % Ok, assign this as default sound file: Better than ol' handel - we're
%     % sick of that sound.
%     wavfilename = [ PsychtoolboxRoot 'PsychDemos' filesep 'SoundFiles' filesep 'funk.wav'];
% end

if isempty(wavfilename)
        
    % No sound file provided. Load pink noise!
    % L = 60000; % the duration of the sound will be number of samples/sample rate: L/freq
    % e.g. L = 60000 and freq = 1000 produce 60 seconds of sound
    % wavedata = pinknoise(L);
    nrchannels = 2; % One channel only -> Mono sound.
    % Fs is the correct playback frequency for handel.
    freq = 48000;   % 1000, 2000 sound OK   

        
    %noise.wave1 = ones(1, 100000);

    %noise.nwave1 = awgn(noise.wave1,2);
    %noise.nwave2 = awgn(noise.wave1,10);
    %noise.nwave3 = awgn(noise.wave1,20);

    load whitenoise3;
    %wavedata = [ noise.nwave1 noise.nwave2 noise.nwave3 ];
     wavedata = sound.wavedata;
     
        noise.data       = wavedata;
        noise.channels   = nrchannels;
        noise.samplerate = freq;       
        
        
else
    % Read WAV file from filesystem:
        noise.wvname = wavfilename;
    [y, freq] = wavread(wavfilename);
    wavedata = y';
    nrchannels = size(wavedata,1); % Number of rows == number of channels.
end

% Make sure we have always 2 channels stereo output.
% Why? Because some low-end and embedded soundcards
% only support 2 channels, not 1 channel, and we want
% to be robust in our demos.
if nrchannels < 2
    wavedata = [wavedata ; wavedata];    %Need sound vector as row vector, one row per channel.
    nrchannels = 2;
        noise.data = wavedata;
        noise.channels = nrchannels;
end

% Perform basic initialization of the sound driver:
InitializePsychSound;

% Open the default audio device [], with default mode [] (==Only playback),
% and a required latencyclass of zero 0 == no low-latency mode, as well as
% a frequency of freq and nrchannels sound channels.
% This returns a handle to the audio device:
try
    % Try with the 'freq'uency we wanted:
    pahandle = PsychPortAudio('Open', [], [], 0, freq, nrchannels);
catch
    % Failed. Retry with default frequency as suggested by device:
    fprintf('\nCould not open device at wanted playback frequency of %i Hz. Will retry with device default frequency.\n', freq);
    fprintf('Sound may sound a bit out of tune, ...\n\n');

    psychlasterror('reset');
    pahandle = PsychPortAudio('Open', [], [], 0, [], nrchannels);
end

% Fill the audio playback buffer with the audio data 'wavedata':
PsychPortAudio('FillBuffer', pahandle, wavedata);

% Start audio playback for 'repetitions' repetitions of the sound data,
% start it immediately (0) and wait for the playback to start, return onset
% timestamp.
t1 = PsychPortAudio('Start', pahandle, repetitions, 0, 1);

% Wait for release of all keys on keyboard:
KbReleaseWait;

fprintf('Audio playback started, press any key for about 1 second to quit.\n');

lastSample = 0;
lastTime = t1;

s = PsychPortAudio('GetStatus', pahandle);

    noise.started = t1;
    noise.handle = pahandle;

% Stay in a little loop until keypress:
while s.Active

    % Wait a seconds...
    WaitSecs(1);

    % Print it:
    fprintf('\n\nAudio playback running\n');
    fprintf('This is some status output of PsychPortAudio:\n');
    disp(s);
    
    realSampleRate = (s.ElapsedOutSamples - lastSample) / (s.CurrentStreamTime - lastTime);
    fprintf('Measured average samplerate Hz: %f\n', realSampleRate);
    
    tHost = s.CurrentStreamTime;
    clockDelta = (s.ElapsedOutSamples / s.SampleRate) - (tHost - t1);
    clockRatio = (s.ElapsedOutSamples / s.SampleRate) / (tHost - t1);
    fprintf('Delta between audio hw clock and host clock: %f msecs. Ratio %f.\n', 1000 * clockDelta, clockRatio);
    
    % Query current playback status and print it to the Matlab window:
    s = PsychPortAudio('GetStatus', pahandle);
    % tHost = GetSecs;
    
    keyIsDown = KbCheck();
    if keyIsDown
        break;
    end 
end

playtime = GetSecs - t1;
    disp(playtime);
    noise.stopped = playtime + t1;
    noise.duration = playtime;

% Stop playback:
PsychPortAudio('Stop', pahandle);

% Close the audio device:
PsychPortAudio('Close', pahandle);

% Done.
fprintf('Demo finished, bye!\n');

    noise.meta = s;

% figure;
%     plot(wavedata(1,:));
%     t = ['Sound wave. Sampling Rate Freq: ' num2str(freq)];
%     title(t);


