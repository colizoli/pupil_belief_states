% Compute correlation motion energy and coherence 2AFC data 
% Data is local on my laptop
% Run from '~WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500'
% Results will end up in the above folder then ~/save_data/group
% O. Colizoli, 2018

clear all; close all; clc;

% get this code https://github.com/anne-urai/motionEnergy
addpath('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500');

subjects = 15; % 3T subjects only
runs = 24;
trials = 25;

% analysis scripts and data paths
home = '/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500'; 
save_data_dir = [home '/save_data'];
save_pdf_dir = [home '/save_data/pdfs'];
cd(save_data_dir);

% cd('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/RESULTS_RAWDATA');
% raw_data = pwd;

%% start loop

coh_data = []; % coherence per trial
me_data =[]; % mean motion energy per trial
me_data_var = []; % std of motion energy per trial

save_subj = [];
save_session = [];
save_run = [];
save_trial = [];

MAT = dir('*.mat'); % All 
    
    for m = 1:length(MAT)
           
        load(MAT(m).name);
        
        % when direction  = 90 (up), stimulus = -1
        % when direction  = 270 (down), stimulus = 1
        % so need to flip behav.stimulus
        direction = [behav.stimulus].*-1;
        
        me_data = [me_data; mean(transpose(motionenergy.trial(:,2:91)))'];
        me_data_var = [me_data_var; std(transpose(motionenergy.trial(:,2:91)))'];
        coh_data = [coh_data; [[behav.coherence].*[direction]]'];  % get direction as well as coherence
        
        save_subj = [save_subj; cell2mat({behav.subj_idx})']; 
        save_session = [save_session; cell2mat({behav.session})'];
        save_run = [save_run; cell2mat({behav.block})'];
        save_trial = [save_trial; cell2mat({behav.trialnum})'];
            
    end % MAT

% Output to match trials to python dataframe

outdata = [save_subj, save_session, save_run, save_trial, me_data, coh_data];

csvwrite('motion_energy.csv', outdata);

%% group motion energy by coherence levels

coh_unique = unique(coh_data);
me_means = []; % mean motion energy per unique coh level
me_vars = []; % mean std motion energy per unique coh level

    for c = 1:length(coh_unique)
        % get mean motion energy
        idx = ismember(coh_data(:,1),coh_unique(c));
        this_me = me_data(idx); % mean motion energy
        this_var = me_data_var(idx); % std
        
        me_means = [me_means; mean(this_me) ];
        me_vars = [me_vars; mean(this_var) ];

    end % c

%% Plotting

figure;
x = coh_unique*100;
y = me_means;
%plot(x, me_means);
scatter(x,y,20,'fill'); %scatter(x,y,20,g,'fill');
[r,pval] = corr(x,y,'type', 'Pearson');

title(['r = ' num2str(r) ', p = ' num2str(pval)]);
xlabel('Motion coherence (%)','FontSize',14);
ylabel('Motion energy (a.u.)','FontSize',14);
set(gca ,'TickDir','out'); % or 'out'
set(gca, 'LineWidth', 2);
set(findall(gcf,'type','text'),'FontName', 'Arial', 'FontSize', 20);
set(findall(gcf,'type','axes'),'FontName', 'Arial', 'FontSize', 20);      



