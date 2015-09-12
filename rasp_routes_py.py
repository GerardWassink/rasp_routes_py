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
import time
import re

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
pwm = PWM(board)
#pwm = PWM(board, debug=True)

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
	
	def setclosed(self):
		global board, pwm, freq
		if self.board != board:
								# When this turnout board differs from
								# previous, than change working board
			board = self.board
			pwm = PWM(self.board)	
			pwm.setPWMFreq(freq)
		pwm.setPWM(self.channel, 0, self.posclos)
	
	def setthrown(self):
		global board, pwm, freq
		if self.board != board:
								# When this turnout board differs from
								# previous, than change working board
			board = self.board
			pwm = PWM(self.board)	
			pwm.setPWMFreq(freq)
		pwm.setPWM(self.channel, 0, self.posthro)



# ------------------------------------------------------------------------
# class definition for input objects
# ------------------------------------------------------------------------
class input:
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.gpio = x2
		self.name = x3
		self.inpval = 1			# Default, assuming pull-up's

	def setid(self, who):
		self.id = who

	def setgpio(self, who):
		self.gpio = who

	def setname(self, who):
		self.name = who
	
	def getval(self, val):
		self.inpval = 0			# QQQQQQQQQQQQQQ


# ------------------------------------------------------------------------
# class definition for route objects
# ------------------------------------------------------------------------
class route:
	def __init__(self, x1, x2, x3):
		self.id = x1
		self.routeid = x2
		self.settings = x3

	def setid(self, who):
		self.id = who

	def setrouteid(self, who):
		self.routeid = who

	def setsettings(self, who):
		self.settings = who


# ------------------------------------------------------------------------
# lists of various classes
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

	regel = myfile.readline()	# read first line
	lc = 1						# set line count

	while (regel != ""):		# read through file
		regel = regel.rstrip()	# strip all space from right side

		if (len(regel) > 0):	# empty line?

								# get first character to determine line type
			m = re.match("(.).*", regel)
			if m:
				type = (m.group(1))
		
								# Is this a 'turnout' line?
			if (type == "T" or type == "t"):
				m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)[:](.*)", regel)
				if m:			# break down Turnout line and create new turnout
								# object in list of turnouts
					turnoutList.append(turnout(int(m.group(1)), \
									int(m.group(2)), \
									int(m.group(3)), \
									int(m.group(4)), \
									int(m.group(5)), \
									m.group(6) ))
									
				else:
					print "Syntax fout in Turnout regel", lc

									# Is this an 'input' line?
			elif (type == "I" or type == "i"):
				m = re.match("[Ii].*[:](.*)[:](.*)[:](.*)", regel)
				if m:			# break down Input line and create new input
								# object in list of inputs
					inputList.append(input(int(m.group(1)), \
								int(m.group(2)), \
								m.group(3)))
				else:
					print "Syntax fout in Input regel", lc

									# Is this a 'route' line?
			elif (type == "R" or type == "r"):
				m = re.match("[Rr].*[:](.*)[:](.*)[:](.*)", regel)
				if m:			# break down Route line and create new route
								# object in list of routes
					routeList.append(route(int(m.group(1)), \
								m.group(2), \
								m.group(3)))
				else:			# line type not defined
					print "Syntax fout in Route regel", lc

									# Is this a 'name' line?
			elif (type == "N" or type == "n"):
				m = re.match("[Nn].*[:](.*)", regel)
				if m:			# break down Name line
					name = (m.group(1))
					print "name =", name
				else:
					print "Syntax fout in Name regel", lc

									# Is this a 'name' line?
			elif (type != "#"):
				print "Invalid line type in regel", lc

								# read next line		
		regel = myfile.readline()
		lc = lc+1				# increment line count

	myfile.close()				# close config file
	return res


# ------------------------------------------------------------------------
# test routine
# ------------------------------------------------------------------------
def setThemMin(x, y):
	for i in range(x, y):
		turnoutList[i].setclosed()
		time.sleep(speed)


# ------------------------------------------------------------------------
# test routine
# ------------------------------------------------------------------------
def setThemMax(x, y):
	for i in range(x, y):
		turnoutList[i].setthrown()
		time.sleep(speed)


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------
if (read_config_file()):
	print "Conf file read OKAY"

	print ""
	print "# --- Turnout list ---"
	for t in turnoutList:
		print "id=", t.id, "board=", t.board, "channel=", t.channel, "posclos=", t.posclos, "posthro=", t.posthro, "name=", t.name

	print ""
	print "# --- Input list ---"
	for t in inputList:
		print "id=", t.id, "gpio=", t.gpio, "name=", t.name

	print ""
	print "# --- Route list ---"
	for t in routeList:
		print "id=", t.id, "routeid=", t.routeid, "settings=", t.settings

	while (True):					# Change angle of servo 
		setThemMin(0, 4)
		setThemMax(0, 4)


else:
	print "Conf file read WRONG"
