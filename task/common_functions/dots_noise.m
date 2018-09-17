function [ display] = dots_noise(display, dots)

% Generates a dot patch according to a limited lifetime
% algorithm, see:
% Pilly, P. K., & Seitz, A. R. (2009).
% What a difference a parameter makes: a psychophysical comparison
% of random dot motion algorithms. Vision Research, 49(13), 1599?612.
%--------------------------------------------------------------------------

NDOTS       = dots.nDots; 
SPEED       = dots.speed; % downward, as a function of speed (in degrees per second) and framerate)
RADIUS      = dots.radius;
INNER       = dots.innerspace; %inner circle doesn't contain dots
COH         = 0; % in this case, hardcode noise
HEMI        = dots.hemi;

% define the noise dots
noisedots           = round(NDOTS*(1-COH)); %nr of noisedots based on the coherence
t1                  = rand(NDOTS,1);
[t1,t2]             = sort(t1);
noiseindex          = t2(1:noisedots); %random subset of dots

% replot the noisedots somewhere in the aperture
rad                 = RADIUS*sqrt(rand(noisedots,1));
theta               = 2*pi*rand(noisedots,1);
pos(noiseindex,:)   = [rad.*cos(theta) rad.*sin(theta)]; %convert to cartesian coordinates
        %--------------------------
        % one side of circle only
        %--------------------------
        pos(noiseindex,1) = abs(pos(noiseindex,1))*HEMI;


%find the dots that have left the aperture
outindex            = find(sqrt((pos(:,1).^2)+(pos(:,2).^2)) >= RADIUS); %index dots that are outside the aperture
pos(outindex, 2)    = -pos(outindex,2); %move back to the top, only change y coordinate
        %--------------------------
        % one side of circle only
        %--------------------------
        pos(outindex,1) = abs(pos(outindex,1))*HEMI;


%find the dots that are too close to the fixation (1 degree)
innerindex          = find(sqrt((pos(:,1).^2)+(pos(:,2).^2)) <= INNER);
rad                 = RADIUS*sqrt(rand(length(innerindex),1));
theta               = 2*pi*rand(length(innerindex),1);
pos(innerindex, :)  = [rad.*cos(theta) rad.*sin(theta)]; %move back to the top, only change y coordinate
        %--------------------------
        % one side of circle only
        %--------------------------
        pos(innerindex,1) = abs(pos(innerindex,1))*HEMI;


% do this again to make sure there are none left
innerindex          = find(sqrt((pos(:,1).^2)+(pos(:,2).^2)) <= INNER);
rad                 = RADIUS*sqrt(rand(length(innerindex),1));
theta               = 2*pi*rand(length(innerindex),1);
pos(innerindex, :)  = [rad.*cos(theta) rad.*sin(theta)]; %move back to the top, only change y coordinate
        %--------------------------
        % one side of circle only
        %--------------------------
        pos(innerindex,1) = abs(pos(innerindex,1))*HEMI;

% draws the dots on the screen for this frame
Screen('DrawDots',display.h, pos', ...
    dots.size, dots.color, display.center, 2);

end