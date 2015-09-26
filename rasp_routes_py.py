#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	test_routes_py.py
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
# Event handling not in a class, because that would create a new instance
# every time, causing the semaphore not to work properly and generate all
# kinds of unwanted side-effects and key's getting read to often
#
# ##### SINGLETON !?????
#
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# global definitions for event handling
# ------------------------------------------------------------------------
event_input1 = -1
event_input2 = -1
event_lastval = -1
event_semaphore = False


							# event occurred, input gpio specified
def eventHandler(gpio):
	global event_input1
	global event_input2
	global event_lastval
	global event_semaphore
	
	if (not event_semaphore):

		event_semaphore = True	# Signal work in progress (no double calls)

		if (GPIO.input(gpio)):	# get value from GPIO

								# prevent double handling of same button
			if gpio != event_lastval:
				event_lastval = gpio
				logging.debug("event for input:" + str(gpio))

								# button already pushed?
				if event_input1 == gpio or event_input2 == gpio:
					logging.debug("already got it!")
	 
								# input1 still empty? store it there
				elif event_input1 == -1:
					event_input1 = gpio
					logging.debug("stored in slot 1")

								# if not, is input2 empty? store it there
				elif event_input2 == -1:
					event_input2 = gpio
					logging.debug("stored in slot 2")

								# two inputs received
								# input 1 > 2? switch them around
					if event_input1 > event_input2:
						t = event_input1
						event_input1 = event_input2
						event_input2 = t
						logging.debug("swapped slot 1 and 2")

					logging.debug("Triggering event for " + \
							str(event_input1) + " " + \
							str(event_input2))

								# look for valid route
					found = 0
					for r in myLayout.routeList:
						if r.input1 == event_input1 and r.input2 == event_input2:
								# valid route found, set route
							found = 1
							myLayout.setRoute(r.id)
							break		# out of for loop

								# valid route not found, clear event
					if found == 0:
						logging.warning("invalid combination of inputs, try again")

					event_reset()

				else:
								# event when both full, should not happen
					logging.warning("event occurred, both inputs already set. " + \
						"Enter inputs again please")
					event_reset()

		time.sleep(0.5)			# wait for bounce
		
		event_semaphore = False	# Signal work done


def event_reset():
	global event_input1
	global event_input2
	global event_lastval

	event_input1 = -1
	event_input2 = -1
	event_lastval = -1

# ------------------------------------------------------------------------
# End of global definitions
# ------------------------------------------------------------------------



# ------------------------------------------------------------------------
# class definition for Layout object
# 
# offers:
#		setName(name)
#		clearLayout(name)
#		addTurnout(is, board, channel, posclos, posthro, name)
#		addRoute(id, input1, input2, settings)
#		closeTurnout(id)
#		throwTurnout(id)
#		setRoute(id)
#
# ------------------------------------------------------------------------
class layout:
	def __init__(self, name):
		self.clearLayout(name)
		self.servoHandler = gawServoHandler.servoHandler()	# output
		
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


	def setRoute(self, id):
		for r in self.routeList:
			if r.id == id:
				logging.info("setting route from" + str(r.input1) + \
							 "to" + str(r.input2) + "-" + r.settings)
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
		self.state = -1
		self.setClosed()		# Initial position closed


								# set servo to turnouts closed position
	def setClosed(self):
		if self.state != self.CLOSED:
			myLayout.servoHandler.setServo(self.board, self.channel, self.posclos)
			self.state = self.CLOSED
	
	
								# set servo to turnouts thrown position
	def setThrown(self):
		if self.state != self.THROWN:
			myLayout.servoHandler.setServo(self.board, self.channel, self.posthro)
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

	def addPin(self, id, gpio, name):
		self.inputList.append(input(id, gpio, name) )

	def cleanup(self):
		self.clearPins()
		GPIO.cleanup()

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
								# with pull-up, and set event detection
	def setup(self):
		GPIO.setup(self.gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		logging.debug("Adding event for input:" + str(self.gpio))
		GPIO.add_event_detect(self.gpio, \
					GPIO.RISING, \
					callback=eventHandler, \
					bouncetime=150)

								# remove event from this gpio
	def removeEvent(self):
		logging.debug("Removing event for input:" + str(self.gpio))
		GPIO.remove_event_detect(self.gpio)


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
	
		logging.debug("Adding turnout to list:" + tname)
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
	
		logging.debug("Adding route to List:" + id)
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
	print "Reading and checking configuration file, initializing hardware"

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
								# clear Mylayout
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
# Choose logging level
# ------------------------------------------------------------------------
LOGLEVEL = logging.DEBUG
#LOGLEVEL = logging.WARNING
#LOGLEVEL = logging.ERROR
#LOGLEVEL = logging.CRITICAL

# ------------------------------------------------------------------------
# Set logging format
# ------------------------------------------------------------------------
logging.basicConfig(level=LOGLEVEL, \
			format='%(asctime)s: %(levelname)s: %(message)s', \
			datefmt='%Y-%m-%d,%I:%M:%S')


# ------------------------------------------------------------------------
# define some objects we need
# ------------------------------------------------------------------------
myLayout = layout("rasp_routes_py")				# functionality

myPins = inputPins()							# input


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

		else:
			logging.warning("invalid command, type help")

		time.sleep(0.2)

	myPins.cleanup()
	logging.info("user ended session")
	exit(0)

else:
	logging.error("Error reading configuration file")
	exit(1)
	