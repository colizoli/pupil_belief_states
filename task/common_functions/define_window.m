function [window1] = define_window(setup)
% ONE FILE for Behavioral_2AFC, fMRI_2AFC and fMRI_MT_Localizer
%-------------
% window1 settings
%-------------
% 1 = Roeterseiland, 2 = 7T AMC, 3 = 3T AMC (4 = O' Big Mac, 5 = O's laptop, 6 = lab 2.19)
    %   window1.dist            = 45; % lab 1.01
    %   window1.width           = 47; % lab 1.01
    if setup.scanner     == 1
        window1.dist            = 120; % Roeters scanner
        window1.width           = 70; % Roeters scanner  
    elseif setup.scanner == 2
        window1.dist            = 67; % 7T Spinoza AMC 
        window1.width           = 65; % 7T Spinoza AMC    
        % Was here before 24 Sept 2015...
    %     window1.dist            = 35; % 7T Spinoza AMC 
    %     window1.width           = 65; % 7T Spinoza AMC
    elseif setup.scanner == 3
        window1.dist            = 60; % 3T Spinoza AMC
        window1.width           = 65; % 3T Spinoza AMC
    elseif setup.scanner == 4
        window1.dist            = 60; % big mac
        window1.width           = 60; % big mac
    elseif setup.scanner == 5
        window1.dist            = 35; % O's laptop
        window1.width           = 28; % O's laptop
    elseif setup.scanner == 6
        window1.dist            = 32; % Lab 2.19
        window1.width           = 30; % Lab 2.19
    end
    
%     window1.dist            = 45; % lab 1.01
%     window1.width           = 47; % lab 1.01

end
