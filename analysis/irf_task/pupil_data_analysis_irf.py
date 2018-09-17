#!/usr/bin/env python
# encoding: utf-8
"""
================================================
pupil_data_analysis_irf.py

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

import nibabel as nib
import sklearn
import hddm
import mne
import statsmodels.formula.api as sm
import nibabel as nib
import nilearn

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
from Tools.other_scripts.plotting_tools import *
from Tools.other_scripts.circularTools import *

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


class higherLevel(object):
    def __init__(self, subjects, experiment_name, project_directory):
        
        self.subjects = subjects
        self.nr_subjects = len(self.subjects)
        self.experiment_name = experiment_name
        self.project_directory = project_directory
        self.data_folder = os.path.join(project_directory, 'measure_irf', 'across')
        self.figure_folder = os.path.join(project_directory, 'figures')
        self.dataframe_folder = os.path.join(project_directory, 'data_frames')

        ##############################    
        # Define Conditions of Interest
        ##############################
        self.factors = [
            ['subj_idx'], 
        ] 
        self.csv_names = [
            'all', 
        ]
        
        self.time_locked = ['stim_locked','resp_locked']
        # for dataframe_pupil_higher() and run_anova_pupil()
        self.dvs = [
            'RT',
            'pupil_b',
            'pupil_d',
            'pupil_cd', 
        ] 
        self.anova_dv_type =['mean','med']

        
        ##############################    
        # Pupil time series information:
        ##############################
        self.sample_rate = 1000
        self.downsample_rate = 20       # 50
        self.new_sample_rate = self.sample_rate / self.downsample_rate
        self.interval = 15 # in seconds, determines size of kernel when * with sample rate
        # order is stim, feed, resp!
        self.pupil_step_lim = [[-1,14],[-1,14]] 
        self.pupil_values = ['pupil_d','pupil_cd'] # pupil_d locked to choice, pupil_cd locked to cue
        self.pupil_xlim = [   
            # order is stim, resp!
            [-0.5,7.5], 
            [-1,7.5], 
        ]
        self.pupil_time_of_interest = [   
            # order is stim, resp!
            [1,2.5], # original pupil_d
            [-0.5,2.5],# pupil_cd
        ]

        
    def dataframe_pupil_subjects(self):
        #################################
        # pupil_b is pupil baseline before cue
        # pupil_d is pupil dilation locked to response [0, 0.5] s
        # pupil_cd is pupil dilation locked to cue [0.25,1] s
        # defined in pupil_preprocessing_irf.process_across_runs()
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
            # First and last trial NAN, some sort of technical error
            omissions = omissions + np.array(parameters_joined['trial'] == 0)
            omissions = omissions + np.array(parameters_joined['trial'] == 24)
            omissions = omissions + np.isnan(parameters_joined['RT']) # missed trial
        ##############################
        parameters_joined = parameters_joined[~omissions]
        # EVERYTHING UNDER HERE HAS OMISSIONS REMOVED

        # main effects
        response = np.array(parameters_joined['response']) == 1 # answered
        sound = np.array(parameters_joined['sound']) == 1 # always white noise
        RT = np.array(parameters_joined['RT'])
        
        # pupil scalars - phasic scalars already have baseline removed pupil_preprocessing_irf.process_across_runs()
        pupil_b = np.array(parameters_joined['pupil_b'])
        pupil_d = np.array(parameters_joined['pupil_d'])
        pupil_cd = np.array(parameters_joined['pupil_cd'])
        
        # indexing
        run = np.array(parameters_joined['run'], dtype=int)
        session = np.array(parameters_joined['session'], dtype=int)
        subj_idx_all = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
        
        # Creates a dataframe with all trial information for each subject in one large file
        # Note: omissions already removed        
        d = {
        'subj_idx' : pd.Series(subj_idx_all),
        'pupil_b' : pd.Series(pupil_b), # baseline before cue
        'pupil_d' : pd.Series(pupil_d), # phasic locked to response
        'pupil_cd' : pd.Series(pupil_cd), # phasic locked to cue
        'run' : pd.Series(run),
        'session' : pd.Series(session),
        'response' : pd.Series(np.array(response, dtype=int)),
        'sound' : pd.Series(np.array(sound, dtype=int)),
        'RT': pd.Series(np.array(RT, dtype=float)),
        # 'omissions' : pd.Series(np.array(omissions), dtype=int)
        }
        data_response = pd.DataFrame(d)    
        # SAVE DATAFRAME         
        data_response.to_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
        print('success: dataframe_pupil_subjects')


    def dataframe_IRF_deconvolution(self, plot_subjs=True):
        # Finite Impulse Response deconvolution 
        # T. Knapen github
        # Removing first and last trial because of missing data
        # cue-locked and resp-locked
        
        ################################
        ## MAKE EVENT RELATED DATA FRAME
        ################################
        sample_rate = self.sample_rate
        downsample_rate = self.downsample_rate # 20 Hz
        downsample_factor = sample_rate / downsample_rate # 50
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
        omissions = omissions + np.array(parameters_joined['trial_nr'] == 0) # take out first trial
        omissions = omissions + np.array(parameters_joined['trial_nr'] == 24) # take out last trial
        omissions = omissions + np.isnan(parameters_joined['RT']) # missed trial
        
        # debug - will not work without 'self' probably overwriting variables
        self.run = np.array(parameters_joined['run'], dtype=int)
        self.session = np.array(parameters_joined['session'], dtype=int)
        self.subj_idx = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
                
        for t,time_locked in enumerate(['resp_locked']):
            
            # all subjects x deconvolved IRFs saved here:
            IRFs = [] 
        
            if plot_subjs:
                # illustrate in one big figure
                fig = plt.figure(figsize=(8,8))
        
            for i, s in enumerate(self.subjects):
            
                print i
                print s

                runs = np.unique(self.run[self.subj_idx == i])
                sessions = [self.session[self.subj_idx == i][self.run[self.subj_idx == i] == r][0] - 1 for r in runs] 
                # print runs
                # print sessions
                aliases = ['measureIRF_{}_{}'.format(run, session+1) for run, session in zip(runs, sessions)]
                base_directory = os.path.join(self.project_directory, self.experiment_name, s)
                hdf5_filename = os.path.join(base_directory, 'processed', s + '.hdf5')
                ho = HDFEyeOperator.HDFEyeOperator(hdf5_filename)
            
                # load data:
                parameters = []     # run (4) x trials per run (25)
                pupil = []          # time series
                time = []           # time series
                cue_times = []      # trials (100)
                time_to_add = 0
            
                # loops through runs across all the sessions of each subject
                for alias in aliases:
                    parameters.append(ho.read_session_data(alias, 'parameters2'))
                    # self.alias = alias
                    trial_times = ho.read_session_data(alias, 'trials')
                    eye = ho.eye_during_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
                    pupil_data = ho.data_from_time_period((np.array(trial_times['trial_start_EL_timestamp'])[0], np.array(trial_times['trial_end_EL_timestamp'])[-1]), alias)
                    session_start = trial_times['trial_start_EL_timestamp'][0]
                    p = np.array(pupil_data[(eye + '_pupil_bp_clean_psc')]) # USE BAND-PASSED!!
                    p = p[~np.isnan(p)]
                    pupil.append(p)
                    ti = np.array(pupil_data['time']) - session_start
                    time.append(ti + time_to_add)
                    phase_times = ho.read_session_data(alias, 'trial_phases')
                
                    # 1 for sound, 2 for response
                    if time_locked == 'stim_locked':
                        phase_idx = 1
                    else:
                        phase_idx = 2 
                    cue_t = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == phase_idx)]) - session_start + time_to_add
                    # remove first and last trial - bc missing data
                    cue_t = cue_t[1:-1]
                
                    cue_times.append( cue_t )
                
                    time_to_add += ti[-1]

                parameters = pd.concat(parameters)
                pupil = np.concatenate(pupil)
                time = np.concatenate(time)
                events_1 = (np.concatenate(cue_times)/1000.0)-1 # go back 1 sec to include baseline period
            
                #######################
                #### Deconvolution ####
                #######################
                from fir import FIRDeconvolution

                # first, we initialize the object
                fd = FIRDeconvolution(
                            signal = pupil, 
                            events = [events_1,], # stim_onset - 1 in seconds
                            event_names = ['event_1',], 
                            sample_frequency = sample_rate, # Hz
                            deconvolution_frequency = downsample_rate, # Hz
                            deconvolution_interval = [0, interval] # 0 = stim_onset - 1
                            )

                # we then tell it to create its design matrix
                fd.create_design_matrix()

                # perform the actual regression, in this case with the statsmodels backend
                fd.regress(method = 'lstsq')

                # and partition the resulting betas according to the different event types
                fd.betas_for_events()
                fd.calculate_rsq()
                response = fd.betas_per_event_type.squeeze()

                ### BASELINE IRFS - 500 ms before cue
                # response starts 1 second before cue, so want to take [-0.5,0] wrt cue
                baseline_duration = 0.5*downsample_rate
                this_baseline = np.mean(response[int(1*downsample_rate-baseline_duration):int(1*downsample_rate)])
                response = response-this_baseline
            
                # save this subject's deconvolved IRF
                IRFs.append(response)
            
                if plot_subjs:
                    # R-squared value
                    rsquared = fd.rsq
                    # Add error bars
                    fd.bootstrap_on_residuals(nr_repetitions=1000)
                    # plot subject
                    plot_time = response.shape[-1] # for x-axis
                    ax2 = fig.add_subplot(4,4,i+1)
                    ax2.axvline(1*downsample_rate, lw=0.25, alpha=0.5, color = 'k') # Add vertical line at t=0
                    ax2.axhline(0, lw=0.25, alpha=0.5, color = 'k') # Add horizontal line at t=0
                
                    for b in range(fd.betas_per_event_type.shape[0]):
                        ax2.plot(np.arange(plot_time), fd.betas_per_event_type[b])


                    for i in range(fd.bootstrap_betas_per_event_type.shape[0]):
                        mb = fd.bootstrap_betas_per_event_type[i].mean(axis = -1)
                        sb = fd.bootstrap_betas_per_event_type[i].std(axis = -1)
   
                        ax2.fill_between(np.arange(plot_time), 
                                        mb - sb, 
                                        mb + sb,
                                        color = 'k',
                                        alpha = 0.1)
                    # ax2.plot(np.arange(plot_time), response, 'g-')
                
                
                    ax2.set_xticks([1*downsample_rate,plot_time])
                    ax2.set_xticklabels([0,interval-1]) # removed 1 second from events
                    ax2.set_xlabel('Time from event (s)')
                    ax2.legend(['Deconvolution'], loc='best', fontsize=4)
                    # ax2.set_ylim([-2,4])
                    ax2.set_title('{} r2={}'.format(s,rsquared[0]))

            # save all deconvolved IRFs in dataframe
            IRFs = pd.DataFrame(IRFs)
            IRFs.to_csv(os.path.join(self.dataframe_folder,'pupil', 'higher', 'deconvolution_IRF_{}.csv'.format(time_locked)))
        
            if plot_subjs:
                # Save figure
                sns.despine(offset=10, trim=True)
                plt.tight_layout()
                fig.savefig(os.path.join(self.figure_folder, 'conditions', 'pupil', 'deconvolution','Deconvolution_Subjects_IRF_{}.pdf'.format(time_locked)))
        print('success: dataframe_IRF_deconvolution')        
        
        




   