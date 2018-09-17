#!/usr/bin/env python
# encoding: utf-8
"""
Session.py

Created by Tomas HJ Knapen on 2009-11-26.
Copyright (c) 2009 TK. All rights reserved.
"""

import os, sys, pickle, math
from subprocess import *
import datetime

import scipy as sp
import numpy as np
import matplotlib.pylab as pl
from matplotlib.backends.backend_pdf import PdfPages
from nifti import *

import glob

import pp
import logging, logging.handlers, logging.config

from ..log import *
from ..Run import *
from ..Operators.Operator import *
from ..Operators.CommandLineOperator import *
from ..Operators.BehaviorOperator import *
# from ..Operators.ArrayOperator import *
from ..Operators.EyeOperator import *
from IPython import embed as shell
from joblib import Parallel, delayed

from ..Operators.HDFEyeOperator import HDFEyeOperator

from IPython import embed as shell

class PathConstructor(object):
	"""
	FilePathConstructor is an abstract superclass for sessions.
	It constructs the file and folder naming hierarchy for a given session.
	All file naming and calling runs through this class.
	"""
	def __init__(self):
		self.fileNameBaseString = self.dateCode
	
	def base_dir(self):
		"""
		base_dir returns the path in which all data of this session
		is located. this path is located within this observer's
		folder which, in turn, is located within this project's folder
		"""
		return os.path.join(self.project.base_dir, self.subject.initials, self.dateCode)
	
	def make_base_dir(self):
		"""
		make_base_dir creates the path in which  all data of this session
		will be located. it will attempt to build the folder tree towards
		this path, but will run into trouble if even the folder containing
		self.project.base_dir doesn't exist
		"""
		if not os.path.isdir(self.base_dir()):
			try:
				os.mkdir(self.project.base_dir)
			except OSError:
				pass
			try:
				os.mkdir(os.path.join(self.project.base_dir, self.subject.initials))
			except OSError:
				pass
			try:
				os.mkdir(self.base_dir())
			except OSError:
				pass
	
	def stageFolder(self, stage):
		"""
		stageFolder returns the path associated with a certain analysis stage
		such as the subfolders 'raw/mri' or 'processed/eyelink' within the session's base_dir.
		"""
		return os.path.join(self.base_dir(), stage)
	
	def runFolder(self, stage, run):
		"""
		runFolder returns the folder path, within a certain analysis stage (e.g. 'raw/mri/'),
		associated with a particular run (e.g. the run whose ID is 1) that belongs to a certain condition (e.g. 'mapper').
		the return object of that example would be 'raw/mri/mapper/1'
		"""
		return os.path.join(self.stageFolder(stage), run.condition, str(run.ID))
	
	def conditionFolder(self, stage, run):
		"""docstring for runFolder"""
		return os.path.join(self.stageFolder(stage), run.condition)
	
	def runFile(self, stage = None, run = None, postFix = [], extension = standardMRIExtension, base = None):
		"""
		runFile returns the file path, within a certain analysis stage (e.g. 'raw/mri'),
		associated with a particular run (e.g. 1) that belongs to a certain condition (e.g. 'mapper').
		If 'stage' is left blank, then only the filename, rather than the full path, is returned.
		postFix is typically something like ['mcf'], for getting the motion corrected path, but
		can also be an array of strings, which will then be concatenated with '_' separators.
		
		runFile is more flexible than runFolder, because the run
		can have many different relevant files, for instance a motion corrected file and a non-motion
		corrected file, all within the same folder
	
		example of usage 1 (JB, dec 22 2014: I don't quite understand this first one):
		the raw mri file for run index X can be obtained with
		self.runFile('raw/mri', postFix = [str(self.runList[X])], base = self.subject.initials)
		
		example of usage 2:
		the motion corrected file of the run at index X in runList can be obtained with
		self.runFile('processed/mri', run = self.runList[X], postFix = ['mcf'])
		if self.fileNameBaseString for this session is 'QQ_101214', this run's ID and 
		condition are 'mapper' and 1, respectively, and standardMRIExtension (defined in Operator.py)
		is '.nii.gz', then the result, relative to self.base_dir(),
		is: 'processed/mri/mapper/1/QQ_101214_1_mcf.nii.gz'
		
		"""
		
		fn = ''
		if not base:
			fn += self.fileNameBaseString
		else:
			fn += base
		if run:
			fn += '_' + str(run.ID)
		for pf in postFix:
			fn += '_' + pf
		fn += extension
		
		if stage is None:
			return fn
		elif run and stage.split('/')[0] == 'processed':
			return os.path.join(self.runFolder(stage, run), fn)
		else:
			return os.path.join(self.stageFolder(stage), fn)
	
	def createFolderHierarchy(self):
		"""
		createFolderHierarchy creates the folder tree for a session. It needs for at least
		the folder enclosing the project folder self.project.base_dir to exist,
		and will build from there: project/observer/session/[further subfolders].
		"""
		rawFolders = ['raw/mri', 'raw/behavior', 'raw/eye', 'raw/hr']
		self.processedFolders = ['processed/mri', 'processed/behavior', 'processed/eye', 'processed/hr']
		conditionFolders = np.concatenate((self.conditionList, ['log','figs','masks','masks/stat','masks/anat','reg','surf','scripts']))
		
		
		self.make_base_dir()
		# assuming baseDir/raw/ exists, we must make processed
		if not os.path.isdir(os.path.join(self.base_dir(), 'processed') ):
			os.mkdir(os.path.join(self.base_dir(), 'processed'))
		if not os.path.isdir(os.path.join(self.base_dir(), 'raw') ):
			os.mkdir(os.path.join(self.base_dir(), 'raw'))
		
		
		# create folders for processed data
		for pf in self.processedFolders:
			if not os.path.isdir(self.stageFolder(pf)):
				os.mkdir(self.stageFolder(pf))
			# create condition folders in each of the processed data folders and also their surfs
			for c in conditionFolders:
				 if not os.path.isdir(self.stageFolder(pf+'/'+c)):
					os.mkdir(self.stageFolder(pf+'/'+c))
					if pf == 'processed/mri':
						if not os.path.isdir(os.path.join(self.stageFolder(pf+'/'+c), 'surf')):
							os.mkdir(os.path.join(self.stageFolder(pf+'/'+c), 'surf'))
			# create folders for each of the runs in the session and their surfs. NB:
			# these will only be created within the condition folder indicated by 
			# each Run object (i.e. associated with the condition that the run belongs to).
			for rl in self.runList:
				if not os.path.isdir(self.runFolder(pf, run = rl)):
					os.mkdir(self.runFolder(pf, run = rl))
					if pf == 'processed/mri':
						if not os.path.isdir(os.path.join(self.runFolder(pf, run = rl), 'surf')):
							os.mkdir(os.path.join(self.runFolder(pf, run = rl), 'surf'))
						if not os.path.isdir(os.path.join(self.runFolder(pf, run = rl), 'masked')):
							os.mkdir(os.path.join(self.runFolder(pf, run = rl), 'masked'))
	

