#!/usr/bin/env python
# encoding: utf-8
"""
================================================
pupil_preprocessing_control.py

If used, please cite: 
Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018).
================================================
"""

import os
import sys
import datetime
import pickle
import math
import numpy as np
import scipy as sp
import scipy.stats as stats
import matplotlib
import matplotlib.pyplot as plt
import pylab

import seaborn as sns
import pandas as pd
import numpy.linalg as LA
import bottleneck as bn
import glob
from joblib import Parallel, delayed
import itertools
from itertools import chain
import logging
import logging.handlers
import logging.config

import copy

from IPython import embed as shell

sys.path.append(os.environ['ANALYSIS_HOME'])
from Tools.log import *
from Tools.Operators import ArrayOperator, EDFOperator, HDFEyeOperator, EyeSignalOperator
from Tools.Operators.EyeSignalOperator import detect_saccade_from_data
from Tools.Operators.CommandLineOperator import ExecCommandLine
from Tools.other_scripts.plotting_tools import *
from Tools.other_scripts.circularTools import *
from Tools.other_scripts import functions_jw as myfuncs
from Tools.other_scripts import functions_jw_GLM as GLM

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
sns.set(style='ticks', font='Arial', font_scale=1, rc={
    'axes.linewidth': 0.25, 
    'axes.labelsize': 7, 
    'axes.titlesize': 7, 
    'xtick.labelsize': 6, 
    'ytick.labelsize': 6, 
    'legend.fontsize': 6, 
    'xtick.major.width': 0.25, 
    'ytick.major.width': 0.25,
    'text.color': 'Black',
    'axes.labelcolor':'Black',
    'xtick.color':'Black',
    'ytick.color':'Black',} )
sns.plotting_context()

