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

								# set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)


# ------------------------------------------------------------------------
# Global variables and default values
# ------------------------------------------------------------------------

								# values concerning servos' and servo HAT
board = 0x40					# default board value
freq = 50						# frequency for PWM
servoMin = 210  				# Min pulse length out of 4096 (~ 10ms)
servoMax = 400  				# Max pulse length out of 4096 (~ 20ms)
speed = 0.2						# servo moving speed

name = "rasp_routes_py program"	# default value for name

# Initialise the PWM device using the default address (defined above)
# Uncomment the line you want, with, or without debugging

#pwm = PWM(board, debug=True)
pwm = PWM(board)
pwm.setPWMFreq(freq)			# Set frequency to default (see above)


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
								# Below some theoretical entries for future
								# use, setting individual object attributes
	def setid(self, who):
		self.id = who
	def setboard(self, who):
		self.board = who
	def setchannel(self, who):
		self.channel = who
	def setname(self, who):
		self.name = who
	def setposclos(self, who):
		self.posclos = who
	def setposthro(self, who):
		self.posthro = who


								# Set the pulse-width value for this
								# turnout, corresponding with it's 
								# closed position
	def setclosed(self):
		global board, pwm, freq
								# When this turnout board differs from
								# previous, than change working board
		if self.board != board:
			board = self.board		# remember used board
			pwm = PWM(self.board)	# set board to be used
			pwm.setPWMFreq(freq)	# just to be sure, set frequency
									# do it:
		pwm.setPWM(self.channel, 0, self.posclos)
	
	
								# Set the pulse-width value for this
								# turnout, corresponding with it's 
								# thrown position
	def setthrown(self):
		global board, pwm, freq
								# When this turnout board differs from
								# previous, than change working board
		if self.board != board:
			board = self.board		# remember used board
			pwm = PWM(self.board)	# set board to be used
			pwm.setPWMFreq(freq)	# just to be sure, set frequency
									# do it:
		pwm.setPWM(self.channel, 0, self.posthro)



# ------------------------------------------------------------------------
# class definition for input objects
# ------------------------------------------------------------------------
class input:
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.gpio = x2
		self.name = x3
		self.inpval = 0

								# Below some theoretical entries for future
								# use, setting individual object attributes
	def setid(self, who):
		self.id = who
	def setgpio(self, who):
		self.gpio = who
	def setname(self, who):
		self.name = who


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
								# Below some theoretical entries for future
								# use, setting individual object attributes
	def setid(self, who):
		self.id = who
	def input1(self, who):
		self.input1 = who
	def input2(self, who):
		self.input2 = who
	def setsettings(self, who):
		self.settings = who


# ------------------------------------------------------------------------
# lists to hold objects of various classes
# ------------------------------------------------------------------------
turnoutList = []
inputList = []
routeList = []


