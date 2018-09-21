% Replace Strings in EyeLink MSG files for compatibility with Python Pipeline
% Important for pupil data in HD5 format in pupil_2AFC
% O. Colizoli Aug 2016

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

% Adds parameter for easy/difficult trials
% Difficult = 1 (cohlevel1)
% Easy = 2 (cohlevel2)
% Replaces coherence and RT values with NON scientific notation
% This script to be run AFTER MSG_FindReplace is run 

% Once this is run, do the following:
% (1) copy and replace 2AFC_ files into pupil_2AFC subject folders on lisa
% (2) delete old HDF5 files
% (3) rerun the following functions for pupil_2AFC folder in subjects.py:
% import_all_data, process_runs and process_across_runs,

% After MSG files are fixed run MSG_Rename

clear all; close all; clc;

rname = false; % rename _coh.msg to .msg
rmove = false;  % remove _coh.msg files

path_analyses = 'analysis';
path_raw = 'data/pupil_2AFC';

cd(path_analyses);
load('Coherence_Trials.mat'); % get_coherence_levels.m
load('RT_Trials.mat');        % get_RT.m
load('EDForder.mat');         % see raw/main_task

subjects = 15;
sessions = 4;
runs     = 6;
trials   = 25;
% reshape to trials x 24 runs x participant no.
cohtrials = reshape(cohtrials, [trials,sessions*runs,subjects]);
RTs  = reshape(RTs, [trials,sessions*runs,subjects]);

cd(path_raw);

%% see subjects file in raw data folder for python-matlab subject numbers
subj_initials = {'sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15'};
subj_no = [5, 3, 2, 4, 11, 12, 9, 15, 1, 7, 14, 10, 13, 8, 6];
%nr_sessions = [4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4,]
% nr_runs = [24, 22, 24, 18, 24, 24, 24, 24, 24, 23, 23, 18, 24, 24, 24];

% Keep the MSG files in the correct order for missing runs
% Saved the following, use: load('EDForder.mat')

% edforder = repmat(1:24,[15,1]);
% 
% % sub-02 remove session2 run5, session2 run6
% cohtrials(:,11:12,subj_no(strcmp(subj_initials,'sub-02'))) = NaN;
% edforder(subj_no(strcmp(subj_initials,'sub-02')),11:12) = NaN; 
% edforder(subj_no(strcmp(subj_initials,'sub-02')),13:24) = 11:22; 
% % sub-04 remove all session1
% cohtrials(:,1:6,subj_no(strcmp(subj_initials,'sub-04'))) = NaN;
% edforder(subj_no(strcmp(subj_initials,'sub-04')),1:6) = NaN; 
% edforder(subj_no(strcmp(subj_initials,'sub-04')),7:24) = 1:18; 
% % sub-10 remove session1 run6
% cohtrials(:,6,subj_no(strcmp(subj_initials,'sub-10'))) = NaN;
% edforder(subj_no(strcmp(subj_initials,'sub-10')),6) = NaN; 
% edforder(subj_no(strcmp(subj_initials,'sub-10')),7:24) = 6:23; 
% % sub-11 remove session1 run6
% cohtrials(:,6,subj_no(strcmp(subj_initials,'sub-11'))) = NaN;
% edforder(subj_no(strcmp(subj_initials,'sub-11')),6) = NaN; 
% edforder(subj_no(strcmp(subj_initials,'sub-11')),7:24) = 6:23; 
% % sub-12 remove all session1
% cohtrials(:,1:6,subj_no(strcmp(subj_initials,'sub-12'))) = NaN;
% edforder(subj_no(strcmp(subj_initials,'sub-12')),1:6) = NaN; 
% edforder(subj_no(strcmp(subj_initials,'sub-12')),7:24) = 1:18; 

%% REPLACEMENTS

% Trial numbers with trial-1 (should start with 0)
% NOTE: the space after the trial number is crucial!

find_trial_coh = {'trial 0 parameter coherence','trial 1 parameter coherence','trial 2 parameter coherence','trial 3 parameter coherence',... 
    'trial 4 parameter coherence','trial 5 parameter coherence','trial 6 parameter coherence','trial 7 parameter coherence',... 
    'trial 8 parameter coherence','trial 9 parameter coherence','trial 10 parameter coherence' 'trial 11 parameter coherence',... 
    'trial 12 parameter coherence','trial 13 parameter coherence','trial 14 parameter coherence','trial 15 parameter coherence',... 
    'trial 16 parameter coherence','trial 17 parameter coherence','trial 18 parameter coherence','trial 19 parameter coherence',...
    'trial 20 parameter coherence','trial 21 parameter coherence','trial 22 parameter coherence','trial 23 parameter coherence','trial 24 parameter coherence'};

trial_diff = {'trial 0 parameter difficulty','trial 1 parameter difficulty','trial 2 parameter difficulty','trial 3 parameter difficulty',... 
    'trial 4 parameter difficulty','trial 5 parameter difficulty','trial 6 parameter difficulty','trial 7 parameter difficulty',... 
    'trial 8 parameter difficulty','trial 9 parameter difficulty','trial 10 parameter difficulty' 'trial 11 parameter difficulty',... 
    'trial 12 parameter difficulty','trial 13 parameter difficulty','trial 14 parameter difficulty','trial 15 parameter difficulty',... 
    'trial 16 parameter difficulty','trial 17 parameter difficulty','trial 18 parameter difficulty','trial 19 parameter difficulty',...
    'trial 20 parameter difficulty','trial 21 parameter difficulty','trial 22 parameter difficulty','trial 23 parameter difficulty','trial 24 parameter difficulty'};

