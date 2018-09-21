function filterDotsOlympia(filename, save_data_dir, save_pdf_dir)
% Anne Urai, 2018

% get this code https://github.com/anne-urai/motionEnergy
addpath('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/Tobi/2AFC_LCDecisions/Pupil paper 1/Anne/anne-urai-motionEnergy-39b6500');
addpath('/Volumes/OLY 2TB Dropbox Sync/Sync/SYNCBOX/WORK/MatlabScripts/fieldtrip-20180517');
ft_defaults;

if ~exist('filename', 'var'), filename = '2AFC_example.mat'; end
load(filename, 'stim','dots','results','window1','setup');

% avoid window UI error
display.dist        = window1.dist;
display.res         = window1.res;
display.width       = window1.width;
display.frameRate   = window1.frameRate;
display.center      = window1.center;
display.ppd         = deg2pix(display, 1);
coord               = stim; clear stim;

% make sure the framerate matches the nr of dot frames, 750 ms dots
assert(abs(0.75 - size(coord, 3) / display.frameRate) < 0.02, ...
    'frameRate in dots and behav does not match!');

% ==================================================================
% BUILD FILTERS
% ==================================================================

% temporal range of the filter
cfg            = [];
cfg.frameRate  = display.frameRate;
cfg.ppd        = display.ppd;

% k = 60, from Kiani et al. 2008
cfg.k = 60;

% adjust spatial filters to match the speed in the dots
effectiveSpeed = pix2deg(display, dots.speed) ./ dots.nvar;

% Kiani et al. 2008 has a speed of 2.84 deg/s and used sigma_c and sigma_g
% as 0.35 (not explicitly mentioned in their paper). To optimally scale the
% filters for the speed in our dots, multiply the spatial parameters
% see email exchange with Klaus Wimmer
cfg.sigma_c = 0.35 * (effectiveSpeed / 2.84);
cfg.sigma_g = 0.35 * (effectiveSpeed / 2.84);

% equations exactly as in Kiani et al. 2008
[f1, f2] = makeSpatialFilters(cfg);
[g1, g2] = makeTemporalFilters(cfg);

% ==================================================================
% FILTER EACH TRIAL
% ==================================================================

clear data;
ntrials         = size(coord, 2);
data.trial      = nan(ntrials, size(coord, 3));

for t = 1:ntrials,
    
    % GET DOT COORDINATES FOR THIS TRIAL
    thiscoord = squeeze(coord(1, t, :, :, :));
    
    % check that we have no NaNs left
    assert(~any(isnan(thiscoord(:))));
    
    % change coordinates to movie
    % always make the dots go up, that way will get the opponent
    % energy for up-down
    thisstim = coord2stim(display, thiscoord, 90);
    
    % filters
    motionenergy = applyFilters(thisstim, f1, f2, g1, g2);
    
    % also save all the energy summed across space
    data.trial(t, :) = squeeze(sum(sum(motionenergy)));
    
end

% time axis
data.time = 0 : 1/display.frameRate : (size(motionenergy, 3) - 1)/display.frameRate;
assert(numel(data.time) == size(thisstim, 3));

% ==================================================================
% SANITY CHECK
% ==================================================================

% for the last one, check that this worked;
singletrial_motionenergy = nanmean(data.trial, 2);
roc = rocAnalysis(singletrial_motionenergy(dots.direction == 270), ...
    singletrial_motionenergy(dots.direction == 90), 0, 0);
if roc.i < 0.9,
    warning('motion energy does not separate stimulus types');
end

% save this block
motionenergy = data;

% ==================================================================
% ADD BEHAVIORAL VARIABLES
% ==================================================================

% when direction  = 90, stimulus = -1
% when direction  = 270, stimulus = 1
behav = array2table([sign(dots.direction - 100)' dots.coherence' ...
    sign(results.response - 100)' ...
    results.correct' results.RT', transpose(1:length(results.response))], ...
    'variablenames', ...
    {'stimulus', 'coherence', 'response', 'correct', 'RT', 'trialnum'});
behav.subj_idx      = setup.participant *ones(size(behav.response));
behav.session       = setup.session *ones(size(behav.response));
behav.block         = setup.run *ones(size(behav.response));

% optional; change behavioral struct to a table, easier to work with
% (requires one of the more recent Matlab versions)
behav               = table2struct(behav);

% save to a meaningful filename
this_results = sprintf('2AFC_motionFiltered_%s', filename); % name of output file
resultsFile = [save_data_dir '/' this_results];
save(resultsFile, 'motionenergy', 'behav');
disp(resultsFile);

% ==================================================================
% MAKE A SANITY CHECK PLOT
% ==================================================================

cohs = cell2mat({behav.stimulus}) .* cell2mat({behav.coherence});
cohlevels = unique(cohs);
colors = parula(length(cohlevels));
figure; hold on;
for c = 1:length(cohlevels),
    plot(data.time, data.trial(cohs == cohlevels(c), :), 'color', colors(c, :));
end

% save figure
[filepath,name,ext] = fileparts(filename);
this_pdf = sprintf('2AFC_motionFiltered_%s', name); % name of output file
pdfFile = [save_pdf_dir '/' this_pdf];
saveas(gcf, pdfFile, 'pdf')

end