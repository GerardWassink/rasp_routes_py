#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	rasp_routes.c
# Author		:	Gerard Wassink
# Date			:	4 september 2015
#
# Function		:	accept pushbuttons of tracks and consequently
#					set turnouts for a model train layout
#					Two buttons on each end of a route must be
#					pushed to activate a route
#
#					spurs, turnouts and routes in config file
#
#					See the README file for specifics
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

from Adafruit_PWM_Servo_Driver import PWM
import RPi.GPIO as GPIO
import time
import re



# ------------------------------------------------------------------------
# Global variables and default values
# ------------------------------------------------------------------------

								# values concerning servos' and servo HAT
board = 0x40					# default board value
freq = 50						# frequency for PWM
servoMin = 210  				# Min pulse length out of 4096 (~ 10ms)
servoMax = 400  				# Max pulse length out of 4096 (~ 20ms)
speed = 0.2						# servo moving speed

CLOSED = 0
THROWN = 1

								# Initialise the PWM device using the 
								# default address (defined above)
								# Uncomment the line you want, 
								# with, or without debugging
#pwm = PWM(board, debug=True)
pwm = PWM(board)



# ------------------------------------------------------------------------
# class definition for Layout object
# ------------------------------------------------------------------------
class layout:
	def __init__(self, x1):
		self.name = x1
		
	def setName(self, name):
		self.name = name


# ------------------------------------------------------------------------
# class definition for logging events
# ------------------------------------------------------------------------
class logging:
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


# ------------------------------------------------------------------------
# class definition for input events
# ------------------------------------------------------------------------
class inputEvent:
	def __init__(self):			# event empty means both inputs are -1
		self.input1 = -1
		self.input2 = -1

								# event occurred, input gpio specified
	def event(self, val):
		print "I - event for input:", val

								# did we have it already?
		if self.input1 == val or self.input2 == val:
			print "I - already got it!"
		 
								# input1 still empty? sore it there
		elif self.input1 == -1:
			self.input1 = val

								# no, but input2 empty? sore it there
		elif self.input2 == -1:
			self.input2 = val

								# two inputs received
								# input 1 > 2? switch them around
			if self.input1 > self.input2:
				t = self.input1
				self.input1 = self.input2
				self.input2 = t

			print "I - Triggering event for", self.input1, self.input2

								# look for valid route
			found = 0
			for r in routeList:
				if r.input1 == self.input1 and r.input2 == self.input2:

								# valid route found, set route
					found = 1
					r.setRoute()
					break		# out of for loop

								# valid route not found, clear event
			if found == 0:
				print "E - invalid combination of inputs, try again"
				self.reset()

		else:
								# event when both full, should not happen
			print "W - event occurred, both inputs already set. enter inputs again please"
			self.reset()


	def reset(self):
		self.input1 = -1
		self.input2 = -1
	
	
	def status(self):
		print "I - Status of events:"
		if self.input1 != -1:
			print "I - input 1 =", self.input1
		else:
			print "I - status is blank"
		if self.input2 != -1:
			print "I - input 2 =", self.input2


# ------------------------------------------------------------------------
# class definition for turnout objects
# ------------------------------------------------------------------------
class turnout:
	def __init__(self, x1, x2, x3, x4, x5, x6):
		self.id = x1
		self.board = x2
		self.channel = x3
		self.posclos = x4
		self.posthro = x5
		self.name = x6
		self.setClosed()

								# Set the pulse-width value for this
								# turnout, corresponding with it's 
								# closed position
	def setClosed(self):
		global board, pwm, freq
								# When this turnout board differs from
								# previous, than change working board
		if self.board != board:
			board = self.board		# remember used board
			pwm = PWM(self.board)	# set board to be used
			pwm.setPWMFreq(freq)	# just to be sure, set frequency

									# do it:
		pwm.setPWM(self.channel, 0, self.posclos)
		self.state = CLOSED
