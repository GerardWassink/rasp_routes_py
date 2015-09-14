#!/usr/bin/python

# ------------------------------------------------------------------------
# Library		:	gaw_logging.py
# Author		:	Gerard Wassink
# Date			:	14 september 2015
#
# Description	:	offers objectified methods for logging and the ability
#					to determine which level one wants to see
#
# Methods
#	----- name ----		--- description ---		--- parameters ---
# 	__init__			constructor				loglevel
# 	logError			logs errors				message text
# 	logWarning			logs warnings			message text
# 	logInformational	logs info message		message text
#	logReport			prints # per type		()
#
# ------------------------------------------------------------------------
# 						GNU LICENSE CONDITIONS
# ------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------
#				Copyright (C) 2015 Gerard Wassink
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# class definition for logging events
# ------------------------------------------------------------------------
class gaw_logging:
	def __init__(self, level):
		self.errors = 0
		self.warnings = 0
		self.informationals = 0
		self.logLevel = level	# 3 = error,, 2 = warning,
								# 1 = informational, 0 = none

	def	logError(self, text):
		if self.logLevel > 2:
			print "E - " + text
		self.errors +=1
		
	def	logWarning(self, text):
		if self.logLevel > 1:
			print "W - " + text
		self.warnings +=1
		
	def	logInformational(self, text):
		if self.logLevel > 0:
			print "I - " + text
		self.informationals +=1
		
	def logReport(self):
		if self.logLevel > 0:
			print "Logging report:"
			if self.logLevel > 2: print "	# errors:", self.errors
			if self.logLevel > 1: print "	# warnings:", self.warnings
			if self.logLevel > 0: print "	# informationals:", self.informationals

