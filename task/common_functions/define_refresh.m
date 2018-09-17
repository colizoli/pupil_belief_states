function [window1] = define_refresh(setup, window1)
% ONE FILE for Behavioral_2AFC, fMRI_2AFC and fMRI_MT_Localizer

    % 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' Big Mac, 5 = O's laptop, 6 = lab 2.19)

    %-------------
    % REFRESH RATE
    %-------------
    % 7T AMC use 30 Hz overwrite
    % 3T Roeters use 30 Hz overwrite
    % DO NOT OVERWRITE REFRESH RATE AT 3T AMC!!!
        % Lab 2.19 works fine without overwriting the refresh rate (60 Hz)
    %-------------
    % CHECK THIS AGAIN!!!
    if setup.scanner == 1               % Roeters
    %      window1.frameRate      = 30; 
    %      window1.frameDur       = .0332;    
    % Timing is OK at 120 Hz, but the graphical artefact is there
    elseif setup.scanner == 2           % 7T AMC
        % NO need to overwrite, see SetupPTB
    %      window1.rect(3)        = 1920;
    %      window1.center         = [window1.rect(3)/2 540];
    elseif setup.scanner == 3           % 3T AMC
        % it was running OK at the pulled refresh rate 60 Hz (check again)
    elseif setup.scanner == 4           % Big Mac
         window1.frameRate      = 60; 
         window1.frameDur       = .0166; 
    elseif setup.scanner == 5           % Laptop
         window1.frameRate      = 60; 
         window1.frameDur       = .0166;
    end

    % window1.frameRate  = 60; 
    % window1.frameDur   = .0166;

    % window1.frameRate  = 15;
    % window1.frameDur   = .0665; 

    % window1.frameRate  = 120; 
    % window1.frameDur   = .0083; 
end
