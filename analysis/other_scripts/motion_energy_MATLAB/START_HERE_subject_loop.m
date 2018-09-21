% Run loop across 2AFC data to do motion filtering
% Data is local on my laptop
% Run from '~WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500'
% Results will end up in the above folder then ~/save_data/pdfs
% O. Colizoli, 2018

clear all; close all; clc;

% get this code https://github.com/anne-urai/motionEnergy
addpath('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500');

subjects = 15; % 3T subjects only

% analysis scripts and data paths
home = '/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500'; 
save_data_dir = [home '/save_data'];
save_pdf_dir = [home '/save_data/pdfs'];

cd('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/RESULTS_RAWDATA');
raw_data = pwd;

%% start loop
folders = dir; % SUBJECTS
folders = folders([folders.isdir]); % get only folders
folders(strncmp({folders.name}, '.', 1)) = []; % take out the hidden folders with dots

    for i = 16:20
        subj = folders(i).name;
        cd(subj);
        subj_folders = dir([subj '*']); % SESSIONS
        subj_folders = subj_folders([subj_folders.isdir]); % get only folders
        subj_folders(strncmp({subj_folders.name}, '.', 1)) = []; % take out the hidden folders with dots
        
        for j=1:length(subj_folders) 
            session = subj_folders(j).name;
            cd(session);
            cd([subj '_AFC' num2str(j)]);
            MAT = dir('*.mat'); % SCANS
            
            for k=1:length(MAT) % RUNS
                mat_file = MAT(k).name;

                % check if exists, will be faster when have to start over
                if exist([save_data_dir '/2AFC_motionFiltered_' mat_file], 'file') == 0
                    % CALL MOTION ENERGY FILTER SCRIPT 
                    disp(['Filtering ' mat_file]);
                    filterDotsOlympia(mat_file, save_data_dir, save_pdf_dir);
                    close all;
                end % if exists
                
            end % k MAT
            cd ..;cd ..;
        end % j subj_folders
        cd ..;
    end % i subjects
cd(home);
        
