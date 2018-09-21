% Rename MSG files for 'processed/eye' folder
% Important for pupil data in HD5 format in pupil_2AFC
% O. Colizoli Jan 2017

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

% Run after MSG_FindReplace.m AND MSG_insert_parameters.
% Then see:
% copy_fixed_msgs, from the first_level.py script

clear all; close all; clc;

rname = true; % rename detection to P_s_r.edf
rmove = false;  % remove _old.msg files

path_analyses = 'analysis';
path_raw = 'data/pupil_2AFC';

subjects = 15;
sessions = 4;
runs     = 6;
trials   = 25;

% see subjects file in raw data folder for python-matlab subject numbers
subj_initials = {'sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15'};
subj_no = [5, 3, 2, 4, 11, 12, 9, 15, 1, 7, 14, 10, 13, 8, 6];
% nr_sessions = [4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4,];
% nr_runs = [24, 22, 24, 18, 24, 24, 24, 24, 24, 23, 23, 18, 24, 24, 24];

%% !! Keep the MSG files in the correct order for missing runs

load('EDForder.mat')

cd(path_raw);

%% Rename detection files
if rname
    % Loop over subjects
    for a = 1:length(subj_initials)
        this.subj    = subj_initials{a};
        this.subj_no = subj_no(a);
        % make sure the subject initials are matched to the subject numbers
        cd(this.subj);
        
        for b=1:sessions*runs
            oname = ['2AFC_' num2str(edforder(this.subj_no,b)) '_' num2str(edforderSession(this.subj_no,b)) '.msg']; % file in
            if exist(oname, 'file')
                nname = ['P' num2str(this.subj_no) '_s' num2str(edforderSession(this.subj_no,b)) '_r' num2str(edforderRuns(this.subj_no,b)) '.msg'];
                copyfile(oname, nname); 
                disp(this.subj); disp(this.subj_no); disp(edforderSession(this.subj_no,b)); disp(edforderRuns(this.subj_no,b));
       
            end
        end
    cd ..; % get back to folder with subjects
    end
    
    
    
    
end



%% Remove other unnecessary files  
if rmove
    % Loop over subjects
    for a = 1:length(subj_initials)
        this.subj    = subj_initials{a};
        this.subj_no = subj_no(a);
        % make sure the subject initials are matched to the subject numbers
        cd(this.subj);
        
        disp(this.subj);
        delete('2AFC_*_old.msg'); % original message

        cd ..; % get back to folder with subjects
    end
end



