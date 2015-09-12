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

board = 0x40					# default board value
freq = 50						# frequency for PWM
servoMin = 210  				# Min pulse length out of 4096 (~ 10ms)
servoMax = 400  				# Max pulse length out of 4096 (~ 20ms)
speed = 0.2						# servo moving speed


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
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.routeid = x2
		self.settings = x3
								# Below some theoretical entries for future
								# use, setting individual object attributes
	def setid(self, who):
		self.id = who
	def setrouteid(self, who):
		self.routeid = who
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
	res = True
	
	myfile = open("rasp_routes_py.ini", "r")

	line = myfile.readline()	# read first line
	lc = 1						# set line count

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
				m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)", line)
				if m:
					turnoutList.append(turnout(int(m.group(1)), \
								int(m.group(2)), \
								int(m.group(3)), \
								int(m.group(4)), \
								int(m.group(5)), \
								m.group(6) ))
				else:
					print "Syntax error in Turnout line", lc

								# Is this an 'input' line?
								# break down Input line and create new input
								# object in list of inputs
			elif (type == "I" or type == "i"):
				m = re.match("[Ii].*[:](.*)[:](.*)[:](.*)", line)
				if m:
					inputList.append(input(int(m.group(1)), \
								int(m.group(2)), \
								m.group(3)))
				else:
					print "Syntax error in Input line", lc

								# Is this a 'route' line?
								# break down Route line and create new route
								# object in list of routes
			elif (type == "R" or type == "r"):
				m = re.match("[Rr].*[:](.*)[:](.*)[:](.*)", line)
				if m:
					routeList.append(route(int(m.group(1)), \
								m.group(2), \
								m.group(3)))
				else:			# line type not defined
					print "Syntax error in Route line", lc

								# Is this a 'name' line?
								# break down Name line
			elif (type == "N" or type == "n"):
				m = re.match("[Nn].*[:](.*)", line)
				if m:
					name = (m.group(1))
				else:
					print "Syntax error in Name line", lc

									# Is this NOT a comment line?
			elif (type != "#"):
				print "Invalid line type in line", lc

								# read next line and increment line count
		line = myfile.readline()
		lc = lc+1

	myfile.close()				# close config file
	return res


# ------------------------------------------------------------------------
# report values from config file
# ------------------------------------------------------------------------
def report_config_file():
	print ""
	print "# --- Turnout list ---"
	for t in turnoutList:
		print "id=", t.id, "board=", t.board, \
		"channel=", t.channel, "posclos=", t.posclos, \
		"posthro=", t.posthro, "name=", t.name

	print ""
	print "# --- Input list ---"
	for t in inputList:
		print "id=", t.id, "gpio=", t.gpio, "name=", t.name

	print ""
	print "# --- Route list ---"
	for t in routeList:
		print "id=", t.id, "routeid=", t.routeid, "settings=", t.settings

	return 0


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------
if (read_config_file()):

								# Initialize all inputs read
	for i in inputList: i.setup()

	report_config_file()

	while (1):
		for i in inputList: i.getval()
		
		for i in range(0, 4):
			turnoutList[i].setclosed()
			time.sleep(0.2)
			
			turnoutList[i].setthrown()
			time.sleep(0.2)
		
		if inputList[19].inpval == 0:
			print "1 pressed"
		
		if inputList[20].inpval == 0:
			print "2 pressed"
			break

	GPIO.cleanup()
	print "bye now"

else:
	print "Error reading configuration file"
