% Replace Strings in EyeLink MSG files for compatibility with Python Pipeline
% IRF task
% O. Colizoli June 2017

% If used, please cite: 
% Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
% Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018). 

% (1) Add trial start/stop and numbers (start with 0, not 1)
% (2) Add parameters 
% (3) Add phases 1 for sound, 2 for response

close all; clc;
cd('measure_irf/pupil_measureIRF');

home = pwd; 

rename = 1;

%% REPLACEMENTS
% Replace parameter lines
sound_param = 'sound at';
response_param = 'response at';
% Sound
% trial 0 started at 
% trial 0 phase 1 started at
% trial 0 parameter sound : 1 
% Response
% trial 0 phase 2 started at 
% trial 0 parameter response : 1 
% trial 0 stopped at


%% Go through file structure
folders = dir;
folders = folders([folders.isdir]); % get only folders
folders(strncmp({folders.name}, '.', 1)) = []; % take out the hidden folders with dots

for a = 1:length(folders)
    subj = folders(a).name;
    cd(subj);
    cd('raw');
    msgs = dir('measureIRF_*.msg'); % original message
    % in alphabetical order!
    
    if rename
        for b=1:length(msgs)
            fin = msgs(b).name; % file in
            [pathstr, name, ext] = fileparts(fin);
            movefile(fin, [name '_old.msg']); % rename original file to '_old'
        end
    end
    
    omsgs = dir('measureIRF_*_old.msg'); % old messages
    
    for c=1:length(omsgs)
        fin = omsgs(c).name; % file in
        [pathstr, name, ext] = fileparts(fin);
        fout = strrep(fin, '_old', ''); % replace with this

        trial_count = 0; % keep track of number of trials
        
        % search each line in MSG file
        fid1=fopen(fin); % old
        fid2=fopen(fout, 'wt'); % new with same name
        while 1
            s = fgetl(fid1); % get line as string s
            % Sound
            if ~isempty(strfind(s,sound_param))
                [token,remain] = strtok(s);
                [MSG,remain] = strtok(remain);
                % msg = s(5:13); % to get msg number
                line2 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count) ' started at 0.0 trigger None'];             % trial 0 started at 
                line3 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count) ' phase 1 started at 0.0 trigger None'];     % trial 0 phase 1 started at
                line4 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count) ' parameter sound : 1'];    % trial 0 parameter sound : 1 
                replacement = [s '\n' line2 '\n' line3 '\n' line4];
                s = strrep(s, s, replacement); % replace with this
                trial_count = trial_count + 1;
            % Response
            elseif ~isempty(strfind(s,response_param))
                [token,remain] = strtok(s);
                [MSG,remain] = strtok(remain);
                % msg = s(5:13); % to get msg number
                line2 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count-1) ' phase 2 started at 0.0 trigger None'];     % trial 0 phase 1 started at
                line3 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count-1) ' parameter response : 1']; % trial 0 parameter response : 1 
                line4 = ['MSG\t' num2str(MSG) '\t' 'trial ' num2str(trial_count-1) ' stopped at 0.0 trigger None'];             % trial 0 stopped at 
                replacement = [s '\n' line2 '\n' line3 '\n' line4];
                s = strrep(s, s, replacement); % replace with this      
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
    cd ..; cd ..;% get back to folder with subjects
end % a loop
cd(home);
  