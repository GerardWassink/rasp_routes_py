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
import gawRelayHandler
import gawServoHandler
from xml.dom import minidom
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
		self.relayHandler = gawRelayHandler.relayHandler()	# output relays
		self.servoHandler = gawServoHandler.servoHandler()	# output servo's
		
	def clearLayout(self, name):
		self.name = name
		self.owner = ""
		self.turnoutList = []
		self.routeList = []

	def setName(self, name):
		self.name = name
	
	def setOwner(self, owner):
		self.owner = owner
	
	#
	# *** Turnout handling
	#
	
	def addTurnout(self, id, type, board, channel, posclos, posthro, name):
		found = 0				# Try to find turnout
		for t in self.turnoutList:
			if t.id == id:
				found = 1
				break
		if found == 0:			# only add once
			t = turnout(id, type, board, channel, posclos, posthro, name)
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


	#
	# *** Route handling
	#
	
	def addRoute(self, id, input1, input2):
		found = 0				# Try to find route
		for r in self.routeList:
			if r.id == id:
				found = 1
				break
		if found == 0:			# only add once
			self.routeList.append(route(id, input1, input2 ) )
		else:
			logging.error("trying to add duplicate route, id=" + str(id))


	def addRouteTurnout(self, id, name, position):
		found = 0				# Try to find route
		for r in self.routeList:
			if r.id == id:
				found = 1
				break
		if found == 1:
			r.setTurnoutList.append(setTurnout(name, position))
		else:
			logging.error("error trying to add turnout to route, id=" + str(id) + \
							", name=" + name )


	def setRoute(self, id):
		for r in self.routeList:
			if r.id == id:
				logging.info("setting route from " + str(r.input1) + \
							 " to " + str(r.input2))
				tn = 0		# Walk through turnouts to be set
				for s in r.setTurnoutList:
					name = s.name
					position = s.position.upper()
					for t in self.turnoutList:
						if t.name == name:
							if position == "THROWN":
								self.throwTurnout(t.id)
								logging.debug("\tthrowing turnout " + name)
							elif position == "CLOSED":
								self.closeTurnout(t.id)
								logging.debug("\tclosing turnout " + name)
							break
					tn += 1
			


# ------------------------------------------------------------------------
# class definition for turnout objects
# ------------------------------------------------------------------------
class turnout:
	def __init__(self, id, type, board, channel, posclos, posthro, name):
		self.id = id
		self.type = type
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
			if self.type == "servo":
				myLayout.servoHandler.setServo(self.board, self.channel, self.posclos)
			elif self.type == "relay":
				myLayout.relayHandler.setRelay(self.board, self.channel, self.posclos)
			self.state = self.CLOSED
	
	
								# set servo to turnouts thrown position
	def setThrown(self):
		if self.state != self.THROWN:
			if self.type == "servo":
				myLayout.servoHandler.setServo(self.board, self.channel, self.posthro)
			elif self.type == "relay":
				myLayout.relayHandler.setRelay(self.board, self.channel, self.posthro)
			self.state = self.THROWN


# ------------------------------------------------------------------------
# class definition for route objects
# ------------------------------------------------------------------------
class route:
	def __init__(self, id, input1, input2):
		self.id = id
		self.input1 = input1
		self.input2 = input2
		self.setTurnoutList = []

