#!/usr/bin/env python
# encoding: utf-8
"""
first_level.py

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

import pupil_preprocessing
# from VisualSession import VisualSession

subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08', 'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15']
# Notes: sub-04 and sub-12 missing session 1 data
# Commented runs below had poor data quality

for which_subject in subjects:
    sessions = [1,2,3,4]
        
    subj_ind = subjects.index(which_subject) # subject index, not number
    
    if which_subject == 'sub-12' or which_subject == 'sub-04' :
        sessions = [2,3,4]
    
    edfs = []
    for s in sessions:
        
        def runWholeSession( rDA, session ):

            for r in rDA:
                thisRun = Run( **r )
                presentSession.addRun(thisRun)
            session.parcelateConditions()
            session.parallelize = True
            
            # ----------------------------
            # Pupil:                     -
            # ----------------------------
            
            # -----------------------
            # initialize pupil session:
            # -----------------------
            global edfs
            edfs.append( [rDA[i]['eyeLinkFilePath'] for i in range(len(rDA)) if rDA[i]['condition'] == 'task'] )
            if s == 4:
                edfs = list(np.concatenate(edfs))
                aliases = []
                for i in range(len(edfs)):
                    session = int(edfs[i].split('_s')[1][0])
                    aliases.append('2AFC_{}_{}'.format(i+1, session))
                print aliases
                subject = Subject(which_subject, '?', None, None, None)
                experiment = 1
                version = 2
                
                # -----------------------
                # Preprocessing:
                # -----------------------
                pupilPreprocessSession = pupil_preprocessing.pupilPreprocessSession(subject=subject, experiment_name='pupil_2AFC', experiment_nr=experiment, version=version, sample_rate_new=50, project_directory=this_project_folder)
                pupilPreprocessSession.import_raw_data(edf_files=edfs, aliases=aliases)
                pupilPreprocessSession.convert_edfs(aliases)
                # pupilPreprocessSession.delete_hdf5() # run if need to replace HDF5 files
                    # -----------------------
                    # Run MATLAB code here to fix MSG files
                    # -----------------------
                pupilPreprocessSession.import_all_data(aliases)
                for alias in aliases:
                    pupilPreprocessSession.process_runs(alias, artifact_rejection='not_strict', create_pupil_BOLD_regressor=False)
                    pass
                pupilPreprocessSession.process_across_runs(aliases, create_pupil_BOLD_regressor=False)
                ## to change pupil scalars, you don't need to rerun functions above
            
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-01_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-01_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-01_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-01_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-02_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r4.edf' ),
                            },
                        # {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                        #     'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r5.edf' ),
                        #     },
                        # {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                        #     'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-02_s2_r6.edf' ),
                        #     },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-02_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-02_s4_r6.edf' ),
                            },
                        ]

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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-03_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-03_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-03_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        # {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                        #     'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r1.edf' ),
                        #     },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-03_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
            
                # if s == 1:
                #     # NOTE WE HAD TECHNICAL PROBLEMS IN THIS SESSION, DO NOT INCLUDE IT.
                #         ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-04_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-04_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-04_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-05_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-05_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-05_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-05_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-06_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-06_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-06_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-06_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-07_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-07_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-07_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-07_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-08_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-08_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-08_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-08_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-09_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-09_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-09_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-09_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-10_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-10_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-10_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-10_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-10_s1_r5.edf' ),
                            },
                        ## Run 6 not acquired
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-10_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-10_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-10_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
                
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-11_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-11_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-11_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-11_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-11_s1_r5.edf' ),
                            },
                        ## Run 6 not acquired
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-11_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-11_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-11_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
            
                ## session 1 had technical difficulties, not included
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-12_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r4.edf' ),
                            }
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-12_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        # {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                        #     'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r1.edf' ),
                        #     },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-12_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-13_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-13_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-13_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-13_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
            
                if s == 1:
                    runDecisionArray = [
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-14_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-14_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-14_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-14_s4_r6.edf' ),
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
                presentProject = Project( '3T_2AFC', subject = presentSubject, base_dir = os.path.join(this_project_folder, 'data') )
                sessionID = '3T_2AFC' + presentSubject.initials
            
                sj_session1 = []
                sj_session2 = []
                sj_session3 = []
                sj_session4 = []
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
            
                if s == 1:
                    runDecisionArray = [
                        # Decision tasks session 1:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 1,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session1, 'eye', 'sub-15_s1_r6.edf' ),
                            },
                        ]
                if s == 2:
                    runDecisionArray = [
                        # Decision tasks session 2:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 2,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session2, 'eye', 'sub-15_s2_r6.edf' ),
                            },
                        ]
                if s == 3:
                    runDecisionArray = [
                        # Decision tasks session 3:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 3,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session3, 'eye', 'sub-15_s3_r6.edf' ),
                            },
                        ]
                if s == 4:
                    runDecisionArray = [
                        # Decision tasks session 4:
                        {'ID' : 1, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r1.edf' ),
                            },
                        {'ID' : 2, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r2.edf' ),
                            },
                        {'ID' : 3, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r3.edf' ),
                            },
                        {'ID' : 4, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r4.edf' ),
                            },
                        {'ID' : 5, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r5.edf' ),
                            },
                        {'ID' : 6, 'scanType': 'epi_bold', 'condition': 'task', 'session' : 4,
                            'eyeLinkFilePath': os.path.join(this_raw_folder, initials, sj_session4, 'eye', 'sub-15_s4_r6.edf' ),
                            },
                        ]

                # ----------------------
                # Initialise session   -
                # ----------------------
            
                runWholeSession( runDecisionArray, presentSession )

    