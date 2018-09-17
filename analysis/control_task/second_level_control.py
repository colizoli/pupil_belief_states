#!/usr/bin/env python
# encoding: utf-8
"""
second_level_control.py

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

this_raw_folder = '/home/raw/'
this_project_folder = '/home/control/'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

from Tools.Sessions import *
from Tools.Subjects.Subject import *
from Tools.Run import *
from Tools.Projects.Project import *

import pupil_data_analysis_control

# -----------------
# Comments:       -
# -----------------
## DESIGN = feedback (red vs. green meaningless color)

subjects = ['sub-16','sub-17','sub-18','sub-19','sub-20','sub-21','sub-05','sub-22','sub-23','sub-24','sub-09','sub-25','sub-26','sub-27','sub-28']
nr_sessions = [1,1,1,1,1,1,1,1,1,1,1,1,1,1]

higherLevel = pupil_data_analysis_control.higherLevel(subjects=subjects, experiment_name='pupil_feedback', project_directory=this_project_folder)
#######################################################
## Output dataframes
# higherLevel.dataframe_pupil_subjects()                # outputs one dataframe for all trials for all subjects (pupil data only)
# higherLevel.dataframe_pupil_event_related_subjects()  # per event of interest, outputs one np.array for all trials for all subjects 
# higherLevel.dataframe_pupil_event_related_higher()    # splits time series pupil data into conditions (pupil data only)





