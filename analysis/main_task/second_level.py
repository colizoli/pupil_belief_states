#!/usr/bin/env python
# encoding: utf-8
"""
second_level.py

If used, please cite: 
Colizoli, O., de Gee, J. W., Urai, A. E. & Donner, T. H.
Task-evoked pupil responses reflect internal belief states. Scientific Reports 8, 13702 (2018).

"""

import os, sys, datetime
import subprocess, logging

import scipy as sp
import scipy.stats as stats
import numpy as np
import matplotlib.pylab as pl

from IPython import embed as shell

this_raw_folder = '/home/jwdegee/raw/2015/3T_dots'
this_project_folder = '/home/jwdegee/colizoli/data'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

from Tools.Sessions import *
from Tools.Subjects.Subject import *
from Tools.Run import *
from Tools.Projects.Project import *

import pupil_data_analysis as pupil_data_analysis

# -----------------
# Comments:       -
# -----------------

subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']
nr_sessions = [4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4,]

## DESIGN = arousal x difficulty x hemifield x accuracy
## EVENTS = cue, choice, feedback

higherLevel = pupil_data_analysis.higherLevel(subjects=subjects, experiment_name='pupil_2AFC', project_directory=this_project_folder)
#######################################################

# ----------------------
# Output dataframes
# ----------------------
# higherLevel.dataframe_pupil_subjects(remove_omissions=False)      # outputs one dataframe for all trials for all subjects (pupil data only)
# higherLevel.dataframe_pupil_subjects(remove_omissions=True)       # outputs one dataframe for all trials for all subjects (pupil data only)
# higherLevel.dataframe_processITI()                                # ITIs and other condition information that was not sent to the eyetracker
# higherLevel.dataframe_process_motionEnergy()                      # add motion energy to pupil data frame (from MATLAB output)
# higherLevel.dataframe_pupil_event_related_subjects()              # per event of interest, outputs one np.array for all trials for all subjects on pupil time series
# higherLevel.dataframe_pupil_higher()                              # creates higher level dataframes for ANOVA input (pupil data only)
# higherLevel.dataframe_pupil_event_related_higher()                # splits time series pupil data into conditions (pupil data only)

## DEBUG extra subj_idx column
# higherLevel.dataframe_pupil_event_related_higher_regressRT()      # removes RT from the time courses
# higherLevel.dataframe_pupil_event_related_higher_regressME()      # does regression of motion energy onto pupil, saves betas

# ----------------------
# ANOVAs
# ----------------------
# higherLevel.run_anova_pupil()                 # ANOVAs on all conditions - pupil scalar DVs and RT





