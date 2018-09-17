#!/usr/bin/env python
# encoding: utf-8
"""
first_level_irf.py

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
this_project_folder = '/home/measure_irf'

analysisFolder = os.path.join(this_project_folder, 'analysis')
sys.path.append( analysisFolder )
sys.path.append( os.environ['ANALYSIS_HOME'] )

from Tools.Sessions import *
from Tools.Subjects.Subject import *
from Tools.Run import *
from Tools.Projects.Project import *

import pupil_preprocessing_irf

subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']

for which_subject in subjects:
    sessions = [1,2,3,4]
    
    if which_subject == 'sub-14' or which_subject == 'sub-15':
        sessions = [2,3,4]
    if which_subject == 'sub-02':
        sessions = [1,2,3]
        
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
            if (which_subject=='sub-02' and s == 3) or (which_subject != 'sub-02' and s==4): # if last session
                edfs = list(np.concatenate(edfs))
                aliases = []
                for i in range(len(edfs)):
                    session = int(edfs[i].split('_s')[1][0])
                    aliases.append('measureIRF_{}_{}'.format(i+1, session))
                print aliases
                subject = Subject(which_subject, '?', None, None, None)
                experiment = 1
                version = 2

                # preprocessing:
                pupilPreprocessSession = pupil_preprocessing_irf.pupilPreprocessSession(subject=subject, experiment_name='pupil_measureIRF', experiment_nr=experiment, version=version, sample_rate_new=50, project_directory=this_project_folder)
                pupilPreprocessSession.import_raw_data(edf_files=edfs, aliases=aliases)
                pupilPreprocessSession.convert_edfs(aliases)
                # pupilPreprocessSession.delete_hdf5() # run if need to replace HDF5 files
                ## Run MATLAB code here (MeasureIRF_MSG_FindReplace.m)
                pupilPreprocessSession.import_all_data(aliases)
                for alias in aliases:
                    pupilPreprocessSession.process_runs(alias, artifact_rejection='not_strict', create_pupil_BOLD_regressor=False)
                #     pass
                pupilPreprocessSession.process_across_runs(aliases, create_pupil_BOLD_regressor=False)
                ## missing first trials, and last pupil_cd for each participant!?
                            
        # for testing;
        if __name__ == '__main__':
########################################################################################################################################################################################################
        
            if which_subject == 'sub-01':
                # subject information
                initials = 'sub-01'
                firstName = 'sub-01'
                standardFSID = 'sub-01_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 9)
                    sj_session1 = 'sub-01_091115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 16)
                    sj_session2 = 'sub-01_161115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 27)
                    sj_session3 = 'sub-01_271115'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 04)
                    sj_session4 = 'sub-01_041215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-01_s1_r1_b1_2015-11-09_13-01-09.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-01_s2_r1_b1_2015-11-16_15-18-57.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-01_s3_r1_b1_2015-11-27_13-41-58.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-01_s4_r1_b1_2015-12-04_13-21-02.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-02':
                # subject information
                initials = 'sub-02'
                firstName = 'sub-02'
                standardFSID = 'sub-02_110412'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 9, 28)
                    sj_session1 = 'sub-02_280915'
                if s == 2:
                    sessionDate = datetime.date(2015, 10, 28)
                    sj_session2 = 'sub-02_281015'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 3)
                    sj_session3 = 'sub-02_031115'
                if s == 4:
                    sessionDate = datetime.date(2015, 11, 10)
                    sj_session4 = 'sub-02_101115'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-02_b1_s1_r1_2015-09-28_16-17-09.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-02_s2_r1_b1_2015-10-28_16-22-03.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-02_s3_r2_b1_2015-11-03_17-42-20.edf' ),
                            },
                        ]
                # if s == 4: # gets error on import_all_data
                #     runDecisionArray = [
                #         {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                #             'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-02_s4_r1_b1_2015-11-10_16-18-50.edf' ),
                #             },
                #         ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-03':
                # subject information
                initials = 'sub-03'
                firstName = 'sub-03'
                standardFSID = 'sub-03_190414'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 9, 25)
                    sj_session1 = 'sub-03_250915'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 3)
                    sj_session2 = 'sub-03_031115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 10)
                    sj_session3 = 'sub-03_101115'
                if s == 4:
                    sessionDate = datetime.date(2015, 11, 17)
                    sj_session4 = 'sub-03_171115'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-03_b1_s1_r1_2015-09-25_14-14-04.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-03_s2_r1_b1_2015-11-03_18-19-24.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-03_s3_r1_b1_2015-11-10_18-12-32.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-03_s4_r1_b1_2015-11-17_16-08-55.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-04':
                # subject information
                initials = 'sub-04'
                firstName = 'sub-04'
                standardFSID = 'sub-04_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 9, 25)
                    sj_session1 = 'sub-04_250915'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 12)
                    sj_session2 = 'sub-04_121115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 20)
                    sj_session3 = 'sub-04_201115'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 01)
                    sj_session4 = 'sub-04_011215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-04_b1_s1_r1_2015-09-25_12-34-35.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-04_s2_r1_b1_2015-11-12_10-05-17.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-04_s3_r1_b1_2015-11-20_11-52-27.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-04_s4_r1_b1_2015-12-01_11-56-41.edf' ),
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
                standardFSID = 'sub-05_310312'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 9)
                    sj_session1 = 'sub-05_091115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 16)
                    sj_session2 = 'sub-05_161115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 23)
                    sj_session3 = 'sub-05_231115'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 03)
                    sj_session4 = 'sub-05_031215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-05_s1_r1_b1_2015-11-09_15-26-50.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-05_s2_r1_b1_2015-11-16_11-49-23.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-05_s3_r1_b1_2015-11-23_11-57-28.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-05_s4_r1_b1_2015-12-03_11-28-40.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )



########################################################################################################################################################################################################
        
            if which_subject == 'sub-06':
                # subject information
                initials = 'sub-06'
                firstName = 'sub-06'
                standardFSID = 'sub-06_250514'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 13)
                    sj_session1 = 'sub-06_131115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 21)
                    sj_session2 = 'sub-06_211115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 26)
                    sj_session3 = 'sub-06_261115'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 01)
                    sj_session4 = 'sub-06_011215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-06_s1_r1_b1_2015-11-13_14-02-26.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-06_s2_r1_b1_2015-11-21_10-16-21.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-06_s3_r1_b1_2015-11-26_19-20-42.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-06_s4_r1_b1_2015-12-01_18-55-04.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

########################################################################################################################################################################################################
        
            if which_subject == 'sub-07':
                # subject information
                initials = 'sub-07'
                firstName = 'sub-07'
                standardFSID = 'sub-07_190414'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 4)
                    sj_session1 = 'sub-07_041115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 12)
                    sj_session2 = 'sub-07_121115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 17)
                    sj_session3 = 'sub-07_171115'
                if s == 4:
                    sessionDate = datetime.date(2015, 11, 26)
                    sj_session4 = 'sub-07_261115'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-07_s1_r1_b1_2015-11-04_18-31-23.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-07_s2_r1_b1_2015-11-12_14-22-46.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-07_s3_r1_b1_2015-11-17_14-20-37.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-07_s4_r1_b1_2015-11-26_09-25-25.edf' ),
                            },
                        ]
                
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-08':
                # subject information
                initials = 'sub-08'
                firstName = 'sub-08'
                standardFSID = 'sub-08_030215'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 12, 17)
                    sj_session1 = 'sub-08_171215'
                if s == 2:
                    sessionDate = datetime.date(2016, 01, 11)
                    sj_session2 = 'sub-08_110116'
                if s == 3:
                    sessionDate = datetime.date(2016, 01, 19)
                    sj_session3 = 'sub-08_190116'
                if s == 4:
                    sessionDate = datetime.date(2016, 01, 29)
                    sj_session4 = 'sub-08_290116'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-08_s1_r1_b1_2015-12-17_09-23-37.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-08_s2_r1_b1_2016-01-11_16-15-13.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-08_s3_r1_b1_2016-01-19_16-13-03.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-08_s4_r1_b1_2016-01-29_11-30-10.edf' ),
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
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 18)
                    sj_session1 = 'sub-09_181115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 26)
                    sj_session2 = 'sub-09_261115'
                if s == 3:
                    sessionDate = datetime.date(2015, 12, 10)
                    sj_session3 = 'sub-09_101215'
                if s == 4:
                    sessionDate = datetime.date(2016, 01, 28)
                    sj_session4 = 'sub-09_280116'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-09_s1_r1_b1_2015-11-18_16-02-37.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-09_s2_r1_b1_2015-11-26_16-29-34.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-09_s3_r2_b1_2015-12-10_20-18-28.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-09_s4_r1_b1_2016-01-28_14-59-48.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-10':
                # subject information
                initials = 'sub-10'
                firstName = 'sub-10'
                standardFSID = 'sub-10_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 11)
                    sj_session1 = 'sub-10_111115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 18)
                    sj_session2 = 'sub-10_181115'
                if s == 3:
                    sessionDate = datetime.date(2015, 12, 02)
                    sj_session3 = 'sub-10_021215'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 07)
                    sj_session4 = 'sub-10_071215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-10_s1_r1_b1_2015-11-11_12-02-48.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-10_s2_r1_b1_2015-11-18_11-58-37.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-10_s3_r1_b1_2015-12-02_16-25-52.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-10_s4_r1_b1_2015-12-07_13-25-20.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-11':
                # subject information
                initials = 'sub-11'
                firstName = 'sub-11'
                standardFSID = 'sub-11_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 12, 06)
                    sj_session1 = 'sub-11_061215'
                if s == 2:
                    sessionDate = datetime.date(2016, 01, 13)
                    sj_session2 = 'sub-11_130116'
                if s == 3:
                    sessionDate = datetime.date(2016, 01, 20)
                    sj_session3 = 'sub-11_200116'
                if s == 4:
                    sessionDate = datetime.date(2016, 01, 27)
                    sj_session4 = 'sub-11_270116'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-11_s1_r1_b1_2015-12-06_10-41-43.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-11_s2_r1_b1_2016-01-13_12-29-04.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-11_s3_r1_b1_2016-01-20_12-03-29.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-11_s4_r1_b1_2016-01-27_11-48-32.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-12':
                # subject information
                initials = 'sub-12'
                firstName = 'sub-12'
                standardFSID = 'sub-12_091009tk'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 11, 11)
                    sj_session1 = 'sub-12_111115'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 25)
                    sj_session2 = 'sub-12_251115'
                if s == 3:
                    sessionDate = datetime.date(2015, 12, 02)
                    sj_session3 = 'sub-12_021215'
                if s == 4:
                    sessionDate = datetime.date(2015, 12, 15)
                    sj_session4 = 'sub-12_151215'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-12_s1_r0_b1_2015-11-11_15-30-12.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-12_s2_r1_b1_2015-11-25_17-15-23.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-12_s3_r1_b1_2015-12-02_11-48-04.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-12_s4_r1_b1_2015-12-15_16-19-56.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-13':
                # subject information
                initials = 'sub-13'
                firstName = 'sub-13'
                standardFSID = 'sub-13_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 12, 04)
                    sj_session1 = 'sub-13_041215'
                if s == 2:
                    sessionDate = datetime.date(2015, 12, 11)
                    sj_session2 = 'sub-13_111215'
                if s == 3:
                    sessionDate = datetime.date(2016, 01, 8)
                    sj_session3 = 'sub-13_080116'
                if s == 4:
                    sessionDate = datetime.date(2016, 01, 18)
                    sj_session4 = 'sub-13_180116'
            
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
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'IRF_sub-13_s1_r1_b1_2015-12-04_15-19-42.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-13_s2_r1_b1_2015-12-11_15-48-27.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-13_s3_r1_b1_2016-01-08_16-17-41.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-13_s4_r1_b1_2016-01-18_15-05-41.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-14':
                # subject information
                initials = 'sub-14'
                firstName = 'sub-14'
                standardFSID = 'sub-14_081014'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 10, 01)
                    sj_session1 = 'sub-14_011015'
                if s == 2:
                    sessionDate = datetime.date(2015, 11, 04)
                    sj_session2 = 'sub-14_041115'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 12)
                    sj_session3 = 'sub-14_121115'
                if s == 4:
                    sessionDate = datetime.date(2015, 11, 20)
                    sj_session4 = 'sub-14_201115'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                # No session 1
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-14_s2_r1_b1_2015-11-04_16-28-33.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-14_s3_r1_b1_2015-11-12_16-14-57.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-14_s4_r1_b1_2015-11-20_13-49-42.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )


########################################################################################################################################################################################################
        
            if which_subject == 'sub-15':
                # subject information
                initials = 'sub-15'
                firstName = 'sub-15'
                standardFSID = 'sub-15_140316'
                birthdate = datetime.date( 1900, 01, 01 )
                labelFolderOfPreference = '2014_custom'
                presentSubject = Subject( initials, firstName, birthdate, standardFSID, labelFolderOfPreference )
                presentProject = Project( 'measure_irf', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = 'measure_irf' + presentSubject.initials
            
                if s == 1:
                    sessionDate = datetime.date(2015, 9, 26)
                    sj_session1 = 'sub-15_260915'
                if s == 2:
                    sessionDate = datetime.date(2015, 10, 31)
                    sj_session2 = 'sub-15_311015'
                if s == 3:
                    sessionDate = datetime.date(2015, 11, 07)
                    sj_session3 = 'sub-15_071115'
                if s == 4:
                    sessionDate = datetime.date(2015, 11, 14)
                    sj_session4 = 'sub-15_141115'
            
                presentSession = VisualSession(sessionID, sessionDate, presentProject, presentSubject)
            
                try:
                    os.mkdir(os.path.join(this_project_folder, 'data', initials))
                except OSError:
                    presentSession.logger.debug('output folders already exist')
            
                # ----------------------
                # Decision tasks:      -
                # ----------------------
            
                # No session 1
                if s == 2:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'IRF_sub-15_s2_r1_b1_2015-10-31_10-28-56.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'IRF_sub-15_s3_r1_b1_2015-11-07_10-30-52.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        {'ID' : 1, 'scanType': 'main_task', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'IRF_sub-15_s4_r1_b1_2015-11-14_10-17-03.edf' ),
                            },
                        ]
                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )
