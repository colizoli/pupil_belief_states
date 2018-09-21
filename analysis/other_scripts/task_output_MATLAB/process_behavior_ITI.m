% Put all behavioral data for the 2AFC task in one file
% O. Colizoli Jan 2016

% OUTPUT .mat file will be saved in the analyses path.
% Size = (trials*runs*sessions*participants,conditions)
% LCDec2.behav.data
% LCDec2.behav.headers (condition names)

% Phases 
% phase 1 - baseline period
% phase 2 - pre trial period (wait for trigger)
% phase 3 - stimulus on period (750 ms)
% phase 4 - stim offset -> response
% phase 5 - response -> feedback
% phase 6 - feedback & ITI after feedback

% Behavioral output
% column 1 - coherence
% column 2 - hemifield
% column 3 - direction
% column 4 - response
% column 5 - correct
% column 6 - RT
% column 7 - tone

% NOTES
% missing runs (6 in total): pp4_session1 3-6, pp7_session1 6, pp14_session1 6

clear all; close all; clc;

% folder with real data
% cd('/Volumes/DropboxMacOlympia/Dropbox/WORK/Tobi/2AFC_LCDecisions/RESULTS_RAWDATA/PP1/PP1_fMRI_Session1/PP1_AFC1');
% experiment script folder 3T fmri version
% cd('/Volumes/DropboxMacOlympia/Dropbox/WORK/Tobi/2AFC_LCDecisions/2AFC_Experiment_Olympia/2AFC_0911_ScannerVersion3T_MostRecent');

path_analyses = '/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/RESULTS_ANALYZED';
path_raw = '/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/RESULTS_RAWDATA';
cd(path_raw);

behav_headers = {'coherence','hemifield','direction','response','correct','RT','tone'};
phase_headers = {'baseline period','pre trial period (wait for trigger)','stimulus on period (750 ms)','stim offset -> response','response -> feedback','ITI after feedback'};
output_headers = {'subject_number',...%1
    'session',...%2
    'run',...%3
    'trial_number',...%4
    'arousal_condition',...%5
    'high_arousal',...%6
    'low_arousal',...%7
    'coherence_level',...%8
    'diff_easy',...%9
    'diff_hard',...%10
    'hemifield_condition',...%11
    'hemifield_left',...%12
    'hemifield_right',...%13
    'dot_motion_direction',...%14
    'dot_motion_up',...%15
    'dot_motion_down',...%16
    'response',...%17
    'accuracy',...%18
    'RT',...%19
    'correct_reject',...%20
    'false_alarm',...%21
    'hit',...%22
    'miss',...%23
    'right_hand_response',...%24
    'omission',...%25
    'isi',... %26
    'ITI'}; %27
output_headers = transpose(output_headers);

% SAVE DATA MATRIX
% (trials, conditions, runs, sessions, participants)
trials       = 25;
conditions   = 50; % leave space for new ones
runs         = 6;
sessions     = 4;
participants = 15;

ALL = NaN(1,conditions); % place holder for pushing new matrices into it

% Loop through subject folders, fMRI_session folders, go into AFC folder
folders = dir; % SUBJECTS
folders = folders([folders.isdir]); % get only folders
folders(strncmp({folders.name}, '.', 1)) = []; % take out the hidden folders with dots

