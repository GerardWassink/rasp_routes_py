# TODO list (rasp_routes_py program)
There are a number of things still to be done before this program is ready to be used:

### layout object
* layout object uitbreiden met
	* config file
	* turnoutList
	* inputList
	* routeList
	* logging & level ?

### std logging?
* logging ombouwen naar standaard Python?

### non standard config file
* be able to read another config file from command line

### calibrate servo's
* build code to be able to calibrate servo's
	* set servo to middle between closed and thrown settings
	* accept input to move towards closed position
	* until user is satisfied and inputs **`done`**
	* accept input to move towards thrown position
	* until user is satisfied and inputs **`done`**

# DONE list

### separate logging into module (DONE 2015-09-14
* make logging a separate re-usable library

	Isolated to file **`gaw_logging.py`** and changed code accordingly.

### bouncing inputs (DONE 2015-09-14)
* the input with switches is not reliable
	* find out cause
	* make it work

	Changed it from falling edge to rising edge detection and built in a check for high input according to a [blog post](https://www.raspberrypi.org/forums/viewtopic.php?t=66936&p=490355) on the RPi forum.

### handle inputs (DONE 2015-09-13)
* building code to handle inputs at 'falling-edge' events; handler routine is present as stub, code has to be added: 
	* wait for two inputs, 
	* sort them, 
	* look for presence of route, 
	* otherwise give error and reset

	Built it in along the lines of [this page](http://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/). Improvements still needed, button input bounces like crazy.

### set routes (DONE 2015-09-13)
* build routine to set routes when a valid route is found
	* recieve route to be set
	* split **`settings`** field in loose characters
	* evaluate actions and act accordingly
