# gawServoCalibrate.md

This little utility comes with the rasp_routes_py program and give the user the possibility to calibrate her servo's. Use it to find the desired positions for Closed and Thrown turnouts. (of course she can also use it on other occasions... ;-)

### Interface

The program prompts for a board id:

`enter board> `

user enters: a board number in decimal (so 0x40 becomes 64) OR the letter `q` to end the program.

System responds by giving back the board number entered and asking for a channel:

`B:64`

`enter channel> `

user enters a channel, from 0-15 OR the letter `q` to go back to the board prompt.

System responds by giving back the board and channel number entered and asking for a position:

`B:64 C:5`

`enter position> `

user enters a position OR the letter `q` to go back to the cahnnel prompt.

System responds by giving back the board and channel number entered as well as the entered position. It also sets the given servo to the position entered. Now it asks for a position again:

`B:64 C:5 pos:220`

`enter position> `


**CAVEAT: entering invalid positions might damage your servo's. Use at own risk!**


## See also:
[Readme file](../README.md)

[Explanation of the configuration file](../doc/CONFIG.md)

[Installation HOW TO file](../doc/INSTALL.md)

[Calibrating your servo's](../doc/gawServoCalibrate.md)

[Roadmap or TODO file](../doc/TODO.md)

[License file](../doc/LICENSE)
