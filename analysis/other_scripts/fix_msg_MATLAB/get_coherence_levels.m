% Get the coherence levels to determine easy/difficult trials per
% participant per run

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

clear all; close all; clc;

path_analyses = 'analysis';
path_raw = 'data/pupil_2AFC';
cd(path_raw);

subjects = 15;
sessions = 4;
runs     = 6;
trials   = 25;
% save output in MAT format (runs, diff/easy, session, PPNs)
% data.setup.cohlevel1 = difficult, data.setup.cohlevel2 = easy
cohlevels = nan(runs,2,sessions,subjects);
cohtrials = nan(trials,runs,sessions,subjects);

% Loop through subject folders, fMRI_session folders, go into AFC folder
folders = dir; % SUBJECTS
folders = folders([folders.isdir]); % get only folders
folders(strncmp({folders.name}, '.', 1)) = []; % take out the hidden folders with dots

for i = 1:subjects
     subj = folders(i).name;
     cd(subj);
     subj_folders = dir([subj '*']); % SESSIONS
     subj_folders = subj_folders([subj_folders.isdir]); % get only folders
     subj_folders(strncmp({subj_folders.name}, '.', 1)) = []; % take out the hidden folders with dots
     
     for j=1:length(subj_folders)
        session = subj_folders(j).name;
        cd(session);
        cd('behavior');
        MAT = dir('*.mat'); % SCANS/RUNS    
        
        for k=1:length(MAT)
            
            this.data = load(MAT(k).name);
            % data.setup.cohlevel1 = difficult, data.setup.cohlevel2 = easy
            % run = k, session = j, ppn = i
            cohlevels(k,1:2,j,i) = [this.data.setup.cohlevel1, this.data.setup.cohlevel2];
            cohtrials(:,k,j,i) = this.data.results.output(:,1);
            
            disp(this.data.setup.participant);


            clear this;
        end % k run loop
        cd ..;cd ..; 
     end % j sessions loop
     cd ..; % go back to 
end % i subjects loop

cd(path_analyses);
save('Coherence_Trials.mat', 'cohtrials','cohlevels');

