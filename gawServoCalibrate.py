#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	gawServoCalibrate.py
# Author		:	Gerard Wassink
# Date			:	15 september 2015
#
# Function		:	asks for board, channel and position to be able to
#					calibrate your servos. see gawServoCalibrate.md
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
import gawServoHandler
import time
import logging

# ------------------------------------------------------------------------
# set logging level and format
# ------------------------------------------------------------------------
logging.basicConfig(level=logging.DEBUG, \
			format='%(asctime)s: %(levelname)s: %(message)s', \
			datefmt='%Y-%m-%d,%I:%M:%S')


# ------------------------------------------------------------------------
# Class definition
# ------------------------------------------------------------------------

myServoHandler = gawServoHandler.servoHandler()


# ------------------------------------------------------------------------
# Code Start
# ------------------------------------------------------------------------

done = 0

while (1):
	sBoard = raw_input("enter board> ") 
	if sBoard == "q": break
	board = int(sBoard)
	print "B:" + sBoard
	
	while (1):
		sChannel = " "
		sChannel = raw_input("enter channel> ") 
		if sChannel == "q": break
		channel = int(sChannel)
		print "B:" + sBoard + " C:" + sChannel + " to mid-position (300)"
		myServoHandler.setServo(board, channel, 300)

		while (1):
			sPos = raw_input("enter pos> ")
			if sPos == "q": break	
			pos = int(sPos)
			myServoHandler.setServo(board, channel, pos)
			print "B:" + sBoard + " C:" + sChannel + " pos:" + sPos

print "Done"

exit()