class Session(PathConstructor):
	"""
	Session is an object that contains all the analysis steps 
	for analyzing an entire session. The basic class contains the base level analyis and preparations, 
	such as putting the files in place and setting up the runs. 
	Often-used analysis steps include registration with an anatomical, and motion correction of the functionals.
	"""
	def __init__(self, ID, date, project, subject, parallelize = False, loggingLevel = logging.DEBUG, name_appendix = '', **kwargs):
		self.ID = ID
		self.date = date
		self.project = project
		self.subject = subject
		self.runList = []
		self.name_appendix = name_appendix
		self.dateCode = subject.initials + '_' + ('0'+str(self.date.day))[-2:] + ('0'+str(self.date.month))[-2:] + str(self.date.year)[-2:] + self.name_appendix
		self.parallelize = parallelize
		self.loggingLevel = loggingLevel
		for k,v in kwargs.items():
			setattr(self, k, v)
		
		super(Session, self).__init__()
		
		# add logging for this session
		# sessions create their own logging file handler
		self.logger = logging.getLogger( self.__class__.__name__ )
		self.logger.setLevel(self.loggingLevel)
		if os.path.isdir(self.stageFolder(stage = 'processed/mri/log')):
			addLoggingHandler( logging.handlers.TimedRotatingFileHandler( os.path.join(self.stageFolder(stage = 'processed/mri/log'), 'sessionLogFile.log'), when = 'H', delay = 2, backupCount = 10), loggingLevel = self.loggingLevel )
		else:
			addLoggingHandler( logging.handlers.TimedRotatingFileHandler( os.path.join(self.stageFolder(stage = 'raw'), 'firstSessionSetupLogFile.log'), when = 'H', delay = 2, backupCount = 10), loggingLevel = self.loggingLevel )
		loggingLevelSetup()
		for handler in logging_handlers:
			self.logger.addHandler(handler)
		# self.logger.info('starting analysis of session ' + str(self.ID))
	
	def addRun(self, run):
		"""
		addRun adds a run to a session's run list
		It creates/updates the following attributes of self:
		the list runList, containing all Run objects associated with self;
		the list conditionList, containing all unique condition attributes among those Run objects;
		the list scanTypeList, containing all unique scanType attributes among those Run objects;
		and various other attributes via the parcelateConditions() method (see there)
		"""
		
		run.indexInSession = len(self.runList)
		self.runList.append(run)
		# recreate conditionList
		self.conditionList = list(np.unique(np.array([r.condition for r in self.runList])))
		self.scanTypeList = list(np.unique(np.array([r.scanType for r in self.runList])))
		
		self.parcelateConditions()
	
	def parcelateConditions(self):
		"""
		parcelateConditions creates/updates the following attributes of self:
		the dict scanTypeDict, of which each key-value pair indicates a possible value for the scanType attribute
		of the Run objects of self's runList, and the values of the indexInSession arguments of those Run objects 
		that are associated with that scanType value;
		the list conditions, containing all unique condition attributes among the Run objects in runList. This appears identical to self.conditionList;
		the dict conditionDict, analogous to scanTypeDict but for condition attributes scanType attributes
		"""
		
		# conditions will vary across experiments - this one will be amenable in subclasses,
		# but these are the principal types of runs. For EPI runs conditions will depend on the experiment.
		self.scanTypeDict = {}
		if 'epi_bold' in self.scanTypeList:
			self.scanTypeDict.update({'epi_bold': [hit.indexInSession for hit in filter(lambda x: x.scanType == 'epi_bold', [r for r in self.runList])]})
		if 'inplane_anat' in self.scanTypeList:
			self.scanTypeDict.update({'inplane_anat': [hit.indexInSession for hit in filter(lambda x: x.scanType == 'inplane_anat', [r for r in self.runList])]})
		if '3d_anat' in self.scanTypeList:
			self.scanTypeDict.update({'3d_anat': [hit.indexInSession for hit in filter(lambda x: x.scanType == '3d_anat', [r for r in self.runList])]})
		if 'dti' in self.scanTypeList:
			self.scanTypeDict.update({'dti': [hit.indexInSession for hit in filter(lambda x: x.scanType == 'dti', [r for r in self.runList])]})
		if 'spectro' in self.scanTypeList:
			self.scanTypeDict.update({'spectro': [hit.indexInSession for hit in filter(lambda x: x.scanType == 'spectro', [r for r in self.runList])]})
		if 'field_map' in self.scanTypeList:
			self.scanTypeDict.update({'field_map': [hit.indexInSession for hit in filter(lambda x: x.scanType == 'field_map', [r for r in self.runList])]})
		