find_trial_rt = {'trial 0 parameter RT','trial 1 parameter RT','trial 2 parameter RT','trial 3 parameter RT',... 
    'trial 4 parameter RT','trial 5 parameter RT','trial 6 parameter RT','trial 7 parameter RT',... 
    'trial 8 parameter RT','trial 9 parameter RT','trial 10 parameter RT' 'trial 11 parameter RT',... 
    'trial 12 parameter RT','trial 13 parameter RT','trial 14 parameter RT','trial 15 parameter RT',... 
    'trial 16 parameter RT','trial 17 parameter RT','trial 18 parameter RT','trial 19 parameter RT',...
    'trial 20 parameter RT','trial 21 parameter RT','trial 22 parameter RT','trial 23 parameter RT','trial 24 parameter RT'};

    
%% Go through file structure on lisa
% VERY IMPORTANT TO MATCH SUBJECT INITIALS TO SUBJECT NUMBER

% Loop over subjects
for a = 1:length(subj_initials)
    this.subj    = subj_initials{a};
    this.subj_no = subj_no(a);
    % make sure the subject initials are matched to the subject numbers
    cd(this.subj);
    
    % Loop over all runs
    for b=1:sessions*runs
        
        disp('Subject: '); disp(this.subj); 
        disp('Subject Number: ');disp(this.subj_no); 
        disp('Run: '); disp(b);
        
        this.msg     = edforder(this.subj_no,b);
        this.session = edforderSession(this.subj_no,b);
        disp('This MSG: '); disp(this.msg);

        % Check if missing run and skip if so
        if ~isnan(this.msg)
            
            fin = ['2AFC_' num2str(this.msg) '_' num2str(this.session) '.msg']; % file in
            [pathstr, name, ext] = fileparts(fin);
            fout = strrep(fin, fin, ['2AFC_' num2str(this.msg) '_' num2str(this.session) '_coh.msg']); % replace with this

            % search each line in MSG file
            fid1=fopen(fin);
            fid2=fopen(fout, 'wt');
            while 1
                s = fgetl(fid1); % get line as string s
                % disp(s);

                % Loop over trials
                % Find parameter coherence lines
                for i = 1:trials
                    
                    % disp('Trial: '); disp(i);

                    % REPLACE COHERENCE & ADD DIFFICULTY PARAMETER if there is a match!
                    if ~isempty(strfind(s,find_trial_coh{i}))                       
                        % determine difficulty level for this participant's trial
                        % (trial, run, subj)
                        this.easy = max(cohtrials(:,b,this.subj_no));
                        this.hard = min(cohtrials(:,b,this.subj_no));
                            % Difficult = 1 (cohlevel1)
                            % Easy = 2 (cohlevel2)
                        if cohtrials(i,b,this.subj_no) == this.hard
                            this.level = 1;
                        elseif cohtrials(i,b,this.subj_no) == this.easy
                            this.level = 2;
                        end
                        % get MSG out of string
                        [token,remain] = strtok(s);
                        [MSG,remain] = strtok(remain);
                        news1 = ['MSG\t' num2str(MSG) '\t'  find_trial_coh{i} ' : ' num2str(cohtrials(i,b,this.subj_no))];
                        news2 = ['MSG\t' num2str(MSG) '\t'  trial_diff{i} ' : ' num2str(this.level)];
                        s = strrep(s, s, [news1 '\n' news2 ]); % replace with this      
                    end % strfind
                    
                    % REPLACE RT
                    if ~isempty(strfind(s,find_trial_rt{i}))                       
                        % determine difficulty level for this participant's trial
                        % (trial, run, subj)
                        this.RT = RTs(i,b,this.subj_no);
                        % get MSG out of string
                        [token,remain] = strtok(s);
                        [MSG,remain] = strtok(remain);
                        news = ['MSG\t' num2str(MSG) '\t'  find_trial_rt{i} ' : ' num2str(RTs(i,b,this.subj_no))];                        
                        s = strrep(s, s, news); % replace with this       
                    end % strfind
                end % i trials loop

                % stop while loop at end of text file
                if ~ischar(s), break;
                else
                    fprintf(fid2,[s '\n']); % print replacement to output file
                end
            end % while
            fclose(fid1);         
            fclose(fid2);
        else
            disp('Skipping: '); 
            disp('Subject: '); disp(this.subj); 
            disp('Subject Number: ');disp(this.subj_no); 
            disp('Run: '); disp(b);
        end % if check missing run
    end % b loop
    clear this;
    cd ..; % get back to folder with subjects
end % a loop

cd(path_analyses);


%% Rename files

if rname
    cd(path_raw);
    % Loop over subjects
    for a = 1:length(subj_initials)
        this.subj    = subj_initials{a};
        this.subj_no = subj_no(a);
        % make sure the subject initials are matched to the subject numbers
        cd(this.subj);
        
        for b=1:sessions*runs
            oname = ['2AFC_' num2str(edforder(this.subj_no,b)) '_' num2str(edforderSession(this.subj_no,b)) '_coh.msg']; % file in
            if exist(oname, 'file')
                %[pathstr, name, ext] = fileparts(fin);
                nname = ['2AFC_' num2str(edforder(this.subj_no,b)) '_' num2str(edforderSession(this.subj_no,b)) '.msg'];
                    % movefile('oldname.m','newname.m')
                movefile(oname, nname); 
            end
        end
    cd ..; % get back to folder with subjects
    end
end

%% Remove _coh.msg files

if rmove
    % Loop over subjects
    for a = 1:length(subj_initials)
        this.subj    = subj_initials{a};
        this.subj_no = subj_no(a);
        % make sure the subject initials are matched to the subject numbers
        cd(this.subj);
        
        delete('2AFC_*_coh.msg'); % original message

        cd ..; % get back to folder with subjects
    end
end
