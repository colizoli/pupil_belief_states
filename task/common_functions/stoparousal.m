function [noise] = stoparousal(noise)

    noise.meta2 = PsychPortAudio('GetStatus', noise.handle);
    noise.duration = GetSecs - noise.started;
    noise.stopped = noise.duration + noise.started;
        
    % Stop playback:
    PsychPortAudio('Stop', noise.handle);
    
    % Close the audio device:
    PsychPortAudio('Close', noise.handle);
end