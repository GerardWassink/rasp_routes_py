# TODO list (rasp_routes_py program)
There are a number of things still to be done before this program is ready to be used:

### handle inputs
* building code to handle inputs at 'falling-edge' events; handler routine is present as stub, code has to be added: 
	* wait for two inputs, 
	* sort them, 
	* look for presence of route, 
	* otherwise give error and reset

### set routes
* build routine to set routes when a valid route is found
	* recieve route to be set
	* split **`settings`** field in loose characters
	* evaluate actions and act accordingly

### calibrate servo's
* build code to be able to calibrate servo's
	* set servo to middle between closed and thrown settings
	* accept input to move towards closed position
	* until user is satisfied and inputs **`done`**
	* accept input to move towards thrown position
	* until user is satisfied and inputs **`done`**
