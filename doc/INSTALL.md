# Installation
This Python program, **`rasp_routes_py`**, can be used to control routes on your model railroad layout using a Raspberry Pi.

## Files
The files you need are in the Github repository. The easiest way to obtain those files in to obtain them from [Github](https://github.com).

When you do not have **`git`** installed on your system, you first must install it on your Raspberry Pi by doing:

**`sudo apt-get install git`**

Now you have installed the git software. you can now interact with [Github](https://github.com). Now, to obtain the software, execute the following commands:

**`cd`**

**`git clone http://github.com/GerardWassink/rasp_routes_py`**

In your home directory, you now have a sub-directory with the name **`~/rasp_routes_py/`**. In that directory you will find Adafruit libraries and a library by me, **`gawServoHandler`**. Those libraries are needed to run the programs. The programs are:

* **`rasp_routes_py.py`** (see [the help file](./README.md))
* **`gawServoCalibrate.py`** (see [the help file](./gawServoCalibrate.md))

When you want to start these programs, be sure to do so using the **`sudo`** command. When you are in their directory:

* **`sudo ./rasp_routes_py.py`**
* **`sudo ./gawServoCalibrate.py`**


## License / availability
This software is available under the conditions of the GNU General Public License. See the [LICENSE file](./LICENCSE.md) for further details.

## Use at own risk
Usage of this program is at the user's own risk, author will not be held responsible for any damage to your hardware. Especially the positioning of servo's has to be done with the greatest possible care.

## See also:
[Readme file](../README.md)

[Explanation of the configuration file](../doc/CONFIG.md)

[Installation HOW TO file](../doc/INSTALL.md)

[Calibrating your servo's](../doc/gawServoCalibrate.md)

[Roadmap or TODO file](../doc/TODO.md)

[License file](../LICENSE)