# ------------------------------------------------------------------------
# read and process the configuration file
# ------------------------------------------------------------------------
def read_config_file():
	global name
	res = True
	
	print "--------------------------------------------------------------------------------"
	print "Welcom to " + name
	print "--------------------------------------------------------------------------------"
	print ""
	print "Reading and checking configuration file"

	errors = 0
	warnings = 0
	informationals = 0
		
	myfile = open("rasp_routes_py.ini", "r")

	line = myfile.readline()	# read first line
	
	lc = 1						# set line count
	
	tid = 0						# set Turnout id count
	iid = 0						# set Input id count
	rid = 0						# set Route id count

	while (line != ""):		# read through file
		line = line.rstrip()	# strip all spaces from right side

		if (len(line) > 0):	# empty line?

								# get first character to determine line type
			m = re.match("(.).*", line)
			if m:
				type = (m.group(1))
		
								# Is this a 'turnout' line?
								# break down Turnout line and create new turnout
								# object in list of turnouts
			if (type == "T" or type == "t"):
				m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)", line)
				if m:
					id = str(tid)
					
					base = m.group(1)
					if base == '':
						print "I - board not specified in Turnout line", lc, \
							"- default of 64 substituted"
						base = '64'
						informationals += 1
						
					chan = m.group(2)
					if chan == '':
						print "E - channel not specified in Turnout line", lc, \
							"- default of 0 substituted"
						chan = '0'
						informationals += 1
						
					posclos = m.group(3)
					if posclos == '':
						print "I - posclos not specified in Turnout line", lc, \
							"- default of 210 substituted"
						posclos ='210'
						informationals += 1
						
					posthro = m.group(4)
					if posthro == '':
						print "I - posthro not specified in Turnout line", lc, \
							"- default of 400 substituted"
						posclos ='400'
						informationals += 1
						
					tname = m.group(5)
					if tname == '':
						print "I - name not specified in Turnout line", lc, \
							"- default of T" + id + " substituted"
						tname = "T" + id
						informationals += 1
						
					turnoutList.append(turnout( \
								int(id), \
								int(base), \
								int(chan), \
								int(posclos), \
								int(posthro), \
								tname ) )
					tid += 1
				else:
					print "W - Syntax error in Turnout line", lc, \
							", line not processed"
					warnings += 1


								# Is this an 'input' line?
								# break down Input line and create new input
								# object in list of inputs
			elif (type == "I" or type == "i"):
				m = re.match("[Ii].*[:](.*)[:](.*)", line)
				if m:
					id = str(iid)

					inputList.append(input(int(iid), \
								int(m.group(1)), \
								m.group(2) ) )
					iid += 1
				else:
					print "W - Syntax error in Input line", lc, \
							", line not processed"
					warnings += 1


								# Is this a 'route' line?
								# break down Route line and create new route
								# object in list of routes
			elif (type == "R" or type == "r"):
				m = re.match("[Rr].*[:](.*)[:](.*)[:](.*)", line)
				if m:
					id = str(rid)

					inp1 = m.group(1)
					if inp1 == '':
						print "I - input1 not specified in Route line", lc, \
							"- default of 0 substituted"
						inp1 = '0'
						informationals += 1
						
					inp2 = m.group(2)
					if inp2 == '':
						print "I - input2 not specified in Route line", lc, \
							"- default of 0 substituted"
						inp2 = '0'
						informationals += 1
						
					routeList.append(route(int(rid), \
								int(inp1), \
								int(inp2), \
								m.group(3) ) )
					rid += 1
				else:			# line type not defined
					print "W - Syntax error in Route line", lc, \
							", line not processed"
					warnings += 1


								# Is this a 'name' line?
								# break down Name line
			elif (type == "N" or type == "n"):
				m = re.match("[Nn].*[:](.*)", line)
				if m:
					name = (m.group(1))
				else:
					print "W - Syntax error in Name line", lc, \
							", line not processed"
					warnings += 1

									# Is this NOT a comment line?
			elif (type != "#"):
				print "W - Invalid line type in line", lc
				warnings += 1

								# read next line and increment line count
		line = myfile.readline()
		lc = lc+1

	myfile.close()				# close config file
	
	
								# after reading, check lists for mismatching ID's
								# and other possible errors
								
								# turnout list ID's
	c = 0
	for t in turnoutList:
		if t.id != c:
			print "W - ID specified for turnout '" + t.name + "' not equal to internal ID"
			warnings += 1
		if t.posclos < 210:
			print "I - closed value for turnout '" + t.name + "' less than 210" + \
				", only proceed if this is intentional"
			informationals += 1
		if t.posthro > 400:
			print "I - thrown value for turnout '" + t.name + "' greater than 400" + \
				", only proceed if this is intentional"
			informationals += 1
		c += 1
	
								# input list ID's
	c = 0
	for i in inputList:
		if i.id != c:
			print "W - ID specified for input '" + i.name + "' not equal to internal ID"
			warnings += 1
		if i.gpio == 2 or i.gpio == 3:
			print "E - port 2 or 3 use for input '" + i.name + "' during I2C servo " + \
					"operation, program will end after check"
			errors += 1
		c += 1
	
								# route list ID's
	c = 0
	for r in routeList:
		if r.id != c:
			print "W - ID specified for route '" + r.routeid + "' not equal to internal ID"
			warnings += 1
		c += 1

	print ""
	print "I - during config file check:"
	print "		informationals:", informationals
	print "		warnings      :", warnings
	print "		errors        :", errors
	print ""

	if errors == 0:
		print "I - No errors found, processing continues"
		print ""
	else:
		print "I - rasp_routes_py stopping due to errors in configuration file"
		print ""
		exit(1)
	
	print "--------------------------------------------------------------------------------"
	print "Welcome to " + name
	print "--------------------------------------------------------------------------------"
	
	return res


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
# Give help onscreen
# ------------------------------------------------------------------------
def explain():
	print "rasp_routes_py - valid line commands are:"
	print ""
	print "h | help     : gives you this help information"
	print "l | list     : report about config file contents"
	print "s | servo    : gives the servo's a spin (testing purposes)"
	print "q | quit     : stops this program"
	print ""
	
	return 0
	

# ------------------------------------------------------------------------
# Initialize all input GPIOs as input and set falling edge events for them
# ------------------------------------------------------------------------
def intitialize_inputs():
	for i in inputList: 
		i.setup()
		GPIO.add_event_detect(i.gpio, \
					GPIO.FALLING, \
					callback=process_button, \
					bouncetime=300)


# ------------------------------------------------------------------------
# event that processes pushed buttons (inputs
# ------------------------------------------------------------------------
def process_button(but):
	print "I - button", but, "pressed"
	return 0


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------

if (read_config_file()):

	intitialize_inputs()

	explain()
	
	while True:
		reply = raw_input("> ") 
		reply = reply.upper()

		if reply == "QUIT" or reply == "Q":		break 

		elif reply == "LIST" or reply == "L":	report_config_file()

		elif reply == "HELP" or reply == "H":	explain()

		elif reply == "SERVO" or reply == "S":	# Test entry
			for i in range(0, 4):
				turnoutList[i].setclosed()
				time.sleep(0.2)
			
			for i in range(3, -1, -1):
				turnoutList[i].setthrown()
				time.sleep(0.2)

		else:
			print "W - invalid command, type help"

	GPIO.cleanup()
	print "I - bye now"

else:
	print "E - Error reading configuration file"
