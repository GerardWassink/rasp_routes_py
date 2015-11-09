# Configuration file
The program is driven by a configuration file in XML format. This file is called **`rasp_routes_py.xml`** rather self-explanatory. To be sure, a quick description follows below:

## Sections
In the configuration file we use sections and labels. In the list here-after you will find sections in **`bold`** and labels in ***`italic`***. In the XML file you will see things like:

<**`section`** ***`label1`***="value" ***`label2`***="value"/>

#### List of sections and labels:
* **`layout`** :: Contains all other sections

	* **`description`** :: contains general information
		* ***`name`*** :: contains the name of the layout
		* ***`owner`*** :: when present, contains the name of the layout owner

	* **`input_range`** :: specifies ranges for input specifications
		* ***`gpio_min`*** :: gpio's specified may not be less then this number
		* ***`gpio_max`*** :: gpio's specified may not be higher then this number

	* **`relay_turnout_range`** or **`servo_turnout_range`** :: specifies ranges for relay or servo turnout specifications
		* ***`adr_min`*** :: boardAddress specified may not be less then this number
		* ***`adr_max`*** :: boardAddress specified may not be higher then this number
		* ***`pos_min`*** :: position specified may not be less then this number
		* ***`pos_max`*** :: position specified may not be higher then this number

	* **`turnouts`** :: contains turnout specifications
		* **`turnout`** :: specifies characteristics of one turnout
			* ***`type`*** :: contains "servo" or "relay"
			* ***`boardAddress`*** :: the address from which the servo is driven
			* ***`channel`*** :: the channel on that board (0-15)
			* ***`posclos`*** :: the position when closed
			* ***`posthro`*** :: the position when opened
			* ***`name`*** :: the name of the turnout
		
	* **`inputs`** :: contains input specifications
		* **`input`** :: specifies characteristics for one input
			* ***`gpio`*** :: specifies the gpio pin for this input
			* ***`name`*** :: specifies the (spur) name for this input

	* **`routes`** :: contains route specifications
		* **`route`** :: specifies characteristics for one route
			* ***`input1`*** :: one of two inputs that must be activated for the route
			* ***`input2`*** :: the other input that must be activated for the route
			* **`set_turnout`** :: turnout to be set for this route
				* ***`name`*** :: the name of the turnout, referring to the turnout list
				* ***`position`*** :: the position to which the turnout is to be set for this route


### Special label descriptions
Various special labels are described below.

**`gpio`** - This is the number of the GPIO port that will be used for input.

Mind you: These are NOT the pin numbers on the 40 pin header, they are the actual GPIO numbers as defined by Broadcom, for example: header pin 40 on the RPi connects to GPIO number 21. It is this last number, 21, that you would code here. Check the bcm2835 documentation for the relation between GPIO's and pin numbers.

All input GPIO's will be inilialized as **`pull_up_down=GPIO.PUD_UP`**, meaning that they have to be pulled down to GND to activate.

**`type`** - the type of turnout control, possible values:

* ***`servo`*** the turnout is driven by an Adafruit servo HAT
* ***`relay`*** the turnout is driven by my [relay board](https://github.com/GerardWassink/gaw_Rasp_I2C_16_Relays)

**`boardAddress`** - identification of the board the servo or relay is connected to. These numbers are specified in the documentation as hexadecimal numbers (i.e. 0x20 or 0x40). For ease of parsing this program expects decimal numbers, so 0x40 will be specified as 64 here.

**`channel`** - the slot number for the servo or relay (range 0-15) on the board given in the same line.

**`posclos`** - the desired position for this turnout when in the closed position (the range for servo's and relays can be specified in the file, but commonly they are 210-400 for servo's, and 0 or 1 for relays).

**`posthro`** - the desired position for this turnout when in the thrown position (the range for servo's and relays can be specified in the file, but commonly they are 210-400 for servo's, and 0 or 1 for relays).

**`input1`** **`input2`** - A route is defined by two inputs, one as start- and one as end-point. Routes are specified by two input gpio_numbers. When for example we want a route from input 16 to input 18, we specify "16:18". Note that the route from 18 to 16 is identical (duh). While running, the program evaluates activated inputs in numerical order, so when one activates inputs 18 and 16 in that order, the program will evaluate that against a route identified by "16:18".


## See also:
[Readme file](../README.md)

[Explanation of the configuration file](../doc/CONFIG.md)

[Installation HOW TO file](../doc/INSTALL.md)

[Calibrating your servo's](../doc/gawServoCalibrate.md)

[Roadmap or TODO file](../doc/TODO.md)

[License file](../LICENSE)
