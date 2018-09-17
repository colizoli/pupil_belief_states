#!/usr/bin/env python
# encoding: utf-8
"""
Run.py

Created by Tomas Knapen on 2010-09-15.
Copyright (c) 2010 Tomas Knapen. All rights reserved.
"""

import os, sys, datetime
from subprocess import *
#from volumesAndSurfaces import *

from Tools.Sessions import *
from Operators.BehaviorOperator import *

class Run(object):
	def __init__(self, **kwargs ): #ID, condition, dataType, 
		"""
		run takes an ID, condition, dataType, rawDataFilePath
		"""
		# integer that will tell the run what number it is in the session
		self.indexInSession = None
		self.behaviorFile = None
		self.eyeLinkFile = None
		
		self.trialList = []
		
		for k,v in kwargs.items():
			setattr(self, k, v)		# here the object gets all the attributes listed in the arguments
			
		if not hasattr(self, 'condition'):
			self.condition = ''
		
		if hasattr(self, 'rawDataFilePath'): # datetime of this run is the creation time of the raw data file
			if os.path.isfile(self.rawDataFilePath)			:
				self.dateTime = os.path.getctime(self.rawDataFilePath)
			else:
				print 'rawDataFilePath %s is not file.' % self.rawDataFilePath
		elif hasattr(self, 'behaviorFile'):
			#			self.dateTime = os.path.getctime(self.behaviorFile)
			self.dateTime = datetime.date.today()
		elif hasattr(self, 'eyeFile'):
			self.dateTime = os.path.getctime(self.eyeFile)
	
	def addTrial(self, trial):
		"""docstring for addTrial"""
		trial.indexInRun = trialList.len()
		self.trialList.append(trial)
	
