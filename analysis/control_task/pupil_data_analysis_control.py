#!/usr/bin/env python
# encoding: utf-8
"""
================================================
pupil_data_analysis_control.py

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
import mne
import statsmodels.formula.api as sm

import pyvttbl as pt
from pyvttbl import SimpleHTML
from copy import deepcopy

from IPython import embed as shell

sys.path.append(os.environ['ANALYSIS_HOME'])
from Tools.Sessions import *
from Tools.Run import *
from Tools.Operators import *
from Tools.log import *
# from Tools.Operators import ArrayOperator, EDFOperator, HDFEyeOperator, EyeSignalOperator
# from Tools.Operators.EyeSignalOperator import detect_saccade_from_data
# from Tools.Operators.CommandLineOperator import ExecCommandLine
from Tools.other_scripts import functions_jw as myfuncs
from Tools.other_scripts import functions_jw_GLM as GLM

import functions_oc as ocf


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

############################################
# PUPIL functions first, then BOLD functions
############################################

class higherLevel(object):
    def __init__(self, subjects, experiment_name, project_directory):
        
        self.subjects = subjects
        self.nr_subjects = len(self.subjects)
        self.experiment_name = experiment_name
        self.project_directory = project_directory
        self.data_folder = os.path.join(project_directory, 'feedback', 'across')
        self.figure_folder = os.path.join(project_directory, 'figures')
        self.dataframe_folder = os.path.join(project_directory, 'data_frames')

        ##############################    
        # Define Conditions of Interest
        ##############################
        self.factors = [
            ['subj_idx'], # not for anova
            ['correct'],
        ] 
        self.csv_names = [
            'all', # not for anova
            'correct',
        ]
        
        self.time_locked = ['feed_locked']
        
        ##############################    
        # Pupil time series information:
        ##############################
        self.sample_rate = 1000
        self.downsample_rate = 100       # 50
        self.new_sample_rate = self.sample_rate / self.downsample_rate
        self.interval = 15 # determines size of kernel when * with sample rate
        # order is stim, feed, resp!
        self.pupil_step_lim = [[-2,13]]
        self.pupil_values = ['pupil_d']
        self.pupil_xlim = [[-0.5,3]] 
        self.pupil_time_of_interest = [[1,2]]
    

        
    def dataframe_pupil_subjects(self):
        #################################
        # pupil_b_feed is pupil baseline before feedback
        # pupil_d_feed is pupil dilation locked to feedback [1,2] s
        #################################
        
        #########
        # Get pupil data
        parameters_all = []
        for s in self.subjects:
            base_directory = os.path.join(self.project_directory, self.experiment_name, s)
            hdf5_filename = os.path.join(base_directory, 'processed', s + '.hdf5')
            ho = HDFEyeOperator.HDFEyeOperator(hdf5_filename)
            parameters_all.append(ho.read_session_data('', 'parameters_joined'))
        parameters_joined = pd.concat(parameters_all)

        ##############################
        # OMISSIONS 
        ##############################
        omissions = np.array(parameters_joined['omissions']) 
        # BLINKS
        for subj in np.unique(parameters_joined.subject):
            print round(np.mean(np.array((parameters_joined[parameters_joined.subject == subj]['blinks_nr'] > 0))), 3)
        
        ##############################
        # Always remove omissions BEFORE regressing out RT
        parameters_joined = parameters_joined[~omissions]
        # EVERYTHING UNDER HERE HAS OMISSIONS REMOVED

        # main effects
        correct = np.array(parameters_joined['feedback']) == 1 # green
        error = np.array(parameters_joined['feedback']) == 2 # red
        hemifield = np.array(parameters_joined['hemifield'])
        ITI = np.array(parameters_joined['ITI'])
        fixation = np.array(parameters_joined['fixation'])
        
        # pupil scalars - phasic scalars already have baseline removed pupil_preprocessing_control.process_across_runs()
        pupil_d_feed = np.array(parameters_joined['pupil_d_feed'])
        pupil_b_feed = np.array(parameters_joined['pupil_b_feed'])
        
        # indexing
        run = np.array(parameters_joined['run'], dtype=int)
        session = np.array(parameters_joined['session'], dtype=int)
        subj_idx_all = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
        
        # Creates a dataframe with all trial information for each subject in one large file
        # Note: omissions already removed        
        d = {
        'subj_idx' : pd.Series(subj_idx_all),
        'pupil_b_feed' : pd.Series(pupil_b_feed), # baseline before feedback
        'pupil_d_feed' : pd.Series(pupil_d_feed), # phasic locked to feedback
        'run' : pd.Series(run),
        'session' : pd.Series(session),
        'ITI' : pd.Series(np.array(ITI, dtype=float)),
        'fixation' : pd.Series(np.array(fixation, dtype=float)),
        'correct' : pd.Series(np.array(correct, dtype=int)),
        'error' : pd.Series(np.array(error, dtype=int)),
        'hemiL' : pd.Series(np.array(hemifield) == -1, dtype=int), # 1 = left, 0 = right
        # 'omissions' : pd.Series(np.array(omissions), dtype=int)
        }
        data_response = pd.DataFrame(d)    
        # SAVE DATAFRAME         
        data_response.to_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
        print('success: dataframe_pupil_subjects')
        
        
    def dataframe_pupil_event_related_subjects(self):
        # Cuts out time series of pupil data locked to time points of interest:
        # feed_locked
        # Outputs a numpy arrays corresponding to events, all trials for all subjects with omissions removed
        # Outputs 1 numpy array with the subject index
        
        ################################
        ## MAKE EVENT RELATED DATA FRAME
        ################################
        sample_rate = self.sample_rate
        downsample_rate = self.downsample_rate
        new_sample_rate = self.new_sample_rate
        interval = self.interval # determines size of kernel when * with sample rate
        
        # Get pupil data
        parameters_all = []
        for s in self.subjects:
            base_directory = os.path.join(self.project_directory, self.experiment_name, s)
            hdf5_filename = os.path.join(base_directory, 'processed', s + '.hdf5')
            ho = HDFEyeOperator.HDFEyeOperator(hdf5_filename)
            parameters_all.append(ho.read_session_data('', 'parameters_joined'))
        parameters_joined = pd.concat(parameters_all)
        
        # Define omissions for all subjects and all trials
        omissions = np.array(parameters_joined['omissions']) 
        
        # debug - will not work without 'self' probably overwriting variables
        self.run = np.array(parameters_joined['run'], dtype=int)
        self.session = np.array(parameters_joined['session'], dtype=int)
        self.subj_idx = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
                
        # all trials x events (all subjects at once), will be saved as numpy arrays
        trials_feedback = []    
        trials_subj_idx = []
        
        for i, s in enumerate(self.subjects):
            
            print i
            print s

            runs = np.unique(self.run[self.subj_idx == i])
            sessions = [self.session[self.subj_idx == i][self.run[self.subj_idx == i] == r][0] - 1 for r in runs] 
            # print runs
            # print sessions
            aliases = ['feedback_{}_{}'.format(run, session+1) for run, session in zip(runs, sessions)]
            base_directory = os.path.join(self.project_directory, self.experiment_name, s)
            hdf5_filename = os.path.join(base_directory, 'processed', s + '.hdf5')
            ho = HDFEyeOperator.HDFEyeOperator(hdf5_filename)
            # parameters_joined2.append(ho.read_session_data('', 'parameters_joined'))
            
            # load data:
            parameters = []     # run (24) x trials per run (25)
            pupil = []          # time series
            time = []           # time series
            feedback_times = [] # trials (600)
            blink_times = []
            time_to_add = 0
            # loops through runs across all the sessions of each subject
            for alias in aliases:
                parameters.append(ho.read_session_data(alias, 'parameters2'))
                # self.alias = alias
                trial_times = ho.read_session_data(alias, 'trials')
                eye = ho.eye_during_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
                pupil_data = ho.data_from_time_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
                session_start = trial_times['trial_start_EL_timestamp'][0]
                p = np.array(pupil_data[(eye + '_pupil_bp_clean_psc')]) # USE band-passed signal!
                p = p[~np.isnan(p)]
                pupil.append(p)
                ti = np.array(pupil_data['time']) - session_start
                time.append(ti + time_to_add)
                phase_times = ho.read_session_data(alias, 'trial_phases')
                
                feedback_t = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == 2)]) - session_start + time_to_add 
                
                feedback_times.append( feedback_t )
                
                blink_data = ho.read_session_data(alias, 'blinks_from_message_file')
                blink_times.append( np.array(blink_data['end_timestamp']) - session_start + time_to_add )
                time_to_add += ti[-1]
            
            parameters = pd.concat(parameters)
            pupil = np.concatenate(pupil)
            time = np.concatenate(time)
            feedback_times = np.concatenate(feedback_times) / 1000.0
            blink_times = np.concatenate(blink_times) / 1000.0
            
            # FOR FEEDBACK extract kernel for each trial, concate together with all subjects
            # event related averages:
            feedback_locked_array = np.zeros((len(feedback_times), interval*sample_rate))
            feedback_locked_array[:,:] = np.NaN
            
            # Cut out time series locked to events of interest
            # Subtract baseline pupil
            for j, t in enumerate(np.array(((feedback_times-2)*sample_rate), dtype=int)):
                feedback_locked_array[j,:len(pupil[t:t+(interval*sample_rate)])] = pupil[t:t+(interval*sample_rate)] - np.mean(pupil[t+1500:t+2000])
            
            # Add to dataframe   
            trials_feedback.append(feedback_locked_array)
            trials_subj_idx.append(self.subj_idx[self.subj_idx==i])
        
        # After all subjects are in, make one long list    
        trials_feedback = np.concatenate(np.array(trials_feedback))
        trials_subj_idx = np.concatenate(np.array(trials_subj_idx))
        
        # take out omissions
        trials_feedback = trials_feedback[~omissions]
        trials_subj_idx = trials_subj_idx[~omissions]
        
        # save as numpy arrays, easier than CSV files with 9,000 trials x 15,000 timepoints
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_feed_locked.npy'), trials_feedback)
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_subj_idx.npy'), trials_subj_idx)
    
        print('sucess: dataframe_pupil_event_related_subjects')
        
        
    def dataframe_pupil_event_related_higher(self):
        # Creates event related dataframes for the MEAN across subjects...
        # For each time_locked variable
        # Events (input) have already been baseline-subtracted on a trial-wise basis
        # Omissions have already been removed
        # Run after dataframe_pupil_event_related_subjects()
        # NEED TO SAVE SEPARATE DATAFRAMES FOR EACH COMBINATION OF IVS
                
        factors = deepcopy(self.factors) # deepcopy necessary for stopping backwards referencing of global
        k = self.interval*self.sample_rate # length of kernel
        
        # Loop across factors of interest
        for c,cond in enumerate(self.csv_names):
            g_idx = factors[c]
            # Add 'subj_idx' as first element of list here:
            if cond !='all':
                g_idx.insert(0, 'subj_idx') # get strings not list element
            for time,t in enumerate(self.time_locked):
                # Load numpy arrays containing time series events for all trials, all subjects
                a = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format(t)))
                b = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format('subj_idx')))

                # Read in subjects dataframe
                sdata = pd.read_csv(os.path.join(self.dataframe_folder, 'pupil','subjects','pupil_subjects.csv'))
                sdata.drop(['Unnamed: 0'], axis=1, inplace=True) # artifact of dataframe

                # Make sure that the trial numbers correspond before proceeding...
                if len(sdata) == len(a) == len(b):
                    tsdata = pd.DataFrame(a) # time series data convert to dataframe
                    sdata = pd.concat([tsdata, sdata],axis=1) # concatenate, order is important for selecting columns below
                    data = sdata
                    m = data.groupby(g_idx).mean() # means grouped by subject, then factors of interest
                    m = m.iloc[:,0:k] # get columns corresponding to length of kernel
                    # Save output file
                    m.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}.csv'.format(t,cond)))
                
                    print(t)
                    print(cond)
                else:
                    print('Error! Check number of trials, something went wrong')
        print('success: dataframe_pupil_event_related_higher')
    
    



   