#		time.sleep(0.2)
	
	
								# Set the pulse-width value for this
								# turnout, corresponding with it's 
								# thrown position
	def setThrown(self):
		global board, pwm, freq
								# When this turnout board differs from
								# previous, than change working board
		if self.board != board:
			board = self.board		# remember used board
			pwm = PWM(self.board)	# set board to be used
			pwm.setPWMFreq(freq)	# just to be sure, set frequency

									# do it:
		pwm.setPWM(self.channel, 0, self.posthro)
		self.state = THROWN
#		time.sleep(0.2)


# ------------------------------------------------------------------------
# class definition for input objects
# ------------------------------------------------------------------------
class input:
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.gpio = x2
		self.name = x3
		self.inpval = 0

								# Setup this object's GPIO as an input line
								# with pull-up
	def setup(self):
		GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)


								# Read the current value os this object's
								# GPIO line
	def getval(self):
		self.inpval = GPIO.input(self.gpio)


# ------------------------------------------------------------------------
# class definition for route objects
# ------------------------------------------------------------------------
class route:
	def __init__(self, x1, x2, x3, x4):
		self.id = x1
		self.input1 = x2
		self.input2 = x3
		self.settings = x4

	def setRoute(self):
		print "setting route from", self.input1, "to", self.input2, "-", self.settings
		tn = 0
		for s in self.settings:
			s = s.upper()
			if s == 'T':
				for t in turnoutList:
					if t.id == tn:
						if t.state != THROWN: t.setThrown()
						break
			elif s == 'C':
				for t in turnoutList:
					if t.id == tn:
						if t.state != CLOSED: t.setClosed()
						break
			tn += 1
			

# ------------------------------------------------------------------------
# lists to hold objects of various classes
# ------------------------------------------------------------------------
turnoutList = []
inputList = []
routeList = []

inpEvent = inputEvent()

logger = logging(3)

myLayout = layout("rasp_routes_py")


# ------------------------------------------------------------------------
# parse lines of type Turnout
# ------------------------------------------------------------------------
def parseTurnoutLine(line, tid, lc):
							# break down Turnout line and create new turnout
							# object in list of turnouts
	m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)", line)
	if m:
		id = str(tid)

		base = m.group(1)
		if base == '':
			base = '64'
			logger.logInformational("board not specified in Turnout line " + str(lc) + \
				"- default of 64 substituted")
	
		chan = m.group(2)
		if chan == '':
			chan = '0'
			logger.logInformational("channel not specified in Turnout line " + str(lc) + \
				"- default of 0 substituted")
	
		posclos = m.group(3)
		if posclos == '':
			posclos ='210'
			logger.logInformational("posclos not specified in Turnout line " + str(lc) + \
				"- default of 210 substituted")
	
		posthro = m.group(4)
		if posthro == '':
			posclos ='400'
			logger.logInformational("posthro not specified in Turnout line " + str(lc) + \
				"- default of 400 substituted")
	
		tname = m.group(5)
		if tname == '':
			tname = "T" + id
			logger.logInformational("name not specified in Turnout line " + str(lc) + \
				"- default of:" + tname + " substituted")
	
		turnoutList.append(turnout( \
					int(id), \
					int(base), \
					int(chan), \
					int(posclos), \
					int(posthro), \
					tname ) )
		return True
	else:
		logger.logWarning("Syntax error in Turnout line " + str(lc) + \
				", line not processed")
		return False


# ------------------------------------------------------------------------
# parse lines of type Input
# ------------------------------------------------------------------------
def parseInputLine(line, iid, lc):
								# break down Input line and create new input
								# object in list of inputs
	m = re.match("[Ii].*[:](.*)[:](.*)", line)
	if m:
		id = str(iid)
		
		inputList.append(input(int(iid), \
					int(m.group(1)), \
					m.group(2) ) )
		return 1
	else:
		logger.logWarning("Syntax error in Input line " + str(lc) + \
				", line not processed")
		return 0


