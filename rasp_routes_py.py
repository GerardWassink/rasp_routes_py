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
# Global variables
# ------------------------------------------------------------------------

board = 0x40					# default board value
freq = 50						# frequency for PWM
servoMin = 210  				# Min pulse length out of 4096 (~ 10ms)
servoMax = 400  				# Max pulse length out of 4096 (~ 20ms)
speed = 0.2						# servo moving speed

# Initialise the PWM device using the default address
pwm = PWM(board)
#pwm = PWM(board, debug=True)

pwm.setPWMFreq(freq)			# Set frequency to 50 Hz

turnout = []
input = []
route = []

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
				m = re.match("[Tt].*[:](.*)[:](.*)[:](.*)[:](.*)", regel)

				if m:			# break down Turnout line
					id = int(m.group(1))
					board = int(m.group(2))
					channel = int(m.group(3))
					name = (m.group(4))
					turnout.append([id, board, channel, name])
				else:
					print "Syntax fout in Turnout regel", lc

									# Is this a 'name' line?
			elif (type == "N" or type == "n"):
				m = re.match("[Nn].*[:](.*)", regel)

				if m:			# break down Name line
					name = (m.group(1))
					print "name =", name
				else:
					print "Syntax fout in Name regel", lc

									# Is this an 'input' line?
			elif (type == "I" or type == "i"):
				m = re.match("[Ii].*[:](.*)[:](.*)[:](.*)", regel)

				if m:			# break down Input line
					id = int(m.group(1))
					gpio = int(m.group(2))
					name = (m.group(3))
					input.append([id, gpio, name])
#					print "ID =", id, "GPIO =", gpio, "name =", name
				else:
					print "Syntax fout in Input regel", lc

									# Is this a 'route' line?
			elif (type == "R" or type == "r"):
				m = re.match("[Rr].*[:](.*)[:](.*)[:](.*)", regel)

				if m:			# break down Route line
					id = (m.group(1))
					combo = (m.group(2))
					settings = (m.group(3))
					route.append([id, combo, settings])
#					print "ID =", id, "Route =", combo, "settings =", settings
				else:			# line type not defined
					print "Syntax fout in Route regel", lc

								# read next line		
		regel = myfile.readline()
		lc = lc+1				# increment line count

	myfile.close()				# close config file
	return res


# ------------------------------------------------------------------------
# test routine
# ------------------------------------------------------------------------
def setThemMin(x, y):
	for channel in range(x, y):
		pwm.setPWM(channel, 0, servoMin)
		time.sleep(speed)


# ------------------------------------------------------------------------
# test routine
# ------------------------------------------------------------------------
def setThemMax(x, y):
	for channel in range(x, y):
		pwm.setPWM(channel, 0, servoMax)
		time.sleep(speed)


# ------------------------------------------------------------------------
# main line
# ------------------------------------------------------------------------
if (read_config_file()):
	print "Conf file read OKAY"
	#while (True):					# Change angle of servo 
	#	setThemMin(0, 4)
	#	setThemMax(0, 4)
else:
	print "Conf file read WRONG"

print "Turnouts:"
print turnout
print "Inputs:"
print input
print "Routes:"
print route
