#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	gawRelayHandler.py
# Author		:	Gerard Wassink
# Date			:	26 september 2015
#
# Function		:	Handle relay control for the:
#					gaw_Rasp_I2C_16_Relays board
#
# Offers		:
#		setRelay(boardAddress, channel, position)
#
#		where:
#			boardAddress (0x20 - 0x27)
#			channel (0-15)
#				0-7 	GPIOA ports 0 - 7
#				8-15	GPIOB ports 0 - 7 
#			position (0 or 1)
#				0 = in rest
#				1 = in action
#
# Prerequisites	:
#		smbus
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

import smbus
import time

# --------------------------------------------------------------------------------
# Class for Handling relay's through the gaw_Rasp_I2C_16_Relays boards
# --------------------------------------------------------------------------------
class relayHandler:

	def __init__(self):
		self.lastAddress = -1
										# Determine bus number
		self.bus = smbus.SMBus(1) 		# Rev 2 Pi uses 1
								# Adresses for IOCON.BANK = 0 
								# (default at startup and after reset)

								# GPIO bank A
		self.IODIRA	= 0x00		# Pin direction register
		self.IOCON	= 0x0A		# Configuration register
		self.GPIOA	= 0x12		# Port register
		self.OLATA	= 0x14		# Output Latch register

								# GPIO bank B
		self.IODIRB	= 0x01		# Pin direction register
		self.IOCON	= 0x0B		# Configuration register
		self.GPIOB	= 0x13		# Port register
		self.OLATB	= 0x15		# Output Latch register
		

	def initBoard(self, boardAddress):
										# Force device into default state
		self.bus.write_byte_data(boardAddress,self.IOCON,0x00)
										# Set all GPA pins as outputs
		self.bus.write_byte_data(boardAddress,self.IODIRA,0x00)
		self.bus.write_byte_data(boardAddress,self.IODIRB,0x00)

	
	def setRelay(self, boardAddress, channel, position):
		if boardAddress != self.lastAddress:
			self.initBoard(boardAddress)	# Initialize new board
			self.lastAddress = boardAddress	# remember board address
		
		if (channel > -1 and channel < 8):
			self.register = self.GPIOA
			self.olat = self.OLATA
			self.gpio = channel
		elif (channel > 7 and channel < 16):
			self.register = self.GPIOB
			self.olat = self.OLATB
			self.gpio = channel - 8

								# convert self.gpio to an OR-able value
		self.orable = 2 ** self.gpio

								# read current value
		self.oval = self.bus.read_byte_data(boardAddress,self.olat)

		if position == 0:
			self.oval = ~(~self.oval | self.orable)
		elif position == 1:
			self.oval = self.oval | self.orable

		self.bus.write_byte_data(boardAddress,self.register,self.oval)
		
