function [dots, fix] = setupDots(window1, setup)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% DOTS CHARACTERISTICS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% ALL SIZES ARE HERE IN DEGREES!
% while the dots structure output is given in # of pixels
dots                   = struct; %preallocate
% parameters that stay constant

dots.radius            = deg2pix(window1, 8.4); % RADIUS, not diameter!! % keep constant, Anne had 12 degrees
dots.innerspace        = deg2pix(window1, 1.2); % RADIUS, not diameter! Anne had 2 degrees
dots.lifetime          = 10; % in frames
dots.nvar              = 3; %interleave variants of the stimulus
dots.color             = [255 255 255]; % always 100% dot contrast

% determine the appearance of the dots - as in Siegel, 2007
dots.speed             = deg2pix(window1, 7.5); % speed of the dots in degrees/second
dots.size              = deg2pix(window1, .15); %size of each dot in degrees
dots.density           = 2.37; % dot density in dots per degree^2
dots.nDots             = round(dots.density*pi*pix2deg(window1, dots.radius)^2); %number of dots in the circle, calculated from density (can also just be a fixed nr, eg. 500)
% should be 524 dots

%-------------------------
% Hemifield Left or Right?
%-------------------------
% If setup.hemifieldfirst = 1, 
    % ODD Sessions: ODD Runs = LEFT, EVEN Runs = RIGHT
    % EVEN Session: ODD Runs = RIGHT, EVEN Runs = LEFT
% If setup.hemifieldfirst = 0, 
    % ODD Sessions: ODD Runs = RIGHT, EVEN Runs = LEFT
    % EVEN Session: ODD Runs = LEFT, EVEN Runs = RIGHT

            switch setup.hemifieldfirst % check condition
            case 1 % Condition 1
                    switch mod(setup.session,2) % check session
                    case 1 % odd session
                            switch mod(setup.run,2) % check run
                            case 1 % odd run
                                dots.hemi = -1; % left
                            case 0 % even run
                                dots.hemi = 1; % right
                            end
                    case 0   % even session
                            switch mod(setup.run,2) % check run
                            case 1 % odd run
                                dots.hemi = 1; % right
                            case 0 % even run
                                dots.hemi = -1; % left
                            end
                    end    
            case 2 % Condition 2
                    switch mod(setup.session,2) % check session
                    case 1 % odd session
                            switch mod(setup.run,2) % check run
                            case 1 % odd run
                                dots.hemi = 1; % right
                            case 0 % even run
                                dots.hemi = -1; % left
                            end
                    case 0   % even session
                            switch mod(setup.run,2) % check run
                            case 1 % odd run
                                dots.hemi = -1; % left
                            case 0 % even run
                                dots.hemi = 1; % right
                            end
                    end
            otherwise
                    disp('Something went wrong with counterbalancing hemifields!');
            end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% FIXATION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

fix.dotsize         = deg2pix(window1,0.2); % fixation dot
fix.circlesize      = deg2pix(window1,0.6); % circle around fixation dot
% fix.color1          = [118 118 118]; % outside and color for Anne's fix cross
% fix.color2          = [0 0 0]; % inside

fix.color1          = [0 0 0]; % outside and color for Anne's fix cross
fix.color2          = [118 118 118]; % inside
fix.flip            = 0;

end