class setTurnout:
	def __init__(self, name, position):
		self.name = name
		self.position = position


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
# read and process the configuration file
# ------------------------------------------------------------------------
def read_config_file():
	res = True

								# Initialize all input GPIOs as input and 
								# set falling edge events for them
	GPIO.setmode(GPIO.BCM)		# set up GPIO using BCM numbering

								#
								# read the xml configuration file
	xmldoc = minidom.parse('rasp_routes_py.xml')
	
								#
								# *** find the description parts
	dList = xmldoc.getElementsByTagName('description')
	for d in dList:
		myLayout.setName(d.attributes['name'].value)
		myLayout.setOwner(d.attributes['owner'].value)


	print "--------------------------------------------------------------------------------"
	print "Welcom to " + myLayout.name
	if myLayout.owner != "":
		print "Owned by  " + myLayout.owner
	print "--------------------------------------------------------------------------------"
	print ""
	print "Reading and checking configuration file, initializing hardware"
	print ""
	
								#
								# process input range lines
	irList = xmldoc.getElementsByTagName('input_range')
	for ir in irList:
		gpio_min=int(ir.attributes['gpio_min'].value)
		gpio_max=int(ir.attributes['gpio_max'].value)
		logging.debug("Range for gpio-numbers, min=" + str(gpio_min) + ", max=" + str(gpio_max))
	
								#
								# process relay turnout range lines
	rtrList = xmldoc.getElementsByTagName('relay_turnout_range')
	for rtr in rtrList:
		r_adr_min=int(rtr.attributes['adr_min'].value)
		r_adr_max=int(rtr.attributes['adr_max'].value)
		r_pos_min=int(rtr.attributes['pos_min'].value)
		r_pos_max=int(rtr.attributes['pos_max'].value)
		logging.debug("Ranges for relay-turnouts" + \
				", min_adr=" + str(r_adr_min) + ", max_adr=" + str(r_adr_max) + \
				", min_pos=" + str(r_pos_min) + ", max_pos=" + str(r_pos_max) )
	
								#
								# process servo turnout range lines
	strList = xmldoc.getElementsByTagName('servo_turnout_range')
	for strg in strList:
		s_adr_min=int(strg.attributes['adr_min'].value)
		s_adr_max=int(strg.attributes['adr_max'].value)
		s_pos_min=int(strg.attributes['pos_min'].value)
		s_pos_max=int(strg.attributes['pos_max'].value)
		logging.debug("Ranges for servo-turnouts" + \
				", min_adr=" + str(s_adr_min) + ", max_adr=" + str(s_adr_max) + \
				", min_pos=" + str(s_pos_min) + ", max_pos=" + str(s_pos_max) )
	
								#
								# process input lines
	iList = xmldoc.getElementsByTagName('input')
	iid = 0
	print "This layout has", len(iList), "inputs"
	for i in iList:
		gpio=int(i.attributes['gpio'].value)
		name=i.attributes['name'].value
								#
								# test against specified ranges
		if gpio_min <= gpio <= gpio_max:
			logging.debug("Adding input to list: " + name)
			myPins.addPin(iid, gpio, name)
			iid += 1
		else:
			logging.error("gpio out of range for input '" + name + "', NOT ADDED")
	
	
								#
								# process turnout lines
	tList = xmldoc.getElementsByTagName('turnout')
	tid = 0
	print "This layout has", len(tList), "turnouts"
	for t in tList:
		type=t.attributes['type'].value
		boardAddress=int(t.attributes['boardAddress'].value)
		channel=int(t.attributes['channel'].value)
		posclos=int(t.attributes['posclos'].value)
		posthro=int(t.attributes['posthro'].value)
		name=t.attributes['name'].value
								#
								# test against specified ranges
		if 	(	(type.upper() == "RELAY") & \
				(r_adr_min <= boardAddress <= r_adr_max) & \
				(0 <= channel <= 15) & \
				(r_pos_min <= posclos <= r_pos_max) & \
				(r_pos_min <= posthro <= r_pos_max ) 	) \
			| \
			(	(type.upper() == "SERVO") & \
				(s_adr_min <= boardAddress <= s_adr_max) & \
				(0 <= channel <= 15) & \
				(s_pos_min <= posclos <= s_pos_max) & \
				(s_pos_min <= posthro <= s_pos_max) 	):

			logging.debug("Adding turnout to list: " + name)
			myLayout.addTurnout(tid, type, boardAddress, channel, \
										posclos, posthro, name)
			tid += 1
		else:
			logging.error("value out of range for turnout '" + name + "', NOT ADDED")
	
	
								#
								# process route lines
	rList = xmldoc.getElementsByTagName('route')
	rid = 0
	print "This layout has", len(rList), "routes"
	for r in rList:
		input1=int(r.attributes['input1'].value)
		input2=int(r.attributes['input2'].value)
		logging.debug("Adding route to List: " + str(rid))
		myLayout.addRoute(rid, input1, input2)
								#
								# process route turnouts to be set
		sList = r.getElementsByTagName('set_turnout') 
		for s in sList:
			name = s.attributes['name'].value
			position = s.attributes['position'].value
								#
								# test against specified ranges
			if (position.upper() == "CLOSED") | (position.upper() == "THROWN"):
				logging.debug("Adding turnout to route: " + str(rid) + " " + name + " " + position)
				myLayout.addRouteTurnout(rid, name, position)
			else:
				logging.error("position value error for route " + str(rid) + \
							", set_turnout '" + name + "', NOT ADDED")

		rid += 1
	
	print "--------------------------------------------------------------------------------"
	print "Welcome to " + myLayout.name
	if myLayout.owner != "":
		print "Owned by  " + myLayout.owner
	print "--------------------------------------------------------------------------------"

	return res


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
		print "id=", r.id, "input1=", r.input1, "input2=", r.input2
		for t in r.setTurnoutList:
			print "\t" + t.name + " " + t.position
	print ""
	return 0


# ------------------------------------------------------------------------
# report values for turnouts
# ------------------------------------------------------------------------
def report_turnouts():
	print ""
	print "# --- Turnout list ---"
	for t in myLayout.turnoutList:
		print "id=", t.id, "board=", t.board, "type=", t.type, \
		"channel=", t.channel, "posclos=", t.posclos, \
		"posthro=", t.posthro, "name=", t.name
	print ""

	return 0


# ------------------------------------------------------------------------
# Give help onscreen
# ------------------------------------------------------------------------
def explain():
	print ""
	print "rasp_routes_py - valid line commands are:"
	print ""
	print "h | help     : gives you this help information"
	print "f | fresh    : read fresh copy of configuration file"
	print "l | list     : report about config file contents"
	print "lt           : list turnouts"
	print "li           : list inputs"
	print "lr           : list routes"
	print "q | quit     : stops this program"
	print ""
	
	return 0
	


# ------------------------------------------------------------------------
# MAIN CODE STARTS HERE												MAIN
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

		else:
			logging.warning("invalid command, type help")

		time.sleep(0.2)

	myPins.cleanup()
	logging.info("user ended session")
	exit(0)

else:
	logging.error("Error reading configuration file")
	exit(1)
	