# AMGP - The Automated Map Generation Program
Copyright (c) 2023, Samuel Nelson Bailey
  
The Automated Map Generation Program is a Python-core program used to produce a variety of customizable meteorological maps, originally based on my freshman coursework. It allows users to use raw data from a variety of sources in the backend of the program, automatically compiling them and saving them as high-definition images. With a variety of interchangeable modules to handle the program's many mapping capabilities, adding and editing functionality to your own version is as simple as learning Python and finding your data.

## Raw Python Usage
If you download the source code, you can run:
```
python AMGP/Main.py
```
from your terminal.

You'll be prompted via your terminal to edit the parameters to create maps, which will be saved to AMGP/Maps/{%Y%m%d}.

## Creating Custom Modules
If you want to create your own modules for AMGP, the things to keep in mind are as follows:

~~~python
# Your module must be named
"AMGP_*.py"
# Where * is the name of your module.
# Upon starting AMGP, with your module in "AMGP/Modules" you should be greeted by a message stating
"<startup> AMGP_* loaded as amgp*"
# Any code references within AMGP will refer to the lowercase version of the module name, without the underscore.

# Your module must import AMGP_UTIL, as the content of the utilities module is vital to everything AMGP does.
from Modules import AMGP_UTIL as amgp

# Your module must have the following:
def info():
  return {
          "name" : str(module_name) # module_name is equivalent to AMGP_*
          "priority" : float(priority) # priority dictates when the module is ordered among other modules (for data modules, this dictates map layer plotting order)
          "type" : int(module_type) # module_type tells AMGP how this module should be treated. 0 is a utility module, 1 is a data acquisition module, 2 is an input loop, 3 combines data acquisition and input loops
         }


# A module of type 1 or 3 must also have:
def getFactors():
  return {
          str(factor_name) : int(timecode) # where factor_name is the name of the factor to plot and the timecode as defined below, for each factor
         }

def factors():
  print("<factors_{module name}> '{factor name}' - {factor description}") # for each factor

# Time is a Time object (which contains many datetime objects, refer to the UTIL module)
# factors are any factors that AMGP automatically detected from the input, found in your module's getFactors()
# values are the full set of input conditions given when the program was run
def Retrieve(Time: Time, list: factors, dict: values):
  # Whatever the heck the module does.
  return partialPlotsList # appends to panel.plots as a return. In the future, there will be the option to have modules that DON'T depend on this function


# A module of type 2 or 3 must also have:

def init():
  # What you actually need to do within this function is up to how your module will function, but you should call your input loop within it
  # your input loop should also be able to import the base modules - specifically AMGP_PLT - and be able to call the init() function within it, otherwise there will be no easy way to return to the base of the program
~~~
