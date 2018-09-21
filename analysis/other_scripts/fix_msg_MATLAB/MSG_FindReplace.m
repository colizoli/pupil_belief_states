% Replace Strings in EyeLink MSG files for compatibility with Python Pipeline
% O. Colizoli Feb 2016

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

% (1) Add colon to lines containing parameters
% (2) Trial number must start with 0, not 1
% (3) Missing a line before phase 1 for 'trial started at'

close all; clc;
cd('data/pupil_2AFC');

home = pwd; 

%% REPLACEMENTS
% Replace parameter lines
orig_param = {'parameter coherence','parameter hemifield','parameter direction','parameter answer'...
    'parameter correct','parameter RT','parameter arousal'};
rep_param = {'parameter coherence :','parameter hemifield :','parameter direction :','parameter answer :'...
    'parameter correct :','parameter RT :','parameter arousal :'};

% Replace trial numbers with trial-1 (should start with 0)
% NOTE: the space after the trial number is crucial!
orig_trial = {'trial 1 ','trial 2 ','trial 3 ','trial 4 ','trial 5 ','trial 6 ','trial 7 ','trial 8 ','trial 9 ','trial 10 ',...
    'trial 11 ','trial 12 ','trial 13 ','trial 14 ','trial 15 ','trial 16 ','trial 17 ','trial 18 ','trial 19 ','trial 20 ',...
    'trial 21 ','trial 22 ','trial 23 ','trial 24 ','trial 25 '};
rep_trial = {'trial 0 ','trial 1 ','trial 2 ','trial 3 ','trial 4 ','trial 5 ','trial 6 ','trial 7 ','trial 8 ','trial 9 ',...
    'trial 10 ' 'trial 11 ','trial 12 ','trial 13 ','trial 14 ','trial 15 ','trial 16 ','trial 17 ','trial 18 ','trial 19 ',...
    'trial 20 ','trial 21 ','trial 22 ','trial 23 ','trial 24 '};

% Before 'MSG	3612275.0   phase 1 started at', there needs to be another line that says
% 'MSG	3612275.0	trial 1 started at 2.999022e+04'
orig_phase = {'phase 1 started at'}; % don't need replacement strings, because just deleting portions of the original string
    
%% Go through file structure on lisa
folders = dir;
folders = folders([folders.isdir]); % get only folders
folders(strncmp({folders.name}, '.', 1)) = []; % take out the hidden folders with dots

for a = 1:length(folders)
    subj = folders(a).name;
    cd(subj);
    msgs = dir('2AFC_*.msg'); % original message
    % in alphabetical order!
    
    for b=1:length(msgs)
        fin = msgs(b).name; % file in
        [pathstr, name, ext] = fileparts(fin);
        movefile(fin, [name '_old.msg']); % rename original file to '_old'
    end

    omsgs = dir('2AFC_*_old.msg'); % old messages
    
    for c=1:length(omsgs)
        fin = omsgs(c).name; % file in
        [pathstr, name, ext] = fileparts(fin);
        fout = strrep(fin, '_old', ''); % replace with this

        % search each line in MSG file
        fid1=fopen(fin); % old
        fid2=fopen(fout, 'wt'); % new with same name
        while 1
            s = fgetl(fid1); % get line as string s
%             disp(s);
            % replace parameter lines with colon
            for i = 1:length(orig_param)
                if ~isempty(strfind(s,orig_param{i}))
                    s = strrep(s, orig_param{i}, rep_param{i}); % replace with this 
                end
            end
            % replace trial numbers with trialnum-1
            for j = 1:length(orig_trial)
                if ~isempty(strfind(s,orig_trial{j})) 
                    s = strrep(s, orig_trial{j}, rep_trial{j}); % replace with this 
                end
            end
            % add new line before phase 1 on each trial
            for k = 1:length(orig_phase)
                if ~isempty(strfind(s,orig_phase{k})) 
                    news = strrep(s, 'phase 1 ', ''); % replace with this 
                    news2 = strrep(news, 'trigger None', ''); % replace with this 
                    s = strrep(s, s, [news2 '\n' s ]); % replace with this       
                    %msg = str2double(s(5:13)); % to change msg number
                    %msg = num2str(msg-1);              
                    %s = strrep(s, s, ['MSG	' msg '\t' rep_phase{k} '\n' s ]); % replace with this 
                end
            end
            % stop while loop at end of text file
            if ~ischar(s), break;
            else
                fprintf(fid2,[s '\n']); % print replacement to output file
            end
        end % while
        fclose(fid1);         
        fclose(fid2);
    end % c loop
    cd ..; % get back to folder with subjects
end % a loop
cd(home);
  