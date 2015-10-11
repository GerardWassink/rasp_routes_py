#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	gawServoHandler.py
# Author		:	Gerard Wassink
# Date			:	16 september 2015
#
# Function		:	Handle servo control for the:
#					Adafruit 16 channel servo HAT stack
#
# Offers		:
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
		self.frequency = 50
		self.lastAddress = -1
	
	def setServo(self, address, channel, pos):
		if address != self.lastAddress:
			self.pwm = PWM(address)				# set board address
			self.pwm.setPWMFreq(self.frequency)	# just to be sure, set frequency
		self.pwm.setPWM(channel, 0, pos)	# Set the servo position
		time.sleep(0.3)						# wait for a bit to allow for positioning
