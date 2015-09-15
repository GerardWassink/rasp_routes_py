#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	gawServoHandler.py
# Author		:	Gerard Wassink
# Date			:	15 september 2015
#
# Function		:	Handle servo control for the:
#					Adafruit 16 channel servo HAT stack
#
# Offers		:
#		addBoard(address, frequency)
#		addServo(address, channel)
#		setServo(address, channel, position)
#
# Prerequisites	:
#		Adafruit_PWM_Servo_Driver.py
#		Adafruit_I2C.py
#		time
#		logging
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
# Usage of this library is at the user's own risk, author will not be held
# responsible for any damage to your hardware. Especially the positioning
# of servo's has to be done with the greatest possible care.
#
# ------------------------------------------------------------------------
#				Copyright (C) 2015 Gerard Wassink
# ------------------------------------------------------------------------


from Adafruit_PWM_Servo_Driver import PWM
import time
import logging

# --------------------------------------------------------------------------------
# Class for Handling servo's through the Adafruit servo HAT boards
# --------------------------------------------------------------------------------
class servoHandler:
	def __init__(self):
		self.boardStack = servoBoardStack()
	
	
	def clearServoHandler(self):
		for b in self.boardStack.boardList:
			b.servoList = []
		self.boardStack.boardList = []
	
	
	def addBoard(self, address=0x40, freq=50):
		found = 0
								# Try to find board
		for b in self.boardStack.boardList:
			if b.boardAddress == address:
				found = 1
				break
								# Not found? Add it to the list
		if found == 0:
			self.boardStack.boardList.append(servoBoard(address=address, frequency=freq))


	def addServo(self, address=0x40, channel=0):
		found = 0
								# Find board
		for b in self.boardStack.boardList:
			if b.boardAddress == address:
								# Try to find servo
				for s in b.servoList:
					if s.servoChannel == channel:
						found = 1
						break
								# Not found? Add it to the list
		if found == 0:
			b.servoList.append(servo(address=address, channel=channel))
		else:
			logging.warning("asked to add same servo twice, address:" + \
						hex(address) + ", channel:" + \
						str(channel))


	def setServo(self, address, channel, pos):
		found = 0
								# Find board
		for b in self.boardStack.boardList:
			if b.boardAddress == address:
								# Find servo
				for s in b.servoList:
					if s.servoChannel == channel:
						found = 1
								# found: set board address and set servo to pos
						s.setPos(pos)
								# Not found: Error
		if found == 0:
			logging.warning("asked to set servo that is not in the list, address:" + \
						hex(address) + ", channel:" + \
						str(channel))


# --------------------------------------------------------------------------------
# Helper class for Handling board stacks 
# 	This is formal and a bit theoretical to make the class tree represent the 
# 	outside world
# --------------------------------------------------------------------------------
class servoBoardStack:
	def __init__(self):
		self.boardList = []


# --------------------------------------------------------------------------------
# Helper class per servo HAT board, each holds max 16 channels (0-15)
#	class stores address and desired frequency per board
#	also it contains a list of connected servo's
# --------------------------------------------------------------------------------
class servoBoard:
	def __init__(self, address=0x40, frequency=50):
		self.boardAddress = address
		self.boardFrequency = frequency
		#self.pwm = PWM(self.boardAddress, debug=True)
		self.pwm = PWM(self.boardAddress)			# set board to be used
		self.pwm.setPWMFreq(self.boardFrequency)	# just to be sure, set frequency
		self.servoList = []


# --------------------------------------------------------------------------------
# Helper class per servo
#	for convenience it stores the address as well as the channel
#
#	offers	: setPos(position)
#				will not set servo to same position more than once
# --------------------------------------------------------------------------------
class servo:
	def __init__(self, address=0x40, channel=0):
		self.servoAddress = address
		self.servoChannel = channel
		self.lastPos = 0
	
	
	def setPos(self, pos):
								# Prevent doing it twice to same pos
		if pos != self.lastPos:
			self.lastPos = pos	# Store position
								# Initiate board address
			self.pwm = PWM(self.servoAddress)
								# Set the servo position
			self.pwm.setPWM(self.servoChannel, 0, pos)
								# wait for a bit to allow for positioning
			time.sleep(0.3)