class pupilPreprocessSession(object):
    """pupilPreprocessing"""
    def __init__(self, subject, experiment_name, experiment_nr, version, project_directory, loggingLevel = logging.DEBUG, sample_rate_new = 50):
        self.subject = subject
        self.experiment_name = experiment_name
        self.experiment = experiment_nr
        self.version = version
        try:
            os.mkdir(os.path.join(project_directory, experiment_name))
            os.mkdir(os.path.join(project_directory, experiment_name, self.subject.initials))
        except OSError:
            pass
        self.project_directory = project_directory
        self.base_directory = os.path.join(self.project_directory, self.experiment_name, self.subject.initials)
        self.create_folder_hierarchy()
        self.hdf5_filename = os.path.join(self.base_directory, 'processed', self.subject.initials + '.hdf5')
        self.ho = HDFEyeOperator.HDFEyeOperator(self.hdf5_filename)
        self.velocity_profile_duration = self.signal_profile_duration = 100
        self.loggingLevel = loggingLevel
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.loggingLevel)
        addLoggingHandler(logging.handlers.TimedRotatingFileHandler(os.path.join(self.base_directory, 'log', 'sessionLogFile.log'), when='H', delay=2, backupCount=10), loggingLevel=self.loggingLevel)
        loggingLevelSetup()
        for handler in logging_handlers:
            self.logger.addHandler(handler)
        
        self.logger.info('starting analysis in ' + self.base_directory)
        self.sample_rate_new = int(sample_rate_new)
        self.downsample_rate = int(1000 / sample_rate_new)
        
    def create_folder_hierarchy(self):
        """createFolderHierarchy does... guess what."""
        this_dir = self.project_directory
        for d in [self.experiment_name, self.subject.initials]:
            try:
                this_dir = os.path.join(this_dir, d)
                os.mkdir(this_dir)
            except OSError:
                pass

        for p in ['raw',
         'processed',
         'figs',
         'log']:
            try:
                os.mkdir(os.path.join(self.base_directory, p))
            except OSError:
                pass
    
    def delete_hdf5(self):
        os.system('rm {}'.format(os.path.join(self.base_directory, 'processed', self.subject.initials + '.hdf5')))
    
    def import_raw_data(self, edf_files, aliases):
        """import_raw_data loops across edf_files and their respective aliases and copies and renames them into the raw directory."""
        for (edf_file, alias,) in zip(edf_files, aliases):
            self.logger.info('importing file ' + edf_file + ' as ' + alias)
            ExecCommandLine('cp "' + edf_file + '" "' + os.path.join(self.base_directory, 'raw', alias + '.edf"'))
    
    def convert_edfs(self, aliases):
        for alias in aliases:
            self.ho.add_edf_file(os.path.join(self.base_directory, 'raw', alias + '.edf'))
        
    def import_all_data(self, aliases):
        """import_all_data loops across the aliases of the sessions and converts the respective edf files, adds them to the self.ho's hdf5 file. """
        for alias in aliases:
            self.ho.add_edf_file(os.path.join(self.base_directory, 'raw', alias + '.edf'))
            self.ho.edf_message_data_to_hdf(alias=alias)
            self.ho.edf_gaze_data_to_hdf(alias=alias) # ERROR
    
    def compute_omission_indices(self):
        # note blinks and saccades removed by deconvolution in import_all_data: self.ho.edf_gaze_data_to_hdf (HDFOperator calls EyeSignal Operator)
        self.omission_indices_sac = np.zeros(self.nr_trials, dtype=bool)
        self.omission_indices_blinks = np.zeros(self.nr_trials, dtype=bool)
        self.omission_indices = self.omission_indices_sac + self.omission_indices_blinks
    
    def trial_params(self):
        blinks_nr = np.zeros(self.nr_trials)
        number_blinks = np.zeros(self.nr_trials)
        for t in range(self.nr_trials):
            try:
                blinks_nr[t] = sum((self.blink_start_times > self.feedback_times[t]) * (self.blink_start_times < self.feedback_times[t]+1000))
            except:
                shell()
        sacs_nr = np.zeros(self.nr_trials)
        sacs_dur = np.zeros(self.nr_trials)
        sacs_vel = np.zeros(self.nr_trials)
        for t in range(self.nr_trials):
            saccades_in_trial_indices = (self.saccade_start_times > self.feedback_times[t] - 500) * (self.saccade_start_times < self.feedback_times[t] + 1500)
            sacs_nr[t] = sum(saccades_in_trial_indices)
            sacs_dur[t] = sum(self.saccade_durs[saccades_in_trial_indices])
            if sacs_nr[t] != 0:
                sacs_vel[t] = max(self.saccade_peak_velocities[saccades_in_trial_indices])
        

        run_nr = int(self.alias.split('_')[-2])
        session_nr = int(self.alias.split('_')[-1])
        self.parameters['omissions'] = self.omission_indices
        self.parameters['omissions_sac'] = self.omission_indices_sac
        self.parameters['omissions_blinks'] = self.omission_indices_blinks
        self.parameters['blinks_nr'] = blinks_nr
        self.parameters['sacs_nr'] = sacs_nr
        self.parameters['sacs_dur'] = sacs_dur
        self.parameters['sacs_vel'] = sacs_vel
        self.parameters['trial'] = np.arange(self.nr_trials)
        self.parameters['run'] = run_nr
        self.parameters['session'] = session_nr
        self.ho.data_frame_to_hdf(self.alias, 'parameters2', self.parameters)
        
        print '{} total trials'.format(self.nr_trials)
        print '{} omissions'.format(sum(self.omission_indices))
        print ''
    
            
    def process_runs(self, alias, artifact_rejection='strict', create_pupil_BOLD_regressor=False):
        print 'subject {}; {}'.format(self.subject.initials, alias)
        print '##############################'
        
        self.artifact_rejection = artifact_rejection
        
        # load data:
        self.alias = alias
        # self.events = self.ho.read_session_data(alias, 'events')
        self.parameters = self.ho.read_session_data(alias, 'parameters')
        self.nr_trials = len(self.parameters['trial_nr'])
        self.trial_times = self.ho.read_session_data(alias, 'trials')
        self.session_start = self.trial_times['trial_start_EL_timestamp'][0]
        self.trial_starts = np.array(self.trial_times['trial_start_EL_timestamp'])
        self.trial_ends = np.array(self.trial_times['trial_end_EL_timestamp'])
        self.phase_times = self.ho.read_session_data(alias, 'trial_phases')
        self.baseline_times = np.array(self.phase_times['trial_phase_EL_timestamp'][(self.phase_times['trial_phase_index'] == 1)])
        self.feedback_times = np.array(self.phase_times['trial_phase_EL_timestamp'][(self.phase_times['trial_phase_index'] == 2)])
        self.blink_data = self.ho.read_session_data(alias, 'blinks_from_message_file')
        self.saccade_data = self.ho.read_session_data(alias, 'saccades_from_message_file')
        self.blink_start_times = np.array(self.blink_data['start_timestamp'])
        self.blink_end_times = np.array(self.blink_data['end_timestamp'])
        self.saccade_start_times = np.array(self.saccade_data['start_timestamp'])
        self.saccade_end_times = np.array(self.saccade_data['end_timestamp'])
        self.saccade_durs = np.array(self.saccade_data['duration'])
        self.saccade_peak_velocities = np.array(self.saccade_data['peak_velocity'])
        self.eye = self.ho.eye_during_period((np.array(self.trial_times['trial_start_EL_timestamp'])[0], np.array(self.trial_times['trial_end_EL_timestamp'])[-1]), self.alias)
        self.pupil_data = self.ho.data_from_time_period((np.array(self.trial_times['trial_start_EL_timestamp'])[0], np.array(self.trial_times['trial_end_EL_timestamp'])[-1]), self.alias)
        
        self.time = np.array(self.pupil_data['time'])
        self.pupil = np.array(self.pupil_data[(self.eye + '_pupil_bp_clean_psc')])
        self.gaze_x = np.array(self.pupil_data[(self.eye + '_gaze_x')])
        self.gaze_y = np.array(self.pupil_data[(self.eye + '_gaze_y')])
        
        self.compute_omission_indices()
        self.trial_params()
        if create_pupil_BOLD_regressor:
            self.create_pupil_BOLD_regressor()
        
    
    def process_across_runs(self, aliases, create_pupil_BOLD_regressor=False):
        # scalars:
        # pupil_b_feed is pupil baseline before feedback
        # pupil_d_feed is pupil dilation locked to feedback
        
        # load data:
        parameters = []
        pupil_BOLD_regressors = []
        bp_feed_bp = [] # baseline pupil
        tpr_feed_bp = [] # 1-2 secs
        for alias in aliases:
            parameters.append(self.ho.read_session_data(alias, 'parameters2'))
            if create_pupil_BOLD_regressor:
                pupil_BOLD_regressors.append(np.array(self.ho.read_session_data(alias, 'pupil_BOLD_regressors')))
            trial_times = self.ho.read_session_data(alias, 'trials')
            eye = self.ho.eye_during_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
            pupil_data = self.ho.data_from_time_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
            session_start = trial_times['trial_start_EL_timestamp'][0]
            pupil_bp = np.array(pupil_data[(eye + '_pupil_bp_clean_psc')])
            pupil_lp = np.array(pupil_data[(eye + '_pupil_lp_clean_psc')])
            time = np.array(pupil_data['time']) - session_start
            phase_times = self.ho.read_session_data(alias, 'trial_phases')
            feedback_times = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == 2)]) - session_start
            
            # baseline pupil measures:
            bp_feed_bp.append( np.array([np.mean(pupil_bp[(time>i-500)*(time<i)]) for i in feedback_times]) )
        
            # phasic pupil responses 
                # feedback interval [1, 2]
            tpr_feed_bp.append( np.array([np.mean(pupil_bp[(time>i+1000)*(time<i+2000)]) for i in feedback_times]) - bp_feed_bp[-1]  )
            
        # join over runs:
        parameters_joined = pd.concat(parameters)

        bp_feed_bp = np.concatenate(bp_feed_bp) # baseline pupil
        tpr_feed_bp = np.concatenate(tpr_feed_bp)        
        
        # add to dataframe and save to hdf5:
        parameters_joined['pupil_b_feed'] = bp_feed_bp
        parameters_joined['pupil_d_feed'] = tpr_feed_bp
        
        parameters_joined['subject'] = self.subject.initials
        self.ho.data_frame_to_hdf('', 'parameters_joined', parameters_joined)
    

  