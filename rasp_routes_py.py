#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	rasp_routes_py.py
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
import gawServoHandler
import time
import re
import logging


# ------------------------------------------------------------------------
# class definition for Layout object
# ------------------------------------------------------------------------
class layout:
	def __init__(self, name):
		self.name = name
		self.turnoutList = []
		self.routeList = []

		
	def setName(self, name):
		self.name = name
	
	
	def clearLayout(self, name):
		self.name = name
		self.turnoutList = []
		self.routeList = []


	def addTurnout(self, id, board, channel, posclos, posthro, name):
		found = 0				# Try to find turnout
		for t in self.turnoutList:
			if t.id == id:
				found = 1
				break
		if found == 0:			# only add once
			t = turnout(id, board, channel, posclos, posthro, name)
			self.turnoutList.append(t)
		else:
			logging.error("trying to add duplicate turnout, id=" + str(id))


	def addRoute(self, id, input1, input2, settings):
		found = 0				# Try to find route
		for r in self.routeList:
			if r.id == id:
				found = 1
				break
		if found == 0:			# only add once
			self.routeList.append(route(id, \
						input1, \
						input2, \
						settings ) )
		else:
			logging.error("trying to add duplicate route, id=" + str(id))


	def closeTurnout(self, id):
		found = 0				# Try to find turnout
		for t in self.turnoutList:
			if t.id == id:
				found = 1
				break
		if found == 1:			# only add once
			t.setClosed()
		else:
			logging.error("trying to close unknown turnout, id=" + str(id))


	def throwTurnout(self, id):
		found = 0				# Try to find turnout
		for t in self.turnoutList:
			if t.id == id:
				found = 1
				break
		if found == 1:			# only add once
			t.setThrown()
		else:
			logging.error("trying to throw unknown turnout, id=" + str(id))


	def setRoute(self, id):
		logging.info("setting route from" + str(self.input1) + \
							 "to" + str(self.input2) + "-" + self.settings)
		for r in self.routeList:
			if r.id == id:
				tn = 0		# Walk through settings
				for s in r.settings:
					s = s.upper()
					for t in self.turnoutList:
						if t.id == tn:
							if s == 'T':
								self.throwTurnout(t.id)
							elif s == 'C':
								self.closeTurnout(t.id)
							break
					tn += 1
			


# ------------------------------------------------------------------------
# class definition for turnout objects
# ------------------------------------------------------------------------
class turnout:
	def __init__(self, id, board, channel, posclos, posthro, name):
		self.id = id
		self.board = board
		self.channel = channel
		self.posclos = posclos
		self.posthro = posthro
		self.name = name
		self.CLOSED = 0
		self.THROWN = 1
		self.setClosed()		# Initial position closed


								# set servo to turnouts closed position
	def setClosed(self):
		myServoHandler.setServo(self.board, self.channel, self.posclos)
		self.state = self.CLOSED
	
	
								# set servo to turnouts thrown position
	def setThrown(self):
		myServoHandler.setServo(self.board, self.channel, self.posthro)
		self.state = self.THROWN


# ------------------------------------------------------------------------
# class definition for route objects
# ------------------------------------------------------------------------
class route:
	def __init__(self, id, input1, input2, settings):
		self.id = id
		self.input1 = input1
		self.input2 = input2
		self.settings = settings


# ------------------------------------------------------------------------
# class definition for gpio pins
# ------------------------------------------------------------------------
class inputPins:
	def __init__(self):
		self.inputList = []

	def cleanup(self):
		GPIO.cleanup()

	def addPin(self, id, gpio, name):
		self.inputList.append(input(id, gpio, name) )

	def clearPins(self):
		for i in self.inputList:
			i.removeEvent()
		self.inputList = []


