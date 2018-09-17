function [sound] = setupSounds(audio, setup)
%% auditory feedback

sound.dur = .25; %1.4; % duration of tones in seconds
% have to add extra time here, otherwise it doesn't match visual duration, not sure why!

%sound.samplerate      = audio.freq; %100000; 
% check SetupPTB for audio.freq!
%sound.samples         = sound.dur*sound.samplerate;


%% generate own white noise
% if setup.fmri
%     load whitenoise3 % 250 ms (louder)
% else
%     load whitenoise2 % 250 ms
% end
% w = ones(1,sound.samples);
% w = awgn(w,1)*25; % this function missing on a lot of computers!
% sound.wavedata = [w; w];
% 
%        figure; 
%        plot(sound.wavedata(1,:));

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


%% Create tone
high      = 880; % 880 Hz
low       = 200; % 200 Hz
med       = 440; % 440 Hz

sound.normal = high;
             
[sound.tonebuf, sound.tonepos] = CreateAudioBuffer(CreateTone(sound.normal, sound.dur, audio.freq), sound.wavedata);

                % sound 1 is normal
                % sound 2 is white noise 

PsychPortAudio('FillBuffer', audio.h, sound.tonebuf);

end