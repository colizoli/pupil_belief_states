%% Calculate actual dot motion parameters 2AFC task 
% Due to human error, the distance settings were incorrect in the code
% used. Need to calculate the actual visual angles, dot speed, dot size and dot
% density.

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

% Visual angle calculator used: http://www.1728.org/angsize.htm
% This script calls deg2pix.m, pix2deg.m (in task/common_functions)

%% 3T MRI experiment
disp('3T experiment');
% Resolution of MRI screen
window1.res = [1920,1080];
window1.res.width = 1920;
window1.res.height = 1080;

% Measured by hand the following:
window1.dist = 120; %cm actual distance eyes to screen in scanner
window1.width = 70; %cm actual width of screen
% The stimulus is 35.5 cm on the scanner screen (diameter) 
% The real distance from the person to the screen is 120 cm.
% The screen width is 70 cm (31.55" screen)
% The real outer circle visual angle on the scanner screen is 16.8 degrees.
% The real inner circle 5 cm = 2.4 degrees
% The real fixation rectangle width = .9525 cm = .45 degrees

% What was in the code presented
% window1.dist = 50 % cm
% window1.width = 47 % cm
% dots.radius = 14 % degrees = 502 pixels
% dots.innerspace = 2 % degrees = 71 pixels
% dots.speed = 11.5 % deg/sec = 411 pixels
% dots.size = 0.2 % deg = 7 pixels
% dots.density = .85 % dots per deg2, there were 524 dots

% Given actual distance, resolution, and speed (in pixels)... 
% Calculate degrees/second:
disp('dot speed in deg/s');
pix = 411; % # pixels output
ang = pix2deg(window1,pix);
disp(ang);
% 7.15 deg/sec

% Calculate size dots:
disp('dot size in deg');
pix = 7;
ang = pix2deg(window1,pix);
disp(ang);
% = 0.12 deg

% Calculate outer circle radius:
% radius! not diameter
disp('RADIUS of outer circle in deg');
pix = 502;
ang = pix2deg(window1,pix);
disp(ang);
% 8.7 deg * 2 = 17.4 (measured 16.8 by hand, some measurement error here)

% Calculate inner circle radius:
% radius! not diameter
disp('RADIUS of inner circle in deg');
pix = 71;
ang = pix2deg(window1,pix);
disp(ang);
% 1.2 deg * 2 = 2.4 deg

% Calculate density: note all dots are forced into one visual hemifield
disp('dot density in deg^2');
dots.radius  = deg2pix(window1, 8.4);
dots.density = 2.37; 
dots.nDots   = round(dots.density*pi*pix2deg(window1, dots.radius)^2);
disp(dots.nDots);
% should equal 524

% Calculate density: note all dots are forced into one visual hemifield
% so the real density is x2 or x4?
disp('fixation');
pix = 32; % was always constant
ang = pix2deg(window1,pix);
disp(ang);
% .56 deg (measured .45 by hand, some measurement error here)