# ------------------------------------------------------------------------
# parse lines of type Route
# ------------------------------------------------------------------------
def parseRouteLine(line, rid, lc):
								# break down Route line and create new route
								# object in list of routes
	m = re.match("[Rr].*[:](.*)[:](.*)[:](.*)", line)
	if m:
		id = str(rid)

		inp1 = m.group(1)
		if inp1 == '':
			inp1 = '0'
			logger.logInformational("input1 not specified in Route line " + str(lc) + \
				"- default of 0 substituted")
	
		inp2 = m.group(2)
		if inp2 == '':
			inp2 = '0'
			logger.logInformational("input2 not specified in Route line " + str(lc) + \
				"- default of 0 substituted")
	
		routeList.append(route(int(rid), \
					int(inp1), \
					int(inp2), \
					m.group(3) ) )
		return 1
	else:			# line type not defined
		logger.logWarning("Syntax error in Route line " + str(lc) + \
				", line not processed")
		return 0


# ------------------------------------------------------------------------
# parse lines of type Name
# ------------------------------------------------------------------------
def parseNameLine(line, lc):
							# break down Name line
	m = re.match("[Nn].*[:](.*)", line)
	if m:
		myLayout.setName((m.group(1)))
	else:
		logger.logWarning("Syntax error in Name line " + str(lc) + \
				", line not processed")



# ------------------------------------------------------------------------
# read and process the configuration file
# ------------------------------------------------------------------------
def read_config_file():
	global name
	res = True
	
	print "--------------------------------------------------------------------------------"
	print "Welcom to " + myLayout.name
	print "--------------------------------------------------------------------------------"
	print ""
	print "Reading and checking configuration file"

	errors = 0
	warnings = 0
	informationals = 0
		
	lc = 1						# set line count
	
	tid = 0						# set Turnout id count
	iid = 0						# set Input id count
	rid = 0						# set Route id count

	with open("rasp_routes_py.ini", "r") as myfile:

		for line in myfile:		# read next line
	
			line = line.rstrip()	# strip all spaces from right side

			if (len(line) > 0):	# empty line?

								# get first character to determine line type
				m = re.match("(.).*", line)
				if m: type = (m.group(1))	# Isolate type of line
	
								# Is this a 'turnout' line?
				if (type == "T" or type == "t"):
					if (parseTurnoutLine(line, tid, lc)): tid += 1

								# Is this an 'input' line?
				elif (type == "I" or type == "i"):
					if (parseInputLine(line, iid, lc)): iid += 1

								# Is this a 'route' line?
				elif (type == "R" or type == "r"):
					if (parseRouteLine(line, rid, lc)): rid += 1

								# Is this a 'name' line?
				elif (type == "N" or type == "n"):
					parseNameLine(line, lc)

								# Is this NOT a comment line?
				elif (type != "#"):
					logger.logWarning("Invalid line type in line" + str(lc))

								# increment line count
			lc = lc+1

	checkConfigLists()			# check for errors after building lists

	logger.logReport()			# report # messages per type

	if logger.errors == 0:
		logger.logInformational("No errors found, processing continues")
	else:
		logger.logError("rasp_routes_py stopping due to errors " + \
			"in configuration file")
		exit(1)
	
	print "--------------------------------------------------------------------------------"
	print "Welcome to " + myLayout.name
	print "--------------------------------------------------------------------------------"
	
	intitialize_inputs()

	return res


# ------------------------------------------------------------------------
# check lists after reading config file
# ------------------------------------------------------------------------
def checkConfigLists():
								# after reading, check lists for mismatching ID's
								# and other possible errors
								
								# turnout list ID's
	for t in turnoutList:
		if t.posclos < 210:
			logger.logInformational("closed value for turnout '" + t.name + \
				"' less than 210, only proceed if this is intentional")
		if t.posthro > 400:
			logger.logInformational("thrown value for turnout '" + t.name + \
				"' greater than 400, only proceed if this is intentional")
	
								# input list ID's
	for i in inputList:
		if i.gpio == 2 or i.gpio == 3:
			logger.logError("port 2 or 3 use for input '" + i.name + \
				"' during I2C servo operation, program will end after check")
	
								# route list ID's