# ------------------------------------------------------------------------
# class definition for input objects
# ------------------------------------------------------------------------
class input:
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.gpio = x2
		self.name = x3
		self.inpval = 0
		self.setup()

								# Setup this object's GPIO as an input line
								# with pull-up
	def setup(self):
		GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.gpio, \
					GPIO.RISING, \
					callback=inpEvent.event, \
					bouncetime=75)

								# remove event from this gpio
	def removeEvent(self):
		GPIO.remove_event_detect(self.gpio)

								# Read the current value os this object's
								# GPIO line
	def getval(self):
		self.inpval = GPIO.input(self.gpio)


# ------------------------------------------------------------------------
# class definition for input events
# ------------------------------------------------------------------------
class inputEvent:
	def __init__(self):			# event empty means both inputs are -1
		self.input1 = -1
		self.input2 = -1
		self.lastval = -1

								# event occurred, input gpio specified
	def event(self, val):
		if (GPIO.input(val)):	# run only on button release

								# prevent double handling of same button
			if val != self.lastval:
				self.lastval = val

				logging.info("event for input:" + str(val))

								# did we have it already?
				if self.input1 == val or self.input2 == val:
					logging.info("already got it!")
		 
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

					logging.info("Triggering event for " + str(self.input1) + \
							" " + str(self.input2))

								# look for valid route
					found = 0
					for r in myLayout.routeList:
						if r.input1 == self.input1 and r.input2 == self.input2:
								# valid route found, set route
							found = 1
							myLayout.setRoute(r.id)
							break		# out of for loop

								# valid route not found, clear event
					if found == 0:
						logging.warning("invalid combination of inputs, try again")

					self.reset()

				else:
								# event when both full, should not happen
					logging.warning("event occurred, both inputs already set. " + \
						"Enter inputs again please")
					self.reset()


	def reset(self):
		self.input1 = -1
		self.input2 = -1
		self.lastval = -1

	
	def status(self):
		print "> - Status of events:"
		if self.input1 != -1:
			print "> - input 1 =", self.input1
		else:
			print "> - status is blank"
		if self.input2 != -1:
			print "> - input 2 =", self.input2


