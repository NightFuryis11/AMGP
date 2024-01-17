################################################
#                                              #
#       Automated Map Generation Program       #
#                                              #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.4.0                 #
#                                              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
from io import StringIO
from urllib.request import urlopen
from siphon.simplewebservice.iastate import IAStateUpperAir
from siphon.catalog import TDSCatalog

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from metpy.io import add_station_lat_lon
from metpy.io import metar
from metpy.plots import declarative, PlotGeometry
from metpy.units import units
import metpy.calc as mpcalc
import xarray as xr
import pandas as pd
import geopandas as gpd
from collections import Counter, OrderedDict
import numpy as np
import math
import os
import sys
from PIL import Image as PImage
from PIL import ImageDraw, ImageFont, ImageFilter
import json
import glob
import contextlib
from importlib import import_module

from tkinter import *
from tkinter import ttk

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)

#----------------- AMGP IMPORTS -------------------#

try:
    from Modules import AMGP_UTIL as amgp
    if len(sys.argv) == 1:
        print("(AMGP_Main) <startup> AMGP_UTIL imported as amgp")
except:
    sys.exit("(AMGP_Main) <error> AMGP cannot function without the Utilities module.")

try:
    from Modules import AMGP_MAP as amgpmap
    if len(sys.argv) == 1:
        print("(AMGP_Main) <startup> AMGP_MAP imported as amgpmap")
except:
    sys.exit("(AMGP_Main) <error> AMGP cannot function without the Mapping module.")

try:
    from Modules import AMGP_PLT as amgpplt
    if len(sys.argv) == 1:
        print("(AMGP_Main) <startup> AMGP_PLT imported as amgpplt")
except:
    sys.exit("(AMGP_Main) <error> AMGP cannot function without the Plotting module.")

amgputilmodules = {}
amgpmodules = {}
amgpmenumodules = {}
amgpcombomodules = {}

amgpmodulenames = {0:"AMGP_PLT",100:"AMGP_MAP",200:"AMGP_UTIL"}

for module in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}/Modules"):
    if module.startswith("AMGP_") and (module.replace(".py","") != "AMGP_UTIL") and (module.replace(".py","") != "AMGP_PLT"):
        strp = module.replace(".py", '')
        var = strp.replace("_", '').lower()
        if (module.replace(".py","") not in amgpmodulenames.values()):
            globals()[f"{var}"] = import_module(f'Modules.{strp}')
            if len(sys.argv) == 1:
                print(f"(AMGP_Main) <startup> {strp} imported as {var}")
        tmp = globals()[f"{var}"].info()
        if int(tmp['uid'][3:-4]) == 0:
            amgputilmodules[int(tmp['uid'][4:])] = globals()[f"{var}"]
            amgputilmodules = dict(sorted(amgputilmodules.items()))
        elif int(tmp['uid'][3:-4]) == 1:
            amgpmodules[int(tmp['uid'][4:])] = globals()[f"{var}"]
            amgpmodules = dict(sorted(amgpmodules.items()))
        elif int(tmp['uid'][3:-4]) == 2:
            amgpmenumodules[int(tmp['uid'][4:])] = globals()[f"{var}"]
            amgpmenumodules = dict(sorted(amgpmenumodules.items()))
        elif int(tmp['uid'][3:-4]) == 3:
            amgpcombomodules[int(tmp['uid'][4:])] = globals()[f"{var}"]
            amgpcombomodules = dict(sorted(amgpcombomodules.items()))
        amgpmodulenames[int(tmp['uid'][4:])] = f"{strp}"
    elif module.replace(".py","") == "AMGP_PLT":
        globals()[f"amgpplt"] = import_module(f'Modules.AMGP_PLT')
        amgpmenumodules[0] = globals()[f"amgpplt"]

amgpmodulenames = dict(sorted(amgpmodulenames.items()))

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

version = "0.4.0"

presets = []

# Opening the config file and manual, and finding presets.
if os.path.isfile(f"{os.path.dirname(os.path.realpath(__file__))}/config.json"):
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/config.json", "r") as cfg:
        config = json.load(cfg)

for folder in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}/Presets"):
    for preset in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}/Presets/" + folder):
        if preset.endswith('.json'):
            presets.append([f"{folder}-{preset.replace('.json','')}"])

# Init
area_dictionary = dict(config['areas'])
area_dictionary = {k: tuple(map(float, v.split(", "))) for k, v in area_dictionary.items()}

print(f"(AMGP_Main) <startup> Loaded AMGP modules: {list(amgpmodulenames.values())}")
print(f"(AMGP_Main) <startup> You are using AMGP version {version}")

if len(sys.argv) > 1:
    cfgver = config["config_ver"].split('.')
    amgpver = version.split('.')
    if config["config_ver"] != version:
        if cfgver[0] > amgpver[0]:
            sys.exit()
        elif cfgver[0] < amgpver[0]:
            sys.exit()
        elif cfgver[1] > amgpver[1]:
            sys.exit()

    pack = {'modulenames':amgpmodulenames,
            'utilmods':amgputilmodules,
            'datamods':amgpmodules,
            'menumods':amgpmenumodules,
            'combomods':amgpcombomodules,
            'customareas':area_dictionary,
            'ver':version,
            'presets':presets,
            'config':config}

    amgpplt.init(pack, sys.argv[1])
    
else:
    # Version handler
    cfgver = config["config_ver"].split('.')
    amgpver = version.split('.')
    if config["config_ver"] != version:
        if cfgver[0] > amgpver[0]:
            sys.exit(f"(AMGP_Main) <error> Your installed AMGP version is out of date! Config version {config['config_ver']} found.")
        elif cfgver[0] < amgpver[0]:
            sys.exit(f"(AMGP_Main) <error> The config we found is out of date! Config version {config['config_ver']} found.")
            # attempt to update the config in the future
        elif cfgver[1] > amgpver[1]:
            sys.exit(f"(AMGP_Main) <error> Your installed AMGP version is out of date! Config version {config['config_ver']} found.")
        elif cfgver[1] < amgpver[1]:
            print(f"(AMGP_Main) <warning> The loaded config file is of an earlier version ({config['config_ver']}), consider updating it.")
        else:
            print(f"(AMGP_Main) <warning> The loaded config file we found is of a different compatible version version ({config['config_ver']}).")
    print("(AMGP_Main) <menu> Config loaded.")

    # Packing and starting the program
    
    pack = {'modulenames':amgpmodulenames,
            'utilmods':amgputilmodules,
            'datamods':amgpmodules,
            'menumods':amgpmenumodules,
            'combomods':amgpcombomodules,
            'customareas':area_dictionary,
            'ver':version,
            'presets':presets,
            'config':config}

    amgp.getPing(amgp.setTime(), amgpmodules.values())
    
    amgpplt.init(pack)