
function [edfFile] = ELconfig(window1, setup, block)

% setup the Eyelink initialization at the beginning of each block - code from ENS, Paris
dummymode = 0; % set to 1 to run in dummymode (using mouse as pseudo-eyetracker)
el = EyelinkInitDefaults(window1.h);

% turn the calibration background black - similar luminance as experiment
el.msgfontcolour    = window1.black;
el.imgtitlecolour   = window1.black;
el.calibrationtargetcolour = window1.black;
el.backgroundcolour = window1.white;

% el.msgfontcolour    = window1.white;
% el.imgtitlecolour   = window1.white;
% el.calibrationtargetcolour = window1.white;
% el.backgroundcolour = window1.black;

EyelinkUpdateDefaults(el);

% Initialization of the connection with the Eyelink Gazetracker
if ~EyelinkInit(dummymode, 1)
    fprintf('Eyelink Init aborted.\n');
sca

cleanup(useTrigger);  % cleanup function
    return
end

[v, vs ]    = Eyelink('GetTrackerVersion');
fprintf('Running experiment on a ''%s'' tracker.\n', vs );

% make sure that we get event data from the Eyelink
Eyelink('command', 'file_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS'); %"file_sample_data" specifies what type of samples will be wrtten to the EDF file
Eyelink('command', 'link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS'); %"link_sample_data" specifies what type of samples will be sent to link
Eyelink('command', 'drift_correct_cr_disable = OFF'); % To enable the drift correction procedure to adjust the calibration rather than simply allowing a drift check

% open edf file for recording data from Eyelink
% create a temporary name for this (has to be short)
if setup.localizer == true
    EDFname = sprintf('LP%dS%dR%d', setup.participant, setup.session, block);
elseif setup.localizer == false
    EDFname = sprintf('P%dS%dR%d', setup.participant, setup.session, block);
elseif setup.localizer == 3
    EDFname = sprintf('MP%dS%dR%d', setup.participant, setup.session, block);
else
    EDFname = sprintf('XP%dS%dR%d', setup.participant, setup.session, block);
end
edfFile = [EDFname '.edf'];
Eyelink('Openfile', edfFile);

% Calibrate the eye tracker
EyelinkDoTrackerSetup(el);

% see email Marcus from SR research, 3 Feb 2015
Eyelink('command', 'set_idle_mode');
WaitSecs(0.05);

% start recording eye position
Eyelink('StartRecording');
% record a few samples before we actually start displaying
WaitSecs(0.1);
% mark zero-plot time in data file
Eyelink('message', 'start recording Eyelink');

end