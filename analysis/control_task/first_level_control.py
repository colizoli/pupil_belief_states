#!/usr/bin/env python
# encoding: utf-8
"""
first_level_control.py

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
this_project_folder = '/home/control'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

from Tools.Sessions import *
from Tools.Run import *

import pupil_data_analysis_control

# -----------------
# Comments:       -
# -----------------

subjects = ['sub-16','sub-17','sub-18','sub-19','sub-20','sub-21','sub-05','sub-22','sub-23','sub-24','sub-09','sub-25','sub-26','sub-27','sub-28']

for which_subject in subjects:
    sessions = [1]
    
    edfs = []
    
    for s in sessions:
        
        def runWholeSession( rDA, session ):
            for r in rDA:
                thisRun = Run( **r )
                presentSession.addRun(thisRun)
            session.parcelateConditions()
            session.parallelize = True
                        
            # initialize pupil session:
            global edfs
            edfs.append( [rDA[i]['eyeLinkFilePath'] for i in range(len(rDA)) if rDA[i]['condition'] == 'task'] )
            if s == 1:
                edfs = list(np.concatenate(edfs))
                aliases = []
                for i in range(len(edfs)):
                    session = int(edfs[i].split('_s')[1][0])
                    aliases.append('feedback_{}_{}'.format(i+1, session))
                print aliases
                subject = Subject(which_subject, '?', None, None, None)
                experiment = 1
                version = 2

                ## preprocessing:
                pupilPreprocessSession = pupil_data_analysis_control.pupilPreprocessSession(subject=subject, experiment_name='pupil_feedback', experiment_nr=experiment, version=version, sample_rate_new=50, project_directory=this_project_folder)
                pupilPreprocessSession.import_raw_data(edf_files=edfs, aliases=aliases)
                pupilPreprocessSession.convert_edfs(aliases)
                ## pupilPreprocessSession.delete_hdf5() # run if need to redo HDF5 files
                pupilPreprocessSession.import_all_data(aliases)
                for alias in aliases:
                    pupilPreprocessSession.process_runs(alias, artifact_rejection='not_strict', create_pupil_BOLD_regressor=False)
                    pass
                pupilPreprocessSession.process_across_runs(aliases, create_pupil_BOLD_regressor=False)
            
        # for testing;
        if __name__ == '__main__':

####################################################################################################################################################################################

            if which_subject == 'sub-16':
                # subject information
                initials = 'sub-16'
                firstName = 'sub-16'
                standardFSID = 'sub-16_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 21)
                    sj_session1 = 'sub-16_210617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-16_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################

            if which_subject == 'sub-17':
                # subject information
                initials = 'sub-17'
                firstName = 'sub-17'
                standardFSID = 'sub-17_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 29)
                    sj_session1 = 'sub-17_290617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-17_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


####################################################################################################################################################################################

            if which_subject == 'sub-18':
                # subject information
                initials = 'sub-18'
                firstName = 'sub-18'
                standardFSID = 'sub-18_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 8, 23)
                    sj_session1 = 'sub-18_230817'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-18_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-19':
                # subject information
                initials = 'sub-19'
                firstName = 'sub-19'
                standardFSID = 'sub-19_220617'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 22)
                    sj_session1 = 'sub-19_220617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-19_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-20':
                # subject information
                initials = 'sub-20'
                firstName = 'sub-20'
                standardFSID = 'sub-20_220617'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 22)
                    sj_session1 = 'sub-20_220617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-20_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )



########################################################################################################################################################################################################
        
            if which_subject == 'sub-21':
                # subject information
                initials = 'sub-21'
                firstName = 'sub-21'
                standardFSID = 'sub-21_220617'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []

                if s == 1:
                    sessionDate = datetime.date(2017, 6, 29)
                    sj_session1 = 'sub-21_290617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-21_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-05':
                # subject information
                initials = 'sub-05'
                firstName = 'sub-05'
                standardFSID = 'sub-05_180717'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 7, 18)
                    sj_session1 = 'sub-05_180717'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )                

########################################################################################################################################################################################################
        
            if which_subject == 'sub-22':
                # subject information
                initials = 'sub-22'
                firstName = 'sub-22'
                standardFSID = 'sub-22_220611'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 22)
                    sj_session1 = 'sub-22_220617'
          
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-22_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )    
                
########################################################################################################################################################################################################


            if which_subject == 'sub-23':
                # subject information
                initials = 'sub-23'
                firstName = 'sub-23'
                standardFSID = 'sub-23_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 10, 11)
                    sj_session1 = 'sub-23_111017'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-23_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-24':
                # subject information
                initials = 'sub-24'
                firstName = 'sub-24'
                standardFSID = 'sub-24_180711'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 7, 18)
                    sj_session1 = 'sub-24_180717'
    
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-24_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-09':
                # subject information
                initials = 'sub-09'
                firstName = 'sub-09'
                standardFSID = 'sub-09_250711'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 19)
                    sj_session1 = 'sub-09_190617'
                # if s == 2:
                #     sessionDate = datetime.date(2016, 2, 8)
                #     sj_session2 = 'sub-09_080216'

            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-25':
                # subject information
                initials = 'sub-25'
                firstName = 'sub-25'
                standardFSID = 'sub-25_220617'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 22)
                    sj_session1 = 'sub-25_220617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-25_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-26':
                # subject information
                initials = 'sub-26'
                firstName = 'sub-26'
                standardFSID = 'sub-26_220617'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 6, 22)
                    sj_session1 = 'sub-26_220617'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-26_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################


            if which_subject == 'sub-27':
                # subject information
                initials = 'sub-27'
                firstName = 'sub-27'
                standardFSID = 'sub-27_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 10, 11)
                    sj_session1 = 'sub-27_111017'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-27_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


####################################################################################################################################################################################

            if which_subject == 'sub-28':
                # subject information
                initials = 'sub-28'
                firstName = 'sub-28'
                standardFSID = 'sub-28_010100'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'feedback', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'feedback' + presentSubject.initials
            
                sj_session1 = []
                
                if s == 1:
                    sessionDate = datetime.date(2017, 7, 19)
                    sj_session1 = 'sub-28_190717'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                if s == 1:
                    runDecisionArray = [
                        # Measure IRF:
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r6.edf' ),
                            },
                        {'ID' : 7, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r7.edf' ),
                            },
                        {'ID' : 8, 'scanType': 'main_task', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-28_s1_r8.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
