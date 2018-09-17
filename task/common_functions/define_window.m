function [window1] = define_window(setup)
% ONE FILE for Behavioral_2AFC, fMRI_2AFC and fMRI_MT_Localizer
%-------------
% window1 settings
%-------------
    if setup.scanner     == 1
        window1.dist            = 120; % Roeters scanner
        window1.width           = 70; % Roeters scanner  
    end
end
