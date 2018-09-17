#!/usr/bin/env python
# encoding: utf-8
"""
================================================
pupil_data_analysis.py

If used, please cite: 
Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018).
================================================
"""
from __future__ import division
import os
import sys
import numpy as np
import scipy as sp
import scipy.stats as stats
import pandas as pd
import copy
from copy import deepcopy
import pyvttbl as pt
from pyvttbl import SimpleHTML
from IPython import embed as shell

sys.path.append(os.environ['ANALYSIS_HOME'])
from Tools.Sessions import *
from Tools.Run import *
from Tools.Operators import *
from Tools.log import *

import myfuncs as myfuncs
import functions_oc as ocf

############################################
# PUPIL functions first, then BOLD functions
############################################

class higherLevel(object):
    def __init__(self, subjects, experiment_name, project_directory):
        
        self.subjects = subjects
        self.nr_subjects = len(self.subjects)
        self.experiment_name = experiment_name
        self.project_directory = project_directory
        self.data_folder = os.path.join(project_directory, 'data', 'across')
        self.dataframe_folder = os.path.join(project_directory, 'data_frames')

        ##############################    
        # Define Conditions of Interest
        ##############################
        self.time_locked = ['resp_locked','feed_locked']
        self.factors = [
            ['subj_idx'], # not for anova
            ['easy'],
            ['correct'],
            ['easy','correct'],
        ] 
        self.csv_names = [
            'all', # not for anova
            'easy',
            'correct',
            'easy*correct',
        ]
        # for dataframe_pupil_higher() and run_anova_pupil()
        self.dvs = [
            'rt',
            'pupil_b',
            'pupil_b_feed',            
            'pupil_resp_d_clean', # choice locked  (RT out)
            'pupil_resp_d_clean_RT',   # choice locked  (RT in)
            'pupil_d_feed_clean', # feed locked
            'pupil_feed_stim_baseline',  # feed_baseline - stim_baseline RT out
            'pupil_feed_stim_baseline_RT',  # feed_baseline - stim_baseline RT in

        ] 
        self.anova_dv_type =['mean'] # ,'med']
        
        ##############################    
        # Pupil time series information:
        ##############################
        self.sample_rate = 1000
        self.downsample_rate = 100     
        self.new_sample_rate = self.sample_rate / self.downsample_rate
        self.interval = 15 # determines size of kernel when * with sample rate

        
    def dataframe_pupil_subjects(self, remove_omissions=True):
        #################################
        # see 'd' dataframe below for pupil scalar values
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
        # NOTE: removed the following runs at the higher level because of data quality
        omissions = omissions + np.array((parameters_joined['subject'] == 'sub-11') & (parameters_joined['session'] == 3))
        
        ################
        # feedback baseline pupil - stim-locked baseline pupil (later pre-feedback window [-0.5,0] wrt feedback)
        parameters_joined['pupil_feed_stim_baseline'] = np.array(parameters_joined['pupil_b_feed']) - np.array(parameters_joined['pupil_b'])
        
        ##############################
        # Always remove omissions BEFORE regressing out RT
        # save pupil scalars with RT in (before_omissions, both will be the same)
        parameters_joined['pupil_d_clean_RT'] = np.array(parameters_joined['pupil_d_clean'])
        parameters_joined['pupil_resp_d_clean_RT'] = np.array(parameters_joined['pupil_resp_d_clean'])
        parameters_joined['pupil_feed_stim_baseline_RT'] = np.array(parameters_joined['pupil_feed_stim_baseline'])
        
        
        if remove_omissions: 
            parameters_joined = parameters_joined[~omissions]
            # Regress RT out of pupil only after omissions removed
        
            ##############################
            # regress out RT per session:
            ##############################
            for subj in np.unique(parameters_joined.subject):
                for s in np.unique(parameters_joined.session[parameters_joined.subject == subj]):
                    ind = (parameters_joined.subject == subj) * (parameters_joined.session == s)
                    rt = stats.zscore(np.log(parameters_joined['RT'][ind])) # redo with log transformed and z-scored pupil
                    # pupil_resp_d_clean choice locked
                    pupil_data = np.array(parameters_joined['pupil_resp_d_clean'][ind])
                    pupil_data = myfuncs.lin_regress_resid(pupil_data, [rt]) + pupil_data.mean()
                    parameters_joined['pupil_resp_d_clean'][ind] = pupil_data
                    # feed-stim baselines 
                    pupil_data = np.array(parameters_joined['pupil_feed_stim_baseline'][ind])
                    pupil_data = myfuncs.lin_regress_resid(pupil_data, [rt]) + pupil_data.mean()
                    parameters_joined['pupil_feed_stim_baseline'][ind] = pupil_data
                
        # main effects
        rt = np.array(parameters_joined['RT'])
        correct = np.array(parameters_joined['correct'], dtype=bool) # boolean
        error = ~correct                                             # boolean
        coherence = np.array(parameters_joined['coherence'])
        hemifield = np.array(parameters_joined['hemifield'])
        present = np.array(parameters_joined['direction']) == 90 # boolean
        yes = np.array(parameters_joined['answer']) == 90 # boolean
        hard = np.array(parameters_joined['difficulty']) == 1 # boolean
        easy = np.array(parameters_joined['difficulty']) == 2 # boolean
        
        # pupil scalars - phasic scalars already have baseline removed pupil_preprocessing.process_across_runs()
        pupil_b = np.array(parameters_joined['pupil_b'])                # pre-feedback baseline
        pupil_b_feed = np.array(parameters_joined['pupil_b_feed'])      # post-feedback baseline
        # Scientific Reports
        pupil_resp_d_clean = np.array(parameters_joined['pupil_resp_d_clean'])    # [3,6] locked to choice
        pupil_resp_d_clean_RT = np.array(parameters_joined['pupil_resp_d_clean_RT'])    # [3,6] locked to choice RT in still
        pupil_feed_stim_baseline = np.array(parameters_joined['pupil_feed_stim_baseline'])   # [-0.5,0] locked to feedback RT out
        pupil_feed_stim_baseline_RT = np.array(parameters_joined['pupil_feed_stim_baseline_RT'])   # [-0.5,0] locked to feedback RT in
        pupil_d_feed_clean = np.array(parameters_joined['pupil_d_feed_clean'])   # [3,6] locked to feedback
        
        # SDT measures (yes = up/90)
        hit = yes * present
        fa = yes * ~present
        miss = ~yes * present
        cr = ~yes * ~present
        # indexing
        run = np.array(parameters_joined['run'], dtype=int)
        session = np.array(parameters_joined['session'], dtype=int)
        trial = np.array(parameters_joined['trial_nr'], dtype=int)
        subj_idx_all = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
        
        # Creates a dataframe with all trial information for each subject in one large file
        d = {
        'subj_idx' : pd.Series(subj_idx_all),
        'stimulus' : pd.Series(np.array(present, dtype=int)), # 1 = up, 0 = down
        'response' : pd.Series(np.array(yes, dtype=int)), # 1 = up, 0 = down
        'rt' : pd.Series(rt),
        'pupil_b' : pd.Series(pupil_b), # baseline
        'pupil_b_feed' : pd.Series(pupil_b_feed), # baseline before feedback
        'pupil_resp_d_clean' : pd.Series(pupil_resp_d_clean), # phasic locked to choice, all trials [3,6] RT out
        'pupil_resp_d_clean_RT' : pd.Series(pupil_resp_d_clean_RT), # phasic locked to choice, all trials [3,6] RT in
        'pupil_feed_stim_baseline' : pd.Series(pupil_feed_stim_baseline), # phasic locked to feedback, all trials [-0.5,0]
        'pupil_feed_stim_baseline_RT' : pd.Series(pupil_feed_stim_baseline_RT), # phasic locked to feedback, all trials [-0.5,0]
        'pupil_d_feed_clean' : pd.Series(pupil_d_feed_clean), # phasic locked to cue, all trials [3,6]
        'run' : pd.Series(run),
        'session' : pd.Series(session),
        'trial' : pd.Series(trial),
        'easy' : pd.Series(np.array(easy, dtype=int)), # 1 = easy, 0 = hard
        'correct' : pd.Series(np.array(correct, dtype=int)),
        'hit' : pd.Series(np.array(hit), dtype=int),
        'fa' : pd.Series(np.array(fa), dtype=int),
        'miss' : pd.Series(np.array(miss), dtype=int),
        'cr' : pd.Series(np.array(cr), dtype=int),
        'coherence': pd.Series(coherence, dtype=float),
        'hemiL' : pd.Series(np.array(hemifield) == -1, dtype=int), # 1 = left, 0 = right
        }
        data_response = pd.DataFrame(d)    
        
        # SAVE DATAFRAME         
        if remove_omissions: 
            data_response.to_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
        else:
            # Add omissions column to all-trials dataframe
            data_response['omissions'] = pd.Series(np.array(omissions), dtype=int)
            data_response.to_csv(os.path.join(self.dataframe_folder,'before_omissions','pupil_subjects_all_trials.csv'))
        print('success: dataframe_pupil_subjects')


    def dataframe_processITI(self):
        # Takes output generated from concatenated trial information in MATLAB
        # Matches trials with the EYELINK generated trial information in python
        # Saves a subjects level file with boolean conditions corresponding to the 3 longest ITIs
        # pupil_subjects.csv: pupil scalars have RT regressed out AFTER omissions removed, 
        
        ###############################
        # MATLAB DATA FILE: be careful with subject numbers and run numbers!!
        mat_data = pd.read_csv(os.path.join(self.dataframe_folder, 'before_omissions', 'LCDec2_3T.csv'))   
        # MAT subjects correspond to their ACTUAL subject numbers...
        mat_subjs = ['sub-09','sub-03','sub-02','sub-04','sub-01','sub-15','sub-10','sub-14','sub-07','sub-12','sub-05','sub-06','sub-13','sub-11','sub-08']
        mat_subj_no = range(1,16)
        mat_data.drop(['omissions'], axis=1, inplace=True) # drop and replace with the pupil generated list of omissions
        # Several subjects' sessions and runs need to be removed (subjects.py - what is commented out)
        # sub-11 session1 run6 (session3 comes out later as part of omissions)
        # sub-04 session1-all
        # sub-12 session1-all, session4-run1
        # sub-02 session2-run 5 run 6
        # sub-10 session1-run6
        # sub-03 session4-run1
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-11')]) & (mat_data['session'] == 1) & (mat_data['run'] == 6)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-04')]) & (mat_data['session'] == 1)].index, inplace=True)      
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-12')]) & (mat_data['session'] == 1)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-12')]) & (mat_data['session'] == 4) & (mat_data['run'] == 1)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-02')]) & (mat_data['session'] == 2) & (mat_data['run'] == 5)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-02')]) & (mat_data['session'] == 2) & (mat_data['run'] == 6)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-10')]) & (mat_data['session'] == 1) & (mat_data['run'] == 6)].index, inplace=True)
        mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-03')]) & (mat_data['session'] == 4) & (mat_data['run'] == 1)].index, inplace=True)
        ###############################
                
        # EDF subjects indexed 0-14!! Totally different subject numbers...
        edf_data = pd.read_csv(os.path.join(self.dataframe_folder, 'before_omissions', 'pupil_subjects_all_trials.csv'))
        edf_data.drop(['Unnamed: 0'], axis=1, inplace=True) 
        
        # python order
        # subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']
        # mat_subj_no[mat_subjs.index('sub-11')] # subject number in MAT file
        # self.subjects.index('sub-09') # subject number in python
        
        python_idx = [self.subjects.index(i) for i in mat_subjs]
        matching = dict(zip(mat_subj_no, python_idx)) # dictionary mapping subject numbers to python subj_idx
        
        if len(mat_data) == len(edf_data):
            # Only proceed if same size
            # HAVE TO REODER SUBJECT NUMBERS AND SORT BY...
            s = pd.DataFrame(mat_data['subj_idx'])
            s.replace(matching, inplace=True) # replace old subject numbers with python subj_idx
            mat_data['python_idx'] = s # add python subj_idx column to MAT data frame
            # sort by python subj_idx, session, run, trial number (very important!)
            mat_data.sort_values(by=['python_idx','session','run','trial_number'], inplace=True) 
            mat_data.reset_index(inplace=True) # VERY IMPORTANT, otherwise cannot match/concat dataframes correctly (uses old indices)
            # concate columns of interest
            edf_data = pd.concat([edf_data, mat_data['isi'], mat_data['ITI'], mat_data['right_hand']] ,axis=1) # add to pupil data
            
            # Make columns for 3 longest isi and ITIs (7.5, 9.5, 11.5)
            edf_data['long_isi'] = (edf_data['isi']==7.5) | (edf_data['isi']==9.5) | (edf_data['isi']==11.5)
            edf_data['long_ITI'] = (edf_data['ITI']==7.5) | (edf_data['ITI']==9.5) | (edf_data['ITI']==11.5)
            
            # save file once with omissions in
            edf_data.to_csv(os.path.join(self.dataframe_folder,'before_omissions','pupil_subjects_all_trials.csv'))
            
            # Remove omissions (defined in dataframe_pupil_subjects())
            edf_data = edf_data[edf_data['omissions'] == 0]
            edf_data.reset_index(inplace=True)
            
            # Have to make sure the RT-regressed pupil scalar residuals from the omissions removed file are used
            good_pupil_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
            good_pupil_data.sort_values(by=['subj_idx','run','trial'], ascending=True, inplace=True) # should be sorted already but just in case (runs are 1-24 so don't need session)
            good_pupil_data.reset_index(inplace=True)
            good_pupil_data['isi'] = edf_data['isi'] # if get error here, rerun dataframe_pupil_subjects()
            good_pupil_data['ITI'] = edf_data['ITI']
            good_pupil_data['long_isi'] = edf_data['long_isi']
            good_pupil_data['long_ITI'] = edf_data['long_ITI']
            good_pupil_data['right_hand'] = edf_data['right_hand']
            
            # save file
            good_pupil_data.drop(['Unnamed: 0','index'], axis=1, inplace=True)
            good_pupil_data.to_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_subjects.csv'))
            
            print('success: dataframe_processITI')
        else:
            print('Error! Something wrong with trial numbers...')

    
    def dataframe_process_motionEnergy(self, ): 
        # add motion energy column to pupil data frame (from MATLAB output)
        # have to match Matlab file info to python info, be careful!
        # see second_level.py process_ITI() for subject info
        
        # Motion energy in Matlab output
        ### GOING TO HAVE TO MATCH TRIALS (remember matlab subjects different numbers!!)
        # columns: subject, session, run, trial, motion energy, coh_level
        me_data = pd.read_csv(os.path.join(self.dataframe_folder,'before_omissions','motion_energy.csv'), names=['subj_matlab','session','run','trial','motion_energy','coh_direction'])
        mat_data = pd.read_csv(os.path.join(self.dataframe_folder, 'before_omissions', 'LCDec2_3T.csv')) # all trials MAT 
        
        me_data.sort_values(by=['subj_matlab','session','run','trial'], ascending=True, inplace=True)
        mat_data.sort_values(by=['subj_idx','session','run','trial_number'], ascending=True, inplace=True)
        
        me_data.reset_index(inplace=True)
        mat_data.reset_index(inplace=True)
        mat_data.drop(['index'], axis=1, inplace=True) 
        
        # make sure same number of trials
        if me_data.shape[0] == mat_data.shape[0]:
            # add motion energy to mat_data
            
            mat_data['motion_energy'] = me_data['motion_energy']
            mat_data['coh_direction'] = me_data['coh_direction']
            
            # get rid of omissions, match subject numbers
            mat_subjs = ['sub-09','sub-03','sub-02','sub-04','sub-01','sub-15','sub-10','sub-14','sub-07','sub-12','sub-05','sub-06','sub-13','sub-11','sub-08']
            mat_subj_no = range(1,16)
            mat_data.drop(['omissions'], axis=1, inplace=True) # drop and replace with the pupil generated list of omissions
            # Several subjects' sessions and runs need to be removed (subjects.py - what is commented out)
            # sub-11 session1 run6 (session3 comes out later as part of omissions)
            # sub-04 session1-all
            # sub-12 session1-all, session4-run1
            # sub-02 session2-run 5 run 6
            # sub-10 session1-run6
            # sub-03 session4-run1
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-11')]) & (mat_data['session'] == 1) & (mat_data['run'] == 6)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-04')]) & (mat_data['session'] == 1)].index, inplace=True)      
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-12')]) & (mat_data['session'] == 1)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-12')]) & (mat_data['session'] == 4) & (mat_data['run'] == 1)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-02')]) & (mat_data['session'] == 2) & (mat_data['run'] == 5)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-02')]) & (mat_data['session'] == 2) & (mat_data['run'] == 6)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-10')]) & (mat_data['session'] == 1) & (mat_data['run'] == 6)].index, inplace=True)
            mat_data.drop(mat_data[(mat_data['subj_idx'] == mat_subj_no[mat_subjs.index('sub-03')]) & (mat_data['session'] == 4) & (mat_data['run'] == 1)].index, inplace=True)
                            
            # Python subjects indexed 0-14!! Totally different subject numbers...
            edf_data = pd.read_csv(os.path.join(self.dataframe_folder, 'before_omissions', 'pupil_subjects_all_trials.csv'))
            edf_data.drop(['Unnamed: 0'], axis=1, inplace=True) 
    
            # python order
            # subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']
            # mat_subj_no[mat_subjs.index('sub-11')] # subject number in MAT file
            # self.subjects.index('sub-09') # subject number in python
    
            python_idx = [self.subjects.index(i) for i in mat_subjs]
            matching = dict(zip(mat_subj_no, python_idx)) # dictionary mapping subject numbers to python subj_idx
    
            if len(mat_data) == len(edf_data):
            
                # Only proceed if same size
                # HAVE TO REODER SUBJECT NUMBERS AND SORT BY...
                s = pd.DataFrame(mat_data['subj_idx'])
                s.replace(matching, inplace=True) # replace old subject numbers with python subj_idx
                mat_data['python_idx'] = s # add python subj_idx column to MAT data frame
                # sort by python subj_idx, session, run, trial number (very important!)
                mat_data.sort_values(by=['python_idx','session','run','trial_number'], inplace=True) 
                mat_data.reset_index(inplace=True) # VERY IMPORTANT, otherwise cannot match/concat dataframes correctly (uses old indices)
                
                # concate columns of interest
                edf_data = pd.concat([edf_data, mat_data['motion_energy'], mat_data['coh_direction']] ,axis=1) # add to pupil data
                # Remove omissions (defined in dataframe_pupil_subjects())
                edf_data = edf_data[edf_data['omissions'] == 0]
                edf_data.reset_index(inplace=True)
                
                # Have to make sure the RT-regressed pupil scalar residuals from the omissions removed file are used
                good_pupil_data = pd.read_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
                good_pupil_data.sort_values(by=['subj_idx','run','trial'], ascending=True, inplace=True) # should be sorted already but just in case (runs are 1-24 so don't need session)
                good_pupil_data.reset_index(inplace=True)
                good_pupil_data.drop(['Unnamed: 0','index'], axis=1, inplace=True)
                                
                # add motion energy 
                good_pupil_data = pd.concat([good_pupil_data, edf_data['motion_energy'], edf_data['coh_direction']] ,axis=1) # add to pupil data
                good_pupil_data['abs_motion_energy'] = np.abs(good_pupil_data['motion_energy']) # absolute value of motion energy (ignore dot direction)
                good_pupil_data.to_csv(os.path.join(self.dataframe_folder,'pupil', 'subjects', 'pupil_subjects.csv'))
            else:
                print('Error! Something wrong with MAT vs. Python trial numbers...')
            print('success: dataframe_process_motionEnergy')
        else:
            print('Error! Something went wrong with the number of trials in both MAT files!')
        
        
        
    def dataframe_pupil_event_related_subjects(self):
        # Cuts out time series of pupil data locked to time points of interest:
        # resp_locked, feed_locked
        # Outputs numpy arrays corresponding to events, all trials for all subjects with omissions removed
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
        omissions = omissions + np.array((parameters_joined['subject'] == 'SW') & (parameters_joined['session'] == 3))
        
        # debug - will not work without 'self' probably overwriting variables
        self.run = np.array(parameters_joined['run'], dtype=int)
        self.session = np.array(parameters_joined['session'], dtype=int)
        self.subj_idx = np.concatenate(np.array([np.repeat(i, sum(parameters_joined['subject'] == self.subjects[i])) for i in range(len(self.subjects))]))
                
        # all trials x events (all subjects at once), will be saved as numpy arrays
        trials_cue = []
        trials_choice = []
        trials_feedback = []  
        trials_feedback_b2 = []   
        trials_subj_idx = []
        
        for i, s in enumerate(self.subjects):
            
            print i
            print s

            runs = np.unique(self.run[self.subj_idx == i])
            sessions = [self.session[self.subj_idx == i][self.run[self.subj_idx == i] == r][0] - 1 for r in runs] 
            # print runs
            # print sessions
            aliases = ['2AFC_{}_{}'.format(run, session+1) for run, session in zip(runs, sessions)]
            base_directory = os.path.join(self.project_directory, self.experiment_name, s)
            hdf5_filename = os.path.join(base_directory, 'processed', s + '.hdf5')
            ho = HDFEyeOperator.HDFEyeOperator(hdf5_filename)
            # parameters_joined2.append(ho.read_session_data('', 'parameters_joined'))
            
            # load data:
            parameters = []     # run (24) x trials per run (25)
            pupil = []          # time series
            time = []           # time series
            cue_times = []
            choice_times = []   # trials (600)
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
                p = np.array(pupil_data[(eye + '_pupil_bp_clean_psc')]) # USE BANDPASSED!
                p = p[~np.isnan(p)]
                pupil.append(p)
                ti = np.array(pupil_data['time']) - session_start
                time.append(ti + time_to_add)
                phase_times = ho.read_session_data(alias, 'trial_phases')
                
                cue_t = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == 3)]) - session_start + time_to_add
                choice_t = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == 5)]) - session_start + time_to_add
                feedback_t = np.array(phase_times['trial_phase_EL_timestamp'][(phase_times['trial_phase_index'] == 6)]) - session_start + time_to_add 
                
                cue_times.append( cue_t )
                choice_times.append( choice_t )
                feedback_times.append( feedback_t )
                
                blink_data = ho.read_session_data(alias, 'blinks_from_message_file')
                blink_times.append( np.array(blink_data['end_timestamp']) - session_start + time_to_add )
                time_to_add += ti[-1]
            
            parameters = pd.concat(parameters)
            pupil = np.concatenate(pupil)
            time = np.concatenate(time)
            cue_times = np.concatenate(cue_times) / 1000.0
            choice_times = np.concatenate(choice_times) / 1000.0
            feedback_times = np.concatenate(feedback_times) / 1000.0
            blink_times = np.concatenate(blink_times) / 1000.0
                        
            # FOR CUE, CHOICE, FEEDBACK extract kernel for each trial, concate together with all subjects
            # event related averages:
            cue_locked_array = np.zeros((len(cue_times), interval*sample_rate))
            cue_locked_array[:,:] = np.NaN
            choice_locked_array = np.zeros((len(cue_times), interval*sample_rate))
            choice_locked_array[:,:] = np.NaN
            feedback_locked_array = np.zeros((len(cue_times), interval*sample_rate))
            feedback_locked_array[:,:] = np.NaN
            feedback_locked_array_b2 = np.zeros((len(cue_times), interval*sample_rate))
            feedback_locked_array_b2[:,:] = np.NaN
            # Cut out time series locked to events of interest
            # Subtract baseline pupil!
            save_baselines = []
            for j, t in enumerate(np.array(((cue_times-2)*sample_rate), dtype=int)): # why -2?  Because start plotting a bit before
                cue_locked_array[j,:len(pupil[t:t+(interval*sample_rate)])] = pupil[t:t+(interval*sample_rate)] - np.mean(pupil[t+1500:t+2000])
                save_baselines.append(np.mean(pupil[t+1500:t+2000]))   
            print j
            ### Note resp -5 is different than stim + feedback!
            for j, t in enumerate(np.array(((choice_times-5)*sample_rate), dtype=int)): # take out baseline period preceding cue
                choice_locked_array[j,:len(pupil[t:t+(interval*sample_rate)])] = pupil[t:t+(interval*sample_rate)] - save_baselines[j]
            for j, t in enumerate(np.array(((feedback_times-2)*sample_rate), dtype=int)):
                feedback_locked_array[j,:len(pupil[t:t+(interval*sample_rate)])] = pupil[t:t+(interval*sample_rate)] - np.mean(pupil[t+1500:t+2000])
            # feedback with respect to stim baseline
            for j, t in enumerate(np.array(((feedback_times-2)*sample_rate), dtype=int)):
                feedback_locked_array_b2[j,:len(pupil[t:t+(interval*sample_rate)])] = pupil[t:t+(interval*sample_rate)] - save_baselines[j]             
                            
            # Add to dataframe   
            trials_cue.append(cue_locked_array)
            trials_choice.append(choice_locked_array)
            trials_feedback.append(feedback_locked_array)
            trials_feedback_b2.append(feedback_locked_array_b2)
            trials_subj_idx.append(self.subj_idx[self.subj_idx==i])
        
        # After all subjects are in, make one long list    
        trials_cue = np.concatenate(np.array(trials_cue))
        trials_choice = np.concatenate(np.array(trials_choice))
        trials_feedback = np.concatenate(np.array(trials_feedback))
        trials_feedback_b2 = np.concatenate(np.array(trials_feedback_b2))
        trials_subj_idx = np.concatenate(np.array(trials_subj_idx))
        
        # take out omissions
        trials_cue = trials_cue[~omissions]
        trials_choice = trials_choice[~omissions]
        trials_feedback = trials_feedback[~omissions]
        trials_feedback_b2 = trials_feedback_b2[~omissions]
        trials_subj_idx = trials_subj_idx[~omissions]
                
        # save as numpy arrays, easier than CSV files with 9,000 trials x 15,000 timepoints
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_stim_locked.npy'), trials_cue)
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_resp_locked.npy'), trials_choice)
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_feed_locked.npy'), trials_feedback)
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_feed_locked_b2.npy'), trials_feedback_b2)
        np.save(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_events_subj_idx.npy'), trials_subj_idx)
        print('success: dataframe_pupil_event_related_subjects')
        
        
        
    def dataframe_pupil_higher(self):
        # Run after dataframe_subjects(), creates a higher level dataframe to be used as input for ANOVAs
        # Output formated for repeated measures ANOVA data:
        # NEED TO SAVE SEPARATE DATAFRAMES FOR EACH COMBINATION OF IVS
        
        factors = deepcopy(self.factors) # deepcopy necessary for stopping backwards referencing of global
        csv_names = deepcopy(self.csv_names)
        dvs = deepcopy(self.dvs)
        # Read in subjects dataframe
        sdata = pd.read_csv(os.path.join(self.dataframe_folder, 'pupil', 'subjects', 'pupil_subjects.csv'))

        # Loop through conditions                
        for c,cond in enumerate(csv_names): 
            # intialize dataframe per condition
            g_idx = factors[c]        # need to add subject idx for groupby()
            if cond !='all':
                g_idx.insert(0, 'subj_idx') # get strings not list element
                
            # Here if selecting based on isi or ITI
            for trial_type in ['','_isi','_ITI']:
                this_cond = pd.DataFrame() # initialize new data_frame, prevents overwriting
                this_cond2 = pd.DataFrame() # for separate ITIs initialize new data_frame, prevents overwriting
                
                data = deepcopy(sdata)
                
                # all sessions
                if trial_type == '_isi':
                    data = data[data['long_isi']]
                elif trial_type == '_ITI':
                    data = data[data['long_ITI']]
                
                data.reset_index(inplace=True)
                data.drop(['index'],axis=1,inplace=True)
                
                # Loop through dvs            
                for dv in dvs:
                    # group by subject, then factors
                    g = data.groupby(g_idx)[dv].agg(['mean','std','median'])
                    # add to condition dataframe
                    this_cond = pd.concat([this_cond,g],  axis=1) # can also do: this_cond = this_cond.append()
                    this_cond.rename(columns = {'mean': dv+'_mean', 'std': dv+'_std', 'median': dv+'_med'}, inplace=True)
                    
                # save output file
                this_cond.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_higher_{}{}.csv'.format(cond,trial_type)))
                    
                # save frequencies of condition types
                freq = pd.DataFrame(data.groupby('subj_idx').sum()) # how many times it occured
                freq.drop(dvs, axis=1, inplace=True) # drop dv columns
                freq.drop(['Unnamed: 0','run','session'], axis=1, inplace=True) # drop trial column
                freq.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','frequency{}.csv'.format(trial_type)))
                # save total number of trials per condition
                cnt = pd.DataFrame(data.groupby('subj_idx').count()) # how many trials
                cnt.drop(dvs, axis=1, inplace=True) # drop dv columns
                cnt.drop(['Unnamed: 0','run','session'], axis=1, inplace=True) # drop trial column
                cnt.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','count{}.csv'.format(trial_type)))
                # save frequencies of errors*difficulty
                freq = pd.DataFrame(data.groupby(['easy','correct']).count()) # how many times it occured
                freq.drop(dvs, axis=1, inplace=True) # drop dv columns
                freq.drop(['Unnamed: 0','run','session'], axis=1, inplace=True) # drop trial column
                freq.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','count_easy*correct{}.csv'.format(trial_type)))
                # save frequencies of errors*difficulty per subject
                freq = pd.DataFrame(data.groupby(['subj_idx','easy','correct']).count()) # how many times it occured
                freq.drop(dvs, axis=1, inplace=True) # drop dv columns
                freq.drop(['Unnamed: 0','run','session'], axis=1, inplace=True) # drop trial column
                freq.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','count_easy*correct_subjects{}.csv'.format(trial_type)))        
        print('success: dataframe_pupil_higher')
        
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
                
            for t,time_locked in enumerate(self.time_locked + ['feed_locked_b2']):
                # Load numpy arrays containing time series events for all trials, all subjects
                a = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format(time_locked)))
                b = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format('subj_idx')))

                # Read in subjects dataframe
                sdata = pd.read_csv(os.path.join(self.dataframe_folder, 'pupil','subjects','pupil_subjects.csv'))
                sdata.drop(['Unnamed: 0'], axis=1, inplace=True) # artifact of dataframe

                # Make sure that the trial numbers correspond before proceeding...
                if len(sdata) == len(a) == len(b):
                    tsdata = pd.DataFrame(a) # time series data convert to dataframe
                    sdata = pd.concat([tsdata, sdata],axis=1) # concatenate, order is important for selecting columns below
                    
                    for trial_type in ['','_isi','_ITI']:                    
                        data = deepcopy(sdata)
                        # Here if selecting based on isi or ITI
                        if trial_type == '_isi':
                            data = data[data['long_isi']]
                        elif trial_type == '_ITI':
                            data = data[data['long_ITI']]

                        data.reset_index(inplace=True)
                        data.drop(['index'],axis=1,inplace=True)
                        
                        m = data.groupby(g_idx).mean() # means grouped by subject, then factors of interest
                        m = m.iloc[:,0:k] # get columns corresponding to length of kernel
                        # Save output file
                        m.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format(time_locked,cond,trial_type)))
                    
                        # save as numpy array instead
                        # m = np.array(m)
                        # np.save(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}.npy'.format(trial_type)), m)
                        print(t)
                        print(cond)
                        print(trial_type)     
                else:
                    print('Error! Check number of trials, something went wrong')
        print('success: dataframe_pupil_event_related_higher')
        
    def dataframe_pupil_event_related_higher_regressRT(self, downsample=True):
        # For the stim_locked and resp_locked pupil data (run after dataframe_pupil_event_related_higher() )
        # For each time point 
        # 1) remove RT, for each subject for each session (_rRT)
                
        factors = deepcopy(self.factors) # deepcopy necessary for stopping backwards referencing of global
        k = self.interval*self.sample_rate # length of kernel
        
        downsample_rate = 20 # 20 Hz
        downsample_factor = self.sample_rate / downsample_rate # 50
        interval = self.interval # determines size of kernel when * with sample rate
        k2 = self.interval*downsample_rate # length of kernel
                
        for t,time_locked in enumerate(['resp_locked']): # don't do for feed_locked
            # Load numpy arrays containing time series events for all trials, all subjects
            a = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format(time_locked)))
            b = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format('subj_idx')))

            # Read in subjects dataframe
            sdata = pd.read_csv(os.path.join(self.dataframe_folder, 'pupil','subjects','pupil_subjects.csv'))
            sdata.drop(['Unnamed: 0'], axis=1, inplace=True) # artifact of dataframe

            # Make sure that the trial numbers correspond before proceeding...
            if len(sdata) == len(a) == len(b):
                tsdata = pd.DataFrame(a) # time series data convert to dataframe
                sdata = pd.concat([tsdata, sdata],axis=1) # concatenate, order is important for selecting columns below
                
                for trial_type in ['','_isi','_ITI']:                
                    data = deepcopy(sdata)
                    # Here if selecting based on isi or ITI
                    if trial_type == '_isi':
                        data = data[data['long_isi']]
                    elif trial_type == '_ITI':
                        data = data[data['long_ITI']]

                    data.reset_index(inplace=True)
                    data.drop(['index'],axis=1,inplace=True)
                    # regression doesn't work with NaNs
                    data = data.dropna(axis=0, how='any')
                    
                    # REGRESSION per subject per session
                    #######################################
                    if downsample:
                        pupil = sp.signal.decimate(np.array(data.iloc[:,0:k]), int(downsample_factor), ftype='fir') # original pupil data
                        save_pupil = pupil # rRT
                    else:
                        pupil = np.array(data.iloc[:,0:k])
                        save_pupil = pupil # copy residuals to save_pupil based on index
                    
                    ## NUISANCE REGRESSION OF RT FROM PUPIL ###
                    for subj in np.unique(data['subj_idx']):
                        for s in np.unique(data['session'][data['subj_idx'] == subj]):
                            ind = (data['subj_idx'] == subj) * (data['session'] == s) # which rows

                            rt = stats.zscore(np.log(data['rt'][ind])) # log and zscore
                            this_pupil = np.array(pupil[ind]) # use to prevent overwriting original

                            # loop over time points = columns
                            for i in range(pupil.shape[1]):
                                # regress RT out of pupil, save residuals (log and zscore?)
                                this_pupil[:,i] = myfuncs.lin_regress_resid(np.array(this_pupil[:,i]), [rt]) + np.nanmean(this_pupil[:,i]) # rRT
                            save_pupil[ind] = this_pupil
                            
                    # make new data frame with columns conditions
                    save_pupil = pd.DataFrame(save_pupil).reset_index()
                    cols = data.iloc[:,k+1:].reset_index() # condition columns
                    new_data = pd.concat([save_pupil, cols ],axis=1) 
                    new_data.drop(['index'],axis=1,inplace=True)
                    # save at single trial level for regression to motion energy
                    new_data.to_csv(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}{}_rRT.csv'.format(time_locked,trial_type)))
                    
                    ## GROUPED BY CONDITIONS ##
                    # Loop across factors of interest
                    g_idx = []
                    for c,cond in enumerate(self.csv_names):
                        g_idx = factors[c]
                        # Add 'subj_idx' as first element of list here:
                        if cond !='all':
                            g_idx.insert(0, 'subj_idx') # get strings not list element
                            
                        m = new_data.groupby(g_idx).mean() # means grouped by subject, then factors of interest
                        m = m.iloc[:,0:k2] # get columns corresponding to length of kernel
                        
                        # Save output file
                        m.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}_rRT.csv'.format(time_locked,cond,trial_type)))

                        print(time_locked)
                        print(cond)
                        print(trial_type)     
            else:
                print('Error! Check number of trials, something went wrong')
        print('success: dataframe_pupil_event_related_higher_regressRT')
    
    def dataframe_pupil_event_related_higher_regressME(self, downsample=True):
        # For the stim_locked and resp_locked pupil data (run after dataframe_pupil_event_related_higher() )
        # For each time point 
        # Regression is done separately for each condition of interest
        # 1) get beta motion energy for each subject for each session (_beta)
        # 2) get beta motion energy with nuisance RT for each subject for each session (_beta_rRT)
                
        # only one that matters for motion energy
        factors = ['correct'] # deepcopy necessary for stopping backwards referencing of global
        k = self.interval*self.sample_rate # length of kernel
        
        downsample_rate = 20 # 20 Hz
        downsample_factor = self.sample_rate / downsample_rate # 50
        interval = self.interval # determines size of kernel when * with sample rate
        k2 = self.interval*downsample_rate # length of kernel
                
        for t,time_locked in enumerate(self.time_locked + ['feed_locked_b2']):
        
            # Load numpy arrays containing time series events for all trials, all subjects
            a = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format(time_locked)))
            b = np.load(os.path.join(self.dataframe_folder,'pupil','subjects','pupil_events_{}.npy'.format('subj_idx')))

            # Read in subjects dataframe
            sdata = pd.read_csv(os.path.join(self.dataframe_folder, 'pupil','subjects','pupil_subjects.csv'))
            sdata.drop(['Unnamed: 0'], axis=1, inplace=True) # artifact of dataframe

            # Make sure that the trial numbers correspond before proceeding...
            if len(sdata) == len(a) == len(b):
                tsdata = pd.DataFrame(a) # time series data convert to dataframe
                sdata = pd.concat([tsdata, sdata],axis=1) # concatenate, order is important for selecting columns below
                
                for trial_type in ['','_isi','_ITI']:
                    data = deepcopy(sdata)
                    # Here if selecting based on isi or ITI
                    if trial_type == '_isi':
                        data = data[data['long_isi']]
                    elif trial_type == '_ITI':
                        data = data[data['long_ITI']]

                    data.reset_index(inplace=True)
                    data.drop(['index'],axis=1,inplace=True)
                    # regression doesn't work with NaNs
                    data = data.dropna(axis=0, how='any')
                    
                    save_betas_correct = [] # betas
                    save_betas_error = [] # betas
                    
                    save_betas_rRT_correct = [] # betas_rRT
                    save_betas_rRT_error = [] # betas_rRT
                    
                    # REGRESSION per subject per session
                    #######################################
                    if downsample:
                        pupil = sp.signal.decimate(np.array(data.iloc[:,0:k]), int(downsample_factor), ftype='fir') # original pupil data
                        # save_pupil = pupil # rRT
                    else:
                        pupil = np.array(data.iloc[:,0:k])
                        # save_pupil = pupil # copy residuals to save_pupil based on index
                    
                    for ACC in [0,1]: # do separately for error, correct trials       
                        ### REGRESSION OF MOTION ENERGY ONTO PUPIL ###        
                        for subj in np.unique(data['subj_idx']):
                            this_betas = []
                            this_betas_rRT = []
                            # get beta coefficient for motion energy 

                            ind = (data['subj_idx'] == subj) & (data['correct']==ACC) # which rows
                            rt_me = stats.zscore(np.log(np.array(data['rt'][ind]))) # log and zscore
                            me = stats.zscore(data['abs_motion_energy'][ind]) # motion energy zscore of abs value
                            betas_data = np.array(pupil[ind])
                            betas_rRt_data = np.array(pupil[ind])

                            # loop over time points = columns
                            for i in range(betas_data.shape[1]):
                                Y = np.array(betas_data[:,i]) # pupil data 
                                X = np.column_stack((me)) # motion energy
                                betas = ocf.lin_regress_betas(Y, X)    # constant, ME
                                this_betas.append(betas[1])
                            
                                # RT as nuisance regressor
                                Y = np.array(betas_rRt_data[:,i]) # pupil data 
                                X = np.column_stack((me,rt_me)) # motion energy
                                betas = ocf.lin_regress_betas(Y, transpose(X))    # constant, ME, RT
                                this_betas_rRT.append(betas[1])
                            
                            if ACC:
                                save_betas_correct.append(this_betas)
                                save_betas_rRT_correct.append(this_betas_rRT)
                            else:
                                save_betas_error.append(this_betas)
                                save_betas_rRT_error.append(this_betas_rRT)
                            
                    # subjects x time points
                    save_betas_correct = pd.DataFrame(save_betas_correct)            
                    save_betas_rRT_correct = pd.DataFrame(save_betas_rRT_correct)
                    save_betas_error = pd.DataFrame(save_betas_error)
                    save_betas_rRT_error = pd.DataFrame(save_betas_rRT_error)
                            
                    # make new data frame for both regression models
                    save_m1 = pd.concat([save_betas_error, save_betas_correct],axis=0)  # betas
                    save_m2 = pd.concat([save_betas_rRT_error, save_betas_rRT_correct],axis=0)  # betas_rRT
                    
                    # generate conditions
                    s = np.array(range(len(self.subjects)))
                    ss = np.hstack((s,s))
                    acc_col = np.hstack( (np.repeat(0,len(self.subjects)), np.repeat(1,len(self.subjects))))
                                        
                    save_m1['subj_idx'] = ss
                    save_m1['correct'] = acc_col
                    save_m2['subj_idx'] = ss
                    save_m2['correct'] = acc_col
                                        
                    save_m1.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}.csv'.format(time_locked,'motion_energy',trial_type)))
                    save_m2.to_csv(os.path.join(self.dataframe_folder,'pupil','higher','pupil_events_{}_{}{}_rRT.csv'.format(time_locked,'motion_energy',trial_type)))
                    
                    print(time_locked)
                    # print(cond)
                    print(trial_type)     
            else:
                print('Error! Check number of trials, something went wrong')
        print('success: dataframe_pupil_event_related_higher_regressME')
        
                       
    def run_anova_pupil(self):
        # Runs a repeated measures ANOVA for all dvs for all conditions 
        # Outputs an HTML table of results and CSV file containing statistics 
        # Loads higher level subjects file into dataframe
        # Convert pandas dataframe to pt dataframe for ANOVA input 
    
        factors = deepcopy(self.factors) # deepcopy necessary for stopping backwards referencing of global
        csv_names = deepcopy(self.csv_names)
        dvs = deepcopy(self.dvs)
        
        # loop over factors, loop through dvs    
        for c,cond in enumerate(csv_names):
            # Skip 'all', need to implement 1-way ANOVA
            if cond != 'all':
                for trial_type in ['','_isi','_ITI']:
                    # grab the corresponding higher level file
                    d = pd.read_csv(os.path.join(self.project_directory, 'data_frames','pupil','higher','pupil_higher_{}{}.csv'.format(cond, trial_type)))
                    # pyttble dataframe format  
                    d = pt.DataFrame(d)      
                    # Loop through statistic computed on dv: e.g. mean or std
                    for dv_type in self.anova_dv_type:
                        # loop through all dvs
                        for dv in dvs:                
                            dv = dv+'_'+dv_type # _mean or _std
                            # run anova in pt    
                            aov = d.anova(dv, sub='subj_idx', wfactors=factors[c])
                            # print(aov)        
                            save_output = []
                            # Get important stats out
                            terms = aov.keys() # returns a list of factors with interaction term
                            for k in terms:
                                r = ocf.extract_for_apa(k, aov, values = ['F', 'mse', 'eta', 'p']) # returns a dictionary object
                                save_output.append(r)
                            dout = pd.DataFrame(save_output)
                            # csv: 1st row = 1st factor, 2nd row = factor, 3rd row = interaction    
                            dout.to_csv(os.path.join(self.dataframe_folder, 'anova_output','csv','rm_anova_{}_{}{}.csv'.format(dv, cond, trial_type)))
                        
                            # save whole table in HTML format
                            output = SimpleHTML.SimpleHTML(cond)
                            aov._within_html(output)
                            output.write(os.path.join(self.dataframe_folder, 'anova_output','html','rm_anova_{}_{}{}.html'.format(dv, cond, trial_type)))       
        print('success: run_anova_pupil')

