function [setup, dots, fix, results, flip, sound] = config_Behavioral_Threshold(window, setup, audio)

% general experimental design
setup.cohlevel          = [0, 2.5, 5, 10, 20, 40, 80] / 100; %[0, 2.5, 5, 10, 20, 40, 80] / 100;
setup.trialrep          = 100; %nr of trials per coherence level - should be 100 (50 per hemisphere)
setup.totalntrials      = round(setup.trialrep * length(setup.cohlevel));
setup.nblocks           = 10; % 10 % needs to be > 1 for hemifields to flip correctly...
setup.ntrials           = setup.totalntrials / setup.nblocks;
assert(~mod(setup.ntrials,1), 'Number of trials per block is not integer');
setup.counterbalancing  = mod(setup.participant,2);
% use only one block if at all possible
setup.cancel = false;
setup.session           = 1;
setup.run               = 1;

% timing
setup.fixtime           = (2 + .5*rand(setup.nblocks, setup.ntrials)); %generate the fixation time 1.6 - 1.8s (36-48 frames)
setup.viewingtime       = .75; % viewing duration in seconds (fixed in this script, or maximum viewing duration in RT paradigm
setup.nframes           = ceil(setup.viewingtime*window.frameRate); %number of frames the stimulus is displayed
setup.maxRT             = 3; % maximum time for response

%-------------------
% Hemifield counterbalancing
%-------------------
% If setup.hemifieldfirst = 1, 
    % ODD Sessions: ODD Runs = LEFT, EVEN Runs = RIGHT
    % EVEN Session: ODD Runs = RIGHT, EVEN Runs = LEFT
% If setup.hemifieldfirst = 0, 
    % ODD Sessions: ODD Runs = RIGHT, EVEN Runs = LEFT
    % EVEN Session: ODD Runs = LEFT, EVEN Runs = RIGHT
% see setupDots.m
hemicondition = repmat([1 2 2 1], 1,250); % to prevent confounds with button conditions and feedback conditions
setup.hemifieldfirst    = hemicondition(setup.participant);


%% design
[dots, fix]             = setupDots(window, setup);

% do some randomization
directions              = Shuffle(repmat([90 270]', [setup.ntrials setup.nblocks]))';
dots.direction          = directions(1:setup.nblocks,1:setup.ntrials);

dots.coherence          = Shuffle(repmat(setup.cohlevel', [ceil(setup.ntrials/length(setup.cohlevel)) setup.nblocks ]))';
dots.coherence          = dots.coherence(1:setup.nblocks, 1:setup.ntrials);

% auditory feedback, using some ENS functions (probably from Valentin)
sound = setupSoundsThresh(setup, audio);

%% preallocate results and stimuli structure
% preallocation is a good habit to make sure that Matlab knows how big your
% output structures will be. You might run into memory problems if your
% structures grow on each loop - Matlab will have to find a new chunk of
% memory each time which costs significant time.

results.response            = NaN(setup.nblocks, setup.ntrials);
results.correct             = NaN(setup.nblocks, setup.ntrials);
results.RT                  = NaN(setup.nblocks, setup.ntrials);

% preallocate a full flip structure to store the output of every dynamic
% flip
flip.fix.VBL            = nan(setup.nblocks, setup.ntrials, ceil(max(max(setup.fixtime))/window.frameDur));
flip.fix.StimOns        = flip.fix.VBL;
flip.fix.FlipTS         = flip.fix.VBL;
flip.fix.Missed         = flip.fix.VBL;
flip.fix.beampos        = flip.fix.VBL;

flip.stim.VBL           = nan(setup.nblocks, setup.ntrials, setup.nframes);
flip.stim.StimOns       = flip.stim.VBL;
flip.stim.FlipTS        = flip.stim.VBL;
flip.stim.Missed        = flip.stim.VBL;
flip.stim.beampos       = flip.stim.VBL;

flip.waitRT.VBL        = nan(setup.nblocks, setup.ntrials, ceil(setup.maxRT/window.frameDur));
flip.waitRT.StimOns    = flip.waitRT.VBL;
flip.waitRT.FlipTS     = flip.waitRT.VBL;
flip.waitRT.Missed     = flip.waitRT.VBL;
flip.waitRT.beampos    = flip.waitRT.VBL;

end