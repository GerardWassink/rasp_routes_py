# README
This Python program, **`rasp_routes_py`**, allows you to set routes on your model railroad layout using a Raspberry Pi.

## History
For my model railroad I was looking for a way to be able to set routes thru series of turnouts by pressing one button on either end of the desired route. Eventually the rasp_routes program, written in C, came out of these efforts. See the rasp_routes repository. But I couldn't find a suitable C library to work with the Adafruit 16 channel servo HAT. I found one in python, so I rewrote the program logic in python.

At this moment (september 19, 2015) I consider it working.

## Commands
When the program is running, it presents the user with a prompt: "**`> `**" to indicate it expects a command. type **`h`** or **`help`** to see which command are available.

## License / availability
This software is available under the conditions of the GNU General Public License. See the [LICENSE file](./LICENCSE) for further details.

## Use at own risk
Usage of this program is at the user's own risk, author will not be held responsible for any damage to your hardware. Especially the positioning of servo's has to be done with the greatest possible care.

## See also:
[Readme file](./README.md)

[Explanation of the configuration file](./doc/CONFIG.md)

[Installation HOW TO file](./doc/INSTALL.md)

[Calibrating your servo's](./doc/gawServoCalibrate.md)

[Roadmap or TODO file](./doc/TODO.md)

[License file](./LICENSE)