for i = 1:length(folders)
     subj = folders(i).name;
     cd(subj);
     subj_folders = dir([subj '*']); % SESSIONS
     subj_folders = subj_folders([subj_folders.isdir]); % get only folders
     subj_folders(strncmp({subj_folders.name}, '.', 1)) = []; % take out the hidden folders with dots
     
     for j=1:length(subj_folders)
        session = subj_folders(j).name;
        cd(session);
        cd([subj '_AFC' num2str(j)]);
        MAT = dir('*.mat'); % SCANS/RUNS    
        
        for k=1:length(MAT)
            
        % Particpant, session, run, trial number info
        this.data = load(MAT(k).name);
        this.data.new_out = NaN(this.data.setup.ntrials,50); 
        this.data.new_out(:,1) = this.data.setup.participant; % 1
        this.data.new_out(:,2) = this.data.setup.session; % 2
        this.data.new_out(:,3) = this.data.setup.run; % 3
        this.data.new_out(:,4) = 1:this.data.setup.ntrials; % 4 

        % Behavior
        % 5 Arousal Condition
        this.data.new_out(:,5) = this.data.sound.tones; % white noise
        % 6 High Arousal
        this.data.new_out(:,6) = this.data.sound.tones == 2; % white noise
        % 7 Low Arousal
        this.data.new_out(:,7) = this.data.sound.tones == 1; % tone
        % tone 1 2 white noise or beep, high or low arousal
            % setupSounds.m
            % sound 1 is normal tone, low arousal
            % sound 2 is white noise, high arousal

        % 8 Coherence Level
        this.data.new_out(:,8) = round(this.data.results.output(:,1),4);

        % 9 Difficulty Level = Easy
        this.data.new_out(:,9)  = round(this.data.results.output(:,1),4) == round(this.data.setup.cohlevel2,4); % 4 decimal places, gives 1 is easy, 0 is hard 
        % 10 Difficulty Level = Hard
        this.data.new_out(:,10) = round(this.data.results.output(:,1),4) == round(this.data.setup.cohlevel1,4);
            % if coherence1 < coherence2, coherence1 = hard (70% difficulty), coherence2 = easy (85% difficulty)
            % setup.cohlevel1 is 'hard';
            % setup.cohlevel2 is 'easy';

        % 11 Hemifield Condition
        this.data.new_out(:,11) =   this.data.results.output(:,2); % column 2 behavioral file
        % 12 Hemifield is left -1
        this.data.new_out(:,12) =   this.data.results.output(:,2) == -1; % column 2 behavioral file
        % 13 Hemifield is right 1
        this.data.new_out(:,13) =   this.data.results.output(:,2) == 1; % column 2 behavioral file

        % 14 Dot Motion Direction
            % 90 is up
            % 270 is down
        this.data.new_out(:,14) =   this.data.results.output(:,3); % column 3 behavioral file
        % 15 Dot Motion UP Direction 90
        this.data.new_out(:,15) =   this.data.results.output(:,3) == 90; % column 3 behavioral file
        % 16 Dot Motion DOWN Direction 270
        this.data.new_out(:,16) =   this.data.results.output(:,3) == 270; % column 3 behavioral file

        % 17 Response 90 270 up or down? 
        this.data.new_out(:,17) =   this.data.results.output(:,4); % column 4 behavioral file

        % 18 Accuracy correct or not?
        this.data.new_out(:,18) =   this.data.results.output(:,5); % column 5 behavioral file

        % 19 RT
        this.data.new_out(:,19) =   this.data.results.output(:,6); % column 6 behavioral file

        % Response Types: correct reject, false_alarm, hit, miss
            % Misses and correct reject don't mean the same thing for the 2-interval 2AFC type of task
            % Hit               = Signal A, Response A 
            % False Alarm       = Signal A, Response B
            % 'Miss'            = Signal B, Response A
            % 'Correct Reject'  = Signal B, Response B
            % Just pick arbitrarily that A = up/90, B = down/270

        % 20 Correct reject
        this.data.new_out(:,20) =  this.data.results.output(:,3) == 270 & this.data.results.output(:,4) == 270;
        % 21 False alarm
        this.data.new_out(:,21) =  this.data.results.output(:,3) == 270 & this.data.results.output(:,4) == 90;
        % 22 Hit
        this.data.new_out(:,22) =  this.data.results.output(:,3) == 90 & this.data.results.output(:,4) == 90;
        % 23 Miss
        this.data.new_out(:,23) =  this.data.results.output(:,3) == 90 & this.data.results.output(:,4) == 270;

        % 24 Right Hand?
            % if setup.counterbalancing = 1 left is up/90, right is down/270
            % if setup.counterbalancing = 0 right is up/90, left is down/
        if this.data.setup.counterbalancing == 1
            this.data.new_out(:,24) = this.data.results.output(:,4) == 270;
        elseif this.data.setup.counterbalancing == 0
            this.data.new_out(:,24) = this.data.results.output(:,4) == 90;
        else
            disp('warning: check counterbalancing!');
        end

        % 25 Omission (no response from participant)
        this.data.new_out(:,25) = isnan(this.data.results.output(:,4));

        % Timing
        % Relative to first pulse
        % get this from phase information (actually timing)
        
        % interstimulus intervals
        this.data.new_out(:,26) = this.data.setup.pupilreboundtime1; %26 isi
        this.data.new_out(:,27) = this.data.setup.pupilreboundtime2; %27 ITI

        % Pupil
        
        % Save this.data.new_output to another variable
        % NOT preallocating. This is the safest way to do this, although
        % not the 'most efficient', but it only takes a minute anyway.
        ALL = [ ALL; this.data.new_out];
        
        disp('PP'); disp(this.data.setup.participant);
        disp('Session'); disp(this.data.setup.session);
        disp('Run'); disp(this.data.setup.run);
        
        clear this;
        end % k run loop
        cd ..;cd ..; 
     end % j sessions loop
     cd ..; % go back to 
end % i subjects loop

LCDec2.behav.data    = ALL(2:end,:); % Remove first row, placeholder for first concatenation
LCDec2.behav.headers = output_headers;

cd(path_analyses);

save('LCDec2_3T.mat','LCDec2') 
csvwrite('LCDec2_3T.csv',LCDec2.behav.data)
disp('Finished!');