# ------------------------------------------------------------------------
# parse lines of type Turnout
# ------------------------------------------------------------------------
def parseTurnoutLine(line, tid, lc):
							# break down Turnout line and create new turnout
							# object in list of turnouts
	m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)", line)
	if m:
		id = str(tid)

		board = m.group(1)
		if board == '':
			board = '64'
			logging.info("board not specified in Turnout line " + str(lc) + \
				"- default of 64 substituted")
	
		chan = m.group(2)
		if chan == '':
			chan = '0'
			logging.info("channel not specified in Turnout line " + str(lc) + \
				"- default of 0 substituted")
	
		posclos = m.group(3)
		if posclos == '':
			posclos ='210'
			logging.info("posclos not specified in Turnout line " + str(lc) + \
				"- default of 210 substituted")
	
		posthro = m.group(4)
		if posthro == '':
			posclos ='400'
			logging.info("posthro not specified in Turnout line " + str(lc) + \
				"- default of 400 substituted")
	
		tname = m.group(5)
		if tname == '':
			tname = "T" + id
			logging.info("name not specified in Turnout line " + str(lc) + \
				"- default of:" + tname + " substituted")
	
		myServoHandler.addBoard(int(board), 50)
		myServoHandler.addServo(int(board), int(chan))

		myLayout.addTurnout(int(id), int(board), int(chan), \
									int(posclos), int(posthro), tname)

		return True
	else:
		logging.warning("Syntax error in Turnout line " + str(lc) + \
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
		myPins.addPin(int(iid), int(m.group(1)), m.group(2) )
		return 1
	else:
		logging.warning("Syntax error in Input line " + str(lc) + \
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
			logging.info("input1 not specified in Route line " + str(lc) + \
				"- default of 0 substituted")
	
		inp2 = m.group(2)
		if inp2 == '':
			inp2 = '0'
			logging.info("input2 not specified in Route line " + str(lc) + \
				"- default of 0 substituted")
	
		myLayout.addRoute(int(rid), \
					int(inp1), \
					int(inp2), \
					m.group(3) )
		
		return 1
		
	else:			# line type not defined
	
		logging.warning("Syntax error in Route line " + str(lc) + \
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
		logging.warning("Syntax error in Name line " + str(lc) + \
				", line not processed")



# ------------------------------------------------------------------------
# read and process the configuration file
# ------------------------------------------------------------------------
def read_config_file():
	global name
	res = True

								# Initialize all input GPIOs as input and 
								# set falling edge events for them
	GPIO.setmode(GPIO.BCM)		# set up GPIO using BCM numbering

	print "--------------------------------------------------------------------------------"
	print "Welcom to " + myLayout.name
	print "--------------------------------------------------------------------------------"
	print ""
	print "Reading and checking configuration file"

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
					logging.warning("Invalid line type in line" + str(lc))

								# increment line count
			lc = lc+1

	checkConfigLists()			# check for errors after building lists

	print "--------------------------------------------------------------------------------"
	print "Welcome to " + myLayout.name
	print "--------------------------------------------------------------------------------"

	return res


# ------------------------------------------------------------------------
# check lists after reading config file
# ------------------------------------------------------------------------
def checkConfigLists():
								# after reading, check lists for mismatching ID's
								# and other possible errors
								
								# turnout list ID's
#	for t in myBoards.servoBoard.turnoutList:
#		if t.posclos < 210:
#			logging.info("closed value for turnout '" + t.name + \
#				"' less than 210, only proceed if this is intentional")
#		if t.posthro > 400:
#			logging.info("thrown value for turnout '" + t.name + \
#				"' greater than 400, only proceed if this is intentional")
	
								# input list ID's
	for i in myPins.inputList:
		if i.gpio == 2 or i.gpio == 3:
			logging.error("port 2 or 3 use for input '" + i.name + \
				"' during I2C servo operation, program will end")
			exit(1)
	
								# route list ID's
#	for r in routeList:
								# no checks yet


# ------------------------------------------------------------------------
# re-read config file and setup again
# ------------------------------------------------------------------------
def refresh_config():
	myPins.clearPins()			# before refreshing, remove event triggers
								# clear Mylayout
	myLayout.clearLayout("rasp_routes_py refreshing")
								# clear board stack and
	myServoHandler.clearServoHandler()
								# re-read config file
	if (read_config_file()):
		logging.info("Configuration refreshed on user request")


# ------------------------------------------------------------------------
# report values from config file
# ------------------------------------------------------------------------
def report_config_file():
	report_turnouts()
	report_inputs()
	report_routes()
	return 0


# ------------------------------------------------------------------------
# report values for inputs
# ------------------------------------------------------------------------
def report_inputs():
	print ""
	print "# --- Input list ---"
	for i in myPins.inputList:
		print "id=", i.id, "gpio=", i.gpio, "name=", i.name
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for routes
# ------------------------------------------------------------------------
def report_routes():
	print ""
	print "# --- Route list ---"
	for r in myLayout.routeList:
		print "id=", r.id, "input1=", r.input1, "input2=", r.input2, \
			"settings=", r.settings
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for turnouts
# ------------------------------------------------------------------------
def report_turnouts():
	print ""
	print "# --- Turnout list ---"
	for t in myLayout.turnoutList:
		print "id=", t.id, "board=", t.board, \
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
# CODE STARTS HERE
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# set logging level and format
# ------------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG, \
			format='%(asctime)s: %(levelname)s: %(message)s', \
			datefmt='%Y-%m-%d,%I:%M:%S')


# ------------------------------------------------------------------------
# define some objects we need
# ------------------------------------------------------------------------

myLayout = layout("rasp_routes_py")				# functionality

myServoHandler = gawServoHandler.servoHandler()	# output
				
inpEvent = inputEvent()							# input
myPins = inputPins()


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------

if (read_config_file()):
	
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
			logging.warning("invalid command, type help")

	myPins.cleanup()
	logging.info("user ended session")
	exit(0)

else:
	logging.error("Error reading configuration file")
	exit(1)
	