#		print self.scanTypeDict
		self.conditions = np.unique(np.array([r.condition for r in self.runList]))
		self.conditionDict = {}
		for c in self.conditions:
			if c != '':
				self.conditionDict.update({c: [hit.indexInSession for hit in filter(lambda x: x.condition == c, [r for r in self.runList])]})
		
			
	def import_all_edf_data(self, aliases):
		"""import_all_data loops across the aliases of the sessions and converts the respective edf files, adds them to the self.ho's hdf5 file. """
		for r in self.runList:
			if r.indexInSession in self.scanTypeDict['epi_bold']:
				run_name = os.path.split(self.runFile(stage = 'processed/eye', run = r, extension = ''))[-1]
				ho = HDFEyeOperator(self.runFile(stage = 'processed/eye', run = r, extension = '.hdf5'))
				edf_file = subprocess.Popen('ls ' + self.runFolder(stage = 'processed/eye', run = r) + '/*.edf', shell=True, stdout=PIPE).communicate()[0].split('\n')[0]
				ho.add_edf_file(edf_file)
				ho.edf_message_data_to_hdf(alias = run_name)
				ho.edf_gaze_data_to_hdf(alias = run_name)
	
	def setupFiles(self, rawBase, process_eyelink_file = True, date_format = None):
		"""
		When all runs are listed in the session, 
		the session will be able to distill what conditions are there 
		and setup the folder hierarchy and copy the raw image files into position.
		The folder within which the hierarchy will be built, is indicated by the
		base_dir attribute of self.project.
		
		Depending on settings, setupFiles will also process files: 
		nii.gz from par/rec and hdf5 from edf. NB: the par/rec->nii.gz
		conversion is not currently supported; one is supposed to have done 
		that conversion beforehand using e.g. Parrec2nii or r2agui,
		and use the .nii.gz path as r.rawDataFilePath
		"""
		
		if not os.path.isfile(self.runFile(stage = 'processed/behavior', run = self.runList[0] )):
			self.logger.info('creating folder hierarchy')
			self.createFolderHierarchy()
		
		for r in self.runList:
			if hasattr(r, 'rawDataFilePath'):
				if os.path.splitext(r.rawDataFilePath)[-1] == '.PAR':	#if the rawDataFilePath of the Run object indicates a .par file, then convert to nifti
					self.logger.info('converting par/rec file %s into nii.gz file', r.rawDataFilePath)
					prc = ParRecConversionOperator( self.runFile(stage = 'raw/mri', postFix = [str(r.ID)], base = rawBase, extension = '.PAR' ) )
					prc.configure()
					prc.execute()
					if r.indexInSession in self.scanTypeDict['epi_bold']:
						# address slope and intercept issues
						f = open(self.runFile(stage = 'raw/mri', postFix = [str(r.ID)], base = rawBase, extension = '.PAR' ), 'r')
						fr = f.readlines()
						# column 13 of PAR file is slope - assuming it is identical for the whole file.
						slope = fr[100].split()[12]
						# dcm2nii creates weird file name additions like the f in front of 
						niiFile = NiftiImage(self.runFile(stage = 'raw/mri', postFix = [str(r.ID)], base = rawBase ))
						niiFile.setSlope(slope)
						niiFile.save()
				self.logger.info('place nii files in hierarchy')
				# copy raw files
				ExecCommandLine('cp ' + r.rawDataFilePath + ' ' + self.runFile(stage = 'processed/mri', run = r ) )
			# behavioral files will be copied during analysis
			if hasattr(r, 'eyeLinkFilePath'):
				elO = EyelinkOperator(r.eyeLinkFilePath, date_format = date_format)
				ExecCommandLine('cp ' + os.path.splitext(r.eyeLinkFilePath)[0] + '.* ' + self.runFolder(stage = 'processed/eye', run = r ) )
				if process_eyelink_file:
					elO.processIntoTable(hdf5_filename = self.runFile(stage = 'processed/eye', run = r, extension = '.hdf5'), compute_velocities = False, check_answers = False) #a lot happens in this line: the edf file is parsed into .hdf5 on the basis of messages sent to the eyelink during the experiment
			if hasattr(r, 'rawBehaviorFile'):
				ExecCommandLine('cp ' + r.rawBehaviorFile.replace('|', '\|') + ' ' + self.runFile(stage = 'processed/behavior', run = r, extension = '.dat' ) )
			if hasattr(r, 'physiologyFile'):
				ExecCommandLine('cp ' + r.physiologyFile.replace('|', '\|') + ' ' + self.runFile(stage = 'processed/hr', run = r, extension = '.log' ) )
	