#	for r in routeList:
								# no checks yet


# ------------------------------------------------------------------------
# re-read config file and setup again
# ------------------------------------------------------------------------
def refresh_config():
	global turnoutList
	global inputList
	global routeList
	
								# before refreshing, remove event triggers
	for i in inputList:
		i.setup()
		GPIO.remove_event_detect(i.gpio)

								# nullify lists 
	turnoutList = []
	inputList = []
	routeList = []

								# re-read config file
	if (read_config_file()):
		print "I - Confiugration refrreshed"


# ------------------------------------------------------------------------
# report values from config file
# ------------------------------------------------------------------------
def report_config_file():
	print ""
	print "# --- Turnout list ---"
	for t in turnoutList:
		print "I - id=", t.id, "board=", t.board, \
		"channel=", t.channel, "posclos=", t.posclos, \
		"posthro=", t.posthro, "name=", t.name
	print ""
	print "# --- Input list ---"
	for i in inputList:
		print "I - id=", i.id, "gpio=", i.gpio, "name=", i.name
	print ""
	print "# --- Route list ---"
	for r in routeList:
		print "I - id=", r.id, "input1=", r.input1, "input2=", r.input2, \
			"settings=", r.settings
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for inputs
# ------------------------------------------------------------------------
def report_inputs():
	print ""
	print "# --- Input list ---"
	for i in inputList:
		print "I - id=", i.id, "gpio=", i.gpio, "name=", i.name
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for routes
# ------------------------------------------------------------------------
def report_routes():
	print ""
	print "# --- Route list ---"
	for r in routeList:
		print "I - id=", r.id, "input1=", r.input1, "input2=", r.input2, \
			"settings=", r.settings
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for turnouts
# ------------------------------------------------------------------------
def report_turnouts():
	print ""
	print "# --- Turnout list ---"
	for t in turnoutList:
		print "I - id=", t.id, "board=", t.board, \
		"channel=", t.channel, "posclos=", t.posclos, \
		"posthro=", t.posthro, "name=", t.name
	print ""

	return 0


# ------------------------------------------------------------------------
# Give help onscreen
# ------------------------------------------------------------------------
def explain():
	print "rasp_routes_py - valid line commands are:"
	print ""
	print "h | help     : gives you this help information"
	print "f | fresh    : read fresh copy of configuration file"
	print "l | list     : report about config file contents"
	print "lt           : list turnouts"
	print "li           : list inputs"
	print "lr           : list routes"
	print "s | state    : report about current status of events"
	print "q | quit     : stops this program"
	print ""
	
	return 0
	

# ------------------------------------------------------------------------
# Initialize all input GPIOs as input and set falling edge events for them
# ------------------------------------------------------------------------
def intitialize_inputs():
#	global pwm

								# set up GPIO using BCM numbering
	GPIO.setmode(GPIO.BCM)

	pwm.setPWMFreq(freq)			# Set frequency to default (see above)


	for i in inputList: 
		i.setup()
		GPIO.add_event_detect(i.gpio, \
					GPIO.FALLING, \
					callback=inpEvent.event, \
					bouncetime=500)


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------

if (read_config_file()):

	explain()
	
	while True:
		reply = raw_input("> ") 
		reply = reply.upper()

		if reply == "QUIT" or reply == "Q":		break 
		elif reply == "LIST" or reply == "L":	report_config_file()
		elif reply == "LT":						report_turnouts()
		elif reply == "LI":						report_inputs()
		elif reply == "LR":						report_routes()
		elif reply == "FRESH" or reply == "F":	refresh_config()
		elif reply == "HELP" or reply == "H":	explain()
		elif reply == "STATE" or reply == "S":	inpEvent.status()

		else:
			print "W - invalid command, type help"

	GPIO.cleanup()
	print "I - bye now"

else:
	print "E - Error reading configuration file"
