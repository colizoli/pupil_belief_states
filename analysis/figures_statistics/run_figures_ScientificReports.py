#!/usr/bin/env python
# encoding: utf-8
"""
run_figures_ScientificReports.py

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

this_project_folder = '/home/data'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

import figures_ScientificReports as figures

# -----------------
# Comments:       -
# -----------------
# Run AFTER first and second level scripts for all tasks
# Motion energy computations - see Methods for reference (MATLAB scripts)

f = figures.figureClass(subjects=overlap_subjects, experiment_name='2AFC', project_directory=this_project_folder)
#######################################################

IV = 'coh_direction'
f.sdt_models()                    # competing models internal vs. external noise
f.sdt_models_subjects(IV=IV)      # competing models internal vs. external noise single subjects sigma
f.plot_sdt_models()               # competing models internal vs. external noise
f.plot_sdt_models_subject_predictions(IV=IV)      # competing models internal vs. external noise, single subjects sigma
f.urai_feedback_pupil_median()    # plots the feedback-locked pupil data from Urai et al experiment

for C in [True]:
    f.behavior(controlITI=C)                            # accuracy, RT
    f.pupil_results(controlITI=C, regressRT=False)      # pupil 3T, task vs. IRF responses
    f.RT_pupil_correlation(controlITI=C)                # plots the correlation between the RT and pupil (trial-wise and within conditions)
    f.plot_sdt_models_fits_coherence(controlITI=C)      # competing models internal vs. external noise, fit pupil to model predictions
    f.plot_sdt_models_fits_motion_energy(controlITI=C, binME=True)    # uses motion energy instead of condition categories
    f.control_exp(controlITI=C)                         # plot feedback responses main task vs. feedback correct/error responses control experiment
    f.pupil_results_motion_energy(IV='ME', controlITI=C, subjects=subjects_3T, regressRT=True)      # interaction plots binned by motion energy
    f.pupil_event_related_betas(controlITI=C, regressRT=True)           # computes the interaction term for the resp_locked BETAS time course, with RT regressed out, collapse over time
    f.regress_pupil_motion_energy(controlITI=C, regressRT=True)         # stats for regression models
    



