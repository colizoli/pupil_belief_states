#!/usr/bin/env python
# encoding: utf-8
"""
second_level_irf.py

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

this_raw_folder = '/home/jwdegee/raw/2017/measure_irf'
this_project_folder = '/home/jwdegee/colizoli/measure_irf'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

from Tools.Sessions import *
from Tools.Subjects.Subject import *
from Tools.Run import *
from Tools.Projects.Project import *

import pupil_data_analysis_irf

# -----------------
# Comments:       -
# -----------------
## DESIGN = sound > push a button

subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']
nr_sessions = [4,4,4,4,4,4,4,4,4,4,4,4,4,3,3]

higherLevel = pupil_data_analysis_irf.higherLevel(subjects=subjects, experiment_name='pupil_measureIRF', project_directory=this_project_folder)
#######################################################
## Output dataframes
# higherLevel.dataframe_pupil_subjects()                # outputs one dataframe for all trials for all subjects
# higherLevel.dataframe_IRF_deconvolution(plot_subjs=True)             # Does the FIR deconvolution on IRF (CHECK XLIM in PLOTS!!)

