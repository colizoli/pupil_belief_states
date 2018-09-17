function [ stimuli] = dots_limitedlifetime(setup, display, dots, block, trial, stimuli)

% Generates a dot patch according to a limited lifetime
% algorithm, see:
% Pilly, P. K., & Seitz, A. R. (2009).
% What a difference a parameter makes: a psychophysical comparison
% of random dot motion algorithms. Vision Research, 49(13), 1599?612.
%--------------------------------------------------------------------------

%% Edited by Elisa Mon 17 March 2014 (spec. DIRECTION)

NVAR        = dots.nvar; % interleaved sequence
LIFETIME    = dots.lifetime;
NDOTS       = dots.nDots; % 774, 3097
DIRECTION   = dots.direction(block,trial); % so it'll use a different direction each trial
SPEED       = dots.speed; % downward, as a function of speed (in degrees per second) and framerate)
NFR         = ceil(setup.nframes/NVAR);
RADIUS      = dots.radius;
INNER       = dots.innerspace; %inner circle doesn't contain dots
HEMI        = dots.hemi;

    if length(dots.coherence) > 1, % in case of the thresholding session, use different levels of coherence
        COH = dots.coherence(block, trial);
    else
        COH = dots.coherence; % use the one same value for all trials
    end


for var = 1:NVAR, %create separate variants
    
    % generate random starting points within a circular aperture
    rad     = RADIUS*sqrt(rand(NDOTS,1));
    theta   = 2*pi*rand(NDOTS,1);
    pos     = [rad.*cos(theta) rad.*sin(theta)]; %convert to cartesian coordinates
        %--------------------------
        % one side of circle only
        %--------------------------
        pos(:,1) = abs(pos(:,1))*HEMI; 
    
    % assign each dot a scalar that indicates how long it has been
    % 'alive' (that is, a signal dot)
    % Each dot will have a integer value 'life' which is how many frames the
    % dot has been going.  The starting 'life' of each dot will be a random
    % number between 0 and dots.lifetime-1 so that they don't all 'die' on the
    % same frame:
    
    life    = ceil(rand(1,NDOTS)*LIFETIME);
    
    for frameNum = 1:NFR,
        
        % define the noise dots
        noisedots           = round(NDOTS*(1-COH)); %nr of noisedots based on the coherence
        t1                  = rand(NDOTS,1);
        [t1,t2]             = sort(t1);
        noiseindex          = t2(1:noisedots); %random subset of dots
        % define signal dots
        signalindex         = t2(noisedots+1:end); %the dots that are signal
        
        % move signal dots with a certain speed in the right direction
        pos(signalindex,:)  = [SPEED.*cos(-DIRECTION*pi/180)/display.frameRate+pos(signalindex,1), ...
            SPEED.*sin(-DIRECTION*pi/180)/display.frameRate+pos(signalindex,2)]; %convert to cartesian coordinates
        
        % replot the noisedots somewhere in the aperture
        rad                 = RADIUS*sqrt(rand(noisedots,1));
        theta               = 2*pi*rand(noisedots,1);
        pos(noiseindex,:)   = [rad.*cos(theta) rad.*sin(theta)]; %convert to cartesian coordinates
            %--------------------------
            % one side of circle only
            %--------------------------
            pos(noiseindex,1) = abs(pos(noiseindex,1))*HEMI; 
        
        %increment the 'life' of each dot
        life                = life+1;
        
        %find the 'dead' dots
        deadindex           = mod(life,LIFETIME)==0;
        deaddots            = length(find(deadindex==1));
        
        %replace the positions of the dead dots to a random location
        rad                 = RADIUS*sqrt(rand(deaddots,1));
        theta               = 2*pi*rand(deaddots,1);
        pos(deadindex,:)    = [rad.*cos(theta) rad.*sin(theta)]; %convert to cartesian coordinates
            %--------------------------
            % one side of circle only
            %--------------------------
            pos(deadindex,1) = abs(pos(deadindex,1))*HEMI; 
        
        
        %find the dots that have left the aperture
        outindex            = find(sqrt((pos(:,1).^2)+(pos(:,2).^2)) >= RADIUS); %index dots that are outside the aperture
        % wrap them around in the direction where they came from
        [theta, rad]        = cart2pol(pos(outindex, 1), pos(outindex,2));
        theta               = theta + pi; %move to the other side of the circle
        rad                 = RADIUS*ones(length(rad),1);
        pos(outindex, :)    = [rad.*cos(theta) rad.*sin(theta)]; %move back to the top, only change y coordinate
            %--------------------------
            % one side of circle only
            %--------------------------
            pos(outindex,1) = abs(pos(outindex,1))*HEMI; 
        
        %find the dots that are too close to the fixation
        innerindex          = find(sqrt((pos(:,1).^2)+(pos(:,2).^2)) <= INNER);
        [theta, rad]        = cart2pol(pos(innerindex, 1), pos(innerindex, 2));
        rad                 = INNER + (RADIUS - INNER)*sqrt(rand(length(innerindex),1)); %random radius
        theta               = theta + pi;
        pos(innerindex, :)  = [rad.*cos(theta) rad.*sin(theta)]; %move back to the top, only change y coordinate
            %--------------------------
            % one side of circle only
            %--------------------------
            pos(innerindex,1) = abs(pos(innerindex,1))*HEMI; 
              
        % save the positions per variant
        temp{var,frameNum}  = pos';
    end
end

%% this is not the most elegant code, but is used to interleave the multiple variants of the stimulus created
if NVAR > 1,
    % interleave the cell arrays with position information
    Interleaved = reshape(temp, 1, NFR*NVAR);
    for frame = 1:length(Interleaved),
        % allocate all the dot positions from this trial to the stimulus structure
        stimuli(frame, :, :) = Interleaved{frame};
        %stimuliy(frame, :) = Interleaved{frame}(2,:);
    end
    
    % cut the last frames off to have the correct dims
    stimuli = stimuli(1:setup.nframes, :, :);
    
else %one variant, no interleaving
    for frame = 1:NFR,
        stimuli(frame, :, :) = temp{frame};
    end
end


end