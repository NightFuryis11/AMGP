# AMGP - The Automated Map Generation Program
Copyright (C) 2022-2025, Samuel Nelson Bailey

The Automated Map Generation Program is a Python-core program with a tKinter UI used to produce a variety of customizable meteorological and GIS-style maps and figures, originally based on my Freshman coursework at Valparaiso Univeristy. It allows users to pull data from a variety of remote sources, compile and map the data automatically, and produce high-resolution images for a variety of uses. AMGP thrives on customizability, both providing some official modules for data sources and formats with official AMGP support, and allowing for users to create their own custom modules that will simply run as expected when placed into the appropriate folder.

## Installation
**Currently only Windows systems are supported, this will be changed in the near future.**\
AMGP has two installation methods: direct source code download and source + environment download.

### Source and Environment (Recommended)
Check the latest releases page and download the "AMGP+ENV_v\*" release and place it wherever in your file structure you like. Run the "start_install_amgp_\*" that corresponds to your operating system.\
This script, whether it's a batch file or a shell script for your system, will install the bare minimum environment required to run AMGP via miniconda3, using the requirements.txt distributed along with the rest of the install.\
Running this script again will work to start AMGP on subsequent startups.

### Source Only
Download the latest release of "AMGP_v*" from the releases page and place it wherever you like in your file structure. In order to launch AMGP, you must change the %PYTHON_EXE% variable within "start_amgp_\*" and "start_amgp_noui_\*" to the path of the Python executable within your local environment that has all the required packages listed below.\
Running either of scripts as seen below will then start AMGP as long as your environment supports it.

## Running AMGP
If you installed the environment along with your AMGP install, you can simply run your copy of "start_install_amgp_\*" again to run AMGP with no issues.\
If you installed AMGP without the packaged environment, the AMGP base folder contains two scripts based on your operating system: "start_amgp_\*" and "start_amgp_noui_\*".\
"start_amgp_\*" is the full AMGP experience, while "start_amgp_noui_\*" opens a command line where you can type the absolute file path to a preset.json file (those made naturally with AMGP are stored in AMGP/Presets/AMGP_MENU) to make maps without opening the AMGP UI.\
Alternatively - and most usefully for automated production of maps in an internal system - "start_amgp_noui_\*" can be run with an argument following it containing *either* an absolute path to a preset.json file *or* a *.txt file where each line is an absolute path to a preset.json file. Both of these will cause AMGP to run in the background and close once it has produced the desired maps.

### Requirements
AMGP has been tested on the following Python versions:
- Python 3.11.7 - AMGP v1.0.0
- Python 3.12.9 - Packaged with AMGP v1.0.0

AMGP is *suspected* to work on Python 3.11+, but this has not been rigorously tested.

Below are the package requirements to run all core and official modules and the AMGP version this requirement was introduced in. If any specific package version requirements are discovered, they will be added here as well.\
cartopy - AMGP v1.0.0\
metpy - AMGP v1.0.0\
numpy - AMGP v1.0.0\
pandas - AMGP v1.0.0\
pillow - AMGP v1.0.0\
siphon - AMGP v1.0.0\
xarray - AMGP v1.0.0

## User Customization
**More information, and full tutorials on how to create Styles and Modules, will be available soon, but for now only a brief description will have to suffice. Do note, they are fully implemented even if the description isn't here yet.**
AMGP has been designed since Beta v0.4.0 to be easily able to accomodate users creating their own custom Modules and Styles with which to create plots using their own data and with their own layouts. This comes in the form of two separate files that the user can alter: *Styles* and *Modules*.

### Styles
Found in AMGP/Styles, *Styles* are Python scripts that create a MatPlotLib figure with a specified number and placement of axes that AMGP uses to arrange data (as each axis can have its own projection, data, etc), and are the foundation of how the other parts of AMGP are structured around, due to the variable of axis count.

### Modules
Found in AMGP/ModulesUser for custom modules, *Modules* are Python scripts used for data acquisition and plotting on the axes provided by the selected Style. While there is a lot of freedom in what can be done inside an AMGP Module - technically it doesn't even have to provide anything back to the base program, and can be used to prompt other subprocesses - there are a few required methods within the script in order for it to function properly.

### Other
If you wish to define custom codes to produce specific plotted regions, create the file "AMGP/Resources/user_area_definitions.json" with a similar format to the provided "AMGP/Resources/amgp_area_definitions.json". These formated latitudes and longitudes can be used by AMGP to define the bounds of a given map projection within the projections window, used with maps, etc.

## Features
### Current (v1.0.0)
- The basic framework and UI of AMGP are complete, and will likely see very few changes in the near future. It is this that I was waiting for prior to releasing v1.0.0.
- Surface and upper-air observations for the United States
- GFS filled temperature contours

### Planned
- Full Linux/MacOS install support (this will be difficult, seeing as I don't have a Mac)
- More complete surface and upper-air data for worldwide domains
- Built-in skew-t Styles and data sources
- Full GFS, NAM, RAP, and HRRR support for recent and archive data (potentially implimenting Herbie?), with the latter being a more difficult challenge to source.
- Cross-sections of interpolated and model data based on a pair of lat-lon coordinates
- Automatic updating via the install and run batch files
- A lot more that I've not even been able to put to words yet

## License
AMGP - The Automated Map Generation Program\
Copyright (C) 2022-2025 Samuel Nelson Bailey

This program is free software: you can redistribute it and/or modify\
it under the terms of the GNU General Public License as published by\
the Free Software Foundation, either version 3 of the License, or\
(at your option) any later version.

This program is distributed in the hope that it will be useful,\
but WITHOUT ANY WARRANTY; without even the implied warranty of\
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\
GNU General Public License for more details.

You should have received a copy of the GNU General Public License\
along with this program.  If not, see <https://www.gnu.org/licenses/>.
