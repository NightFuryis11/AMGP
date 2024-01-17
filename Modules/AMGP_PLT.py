################################################
#                                              #
#       Automated Map Generation Program       #
#               Plotting Module                #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.5.0                 #
#             AMGP Version: 0.4.0              #
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
from collections import Counter
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

from Modules import AMGP_MAP as amgpmap
from Modules import AMGP_UTIL as amgp

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_PLT",
            'uid':"00220100"}

def init(pack, QRA=None):
    global unpack
    global area_dictionary
    global version
    global amgpmodules
    global noShow
    global amgpmenumodules
    global amgpcombomodules
    global modules
    unpack = pack

    config = unpack['config']
    area_dictionary = unpack['customareas']
    version = unpack['ver']
    modules = unpack['modulenames']
    amgpmodules = unpack['datamods']
    amgpmenumodules = unpack['menumods']
    amgpcombomodules = unpack['combomods']

    amgp.getTime()
    
    if QRA == None:
        print("(AMGP_PLT) <menu_init> Opened the singular plotting interface <menu_init>")
        noShow = False
        #print(modules[600])
        #print(amgpmodules[600])
        imports(unpack)
        amgp.PrintLocalData(amgp.LocalData())
        
        #setInit()
        presetLoad('default')
        singleLoads()
        inputChain()
    else:
        if QRA.startswith("{"):
            QRA = json.loads(QRA)
            for c, w in QRA.items():
                for k, v in unpack['modulenames'].items():
                    if c.upper() in v:
                        QRA[c]["extras"]["amgpmodules"] = unpack["datamods"]
                        for key, value in unpack['menumods'].items():
                            if key == k:
                                value.run(QRA[c]["values"], QRA[c]["extras"])

        if QRA.endswith(".txt"):
            with open(QRA, "r") as source:
                for line in source:
                    uline = json.loads(line)
                    for c, w in uline.items():
                        for k, v in unpack['modulenames'].items():
                            if c.upper() in v:
                                uline[c]["extras"]["amgpmodules"] = unpack["datamods"]
                                for key, value in unpack['menumods'].items():
                                    if key == k:
                                        value.partialInit(unpack)
                                        value.run(uline[c]["values"], uline[c]["extras"])

        if QRA.endswith(".json"):
            with open(QRA, "r") as source:
                dic = json.load(source)
                for k, v in unpack['modulenames'].items():
                    if dic["type"].upper() in v:
                        for key, value in unpack['menumods'].items():
                            if key == k:
                                extras = {"amgpmodules": unpack["datamods"], "S": True, "noShow": True, "proj": "", "direct": True, "altDir": False, "altDirCon": False, "title": ""}
                                value.run(dic["settings"], extras)

def partialInit(pack):
    global unpack
    unpack = pack
    imports(unpack)

def imports(unpack):
    for module in unpack['datamods'].values():
        import_module(module.__name__)

# Definitions
def inputChain():
    amgp.ClearTemp()
    global loaded
    global title
    global noShow
    
    print("(AMGP_PLT) <menu> Input commands, or type 'help'.")
    comm = input("(AMGP_PLT) <input> ")
    
    command = comm.split(" ")
    
    if command[0] == "list":
        print("(AMGP_PLT) <list> Type 'time' to set and print the current time.")
        print("(AMGP_PLT) <list> Type 'preset {name}' to load a map preset.")
        print("(AMGP_PLT) <list> Type 'preset list' to list available presets.")
        print("(AMGP_PLT) <list> Type 'factors' to list accepted map factors.")
        print("(AMGP_PLT) <list> Type 'paste' to see the currently loaded values.")
        print("(AMGP_PLT) <list> Type 'edit {parameter} {value}' to edit a loaded parameter.")
        print("(AMGP_PLT) <list> Type 'edit Factors {(optional) add/remove} {value}' to edit loaded factors.")
        print("(AMGP_PLT) <list> Type 'save {preset name}' to save the current settings as a preset.")
        print("(AMGP_PLT) <list> Type 'run' to run with the current settings.")
        print("(AMGP_PLT) <list> Type 'switch {module}' to change to a different menu module.")
        print("(AMGP_PLT) <list> Type 'quit' to exit without running.")
        inputChain()
    
    
    if command[0] == 'time':
        currentTime = amgp.getTime()
        inputChain()
#    elif command[0] == 'update':
#        cfgUpdate()
#        inputChain()
    elif command[0] == 'preset':
        if command[1] == 'list':
            plotkeys = []
            for item in unpack['presets']:
                spi = item[0].split("-")
                if spi[0] == "plot":
                    plotkeys.append(spi[1])
            print("(AMGP_PLT) <presets> Below is the list of all currently loaded presets:")
            for item in plotkeys:
                print(f"(AMGP_PLT) <presets> (obs) {item}")
            inputChain()
        else:
            try:
                presetLoad(command[1])
                singleLoads()
            except:
                print("(AMGP_PLT) <error> That is not a valid preset name!")
            inputChain()
    elif command[0] == 'factors':
        for module in amgpmodules.values():
            module.factors()
        inputChain()
    elif command[0] == 'paste':
        singleLoads()
        inputChain()
    elif command[0] == 'edit':
        if command[1] in ["Level", "Date", "Delta", "Factors", "Area", "DPI", "Scale", "PRF", "BF", "Smooth", "Projection", "TM", "CM", "LDS"]:
            if command[1] == "Level":
                loaded.update({'level':command[2]})
            if command[1] == "Date":
                if command[2] == 'recent':
                    loaded.update({'date':command[2]})
                elif command[2] == "today":
                    loaded.update({'date':f'{command[2]}, {command[3]}'})
                else:
                    try:
                        loaded.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}, {command[6]}'})
                    except:
                        loaded.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            if command[1] == "Delta":
                loaded.update({'delta':command[2]})
            if command[1] == "Factors":
                blankFactors = []
                count = 0
                if command[2] == "add":
                    blankFactors = loaded['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            blankFactors.append(command[count])
                        count += 1
                elif command[2] == "remove":
                    blankFactors = loaded['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            if command[count] in blankFactors:
                                blankFactors.pop(blankFactors.index(command[count]))
                            else:
                                print("(AMGP_PLT) <error> That is not a valid factor to remove!")
                                inputChain()
                        count += 1
                else:
                    for item in command:
                        if count > 1:
                            blankFactors.append(command[count])
                        count += 1
                fullFactors = ', '.join(blankFactors)
                loaded.update({'factors':fullFactors})
            if command[1] == "Area":
                loaded.update({'area':command[2]})
            if command[1] == "DPI":
                loaded.update({'dpi':command[2]})
            if command[1] == "Scale":
                loaded.update({'scale':command[2]})
            if command[1] == "PRF":
                loaded.update({'prfactor':command[2]})
            if command[1] == 'BF':
                loaded.update({'barbfactor':command[2]})
            if command[1] == "Smooth":
                loaded.update({'smoothing':command[2]})
            if command[1] == "Projection":
                loaded.update({'projection':command[2]})
            if command[1] == "TM":
                if command[2] not in ["raw","sync","async","near"]:
                    print("(AMGP_PLT) <error> That is not a valid value for the Time Mode!")
                    inputChain()
                loaded.update({'timemode':command[2]})
            if command[1] == "CM":
                if command[2] not in ["recent","latest"]:
                    print("(AMGP_PLT) <error> That is not a valid value for the Convective Mode!")
                    inputChain()
                loaded.update({'convmode':command[2]})
            if command[1] == "LDS":
                count = 0
                partialLDS = []
                for item in command:
                    if count > 1:
                        partialLDS.append(command[count])
                    count += 1
                fullLDS = ", ".join(partialLDS)
                loaded.update({'LDS':fullLDS})
            singleLoads()
            inputChain()
        else:
            print("(AMGP_PLT) <error> That is not a valid parameter to edit!")
            inputChain()
    elif command[0] == 'save':
        save(f'{command[1]}')
        print(f"(AMGP_PLT) <save> Loaded settings saved to Presets/plot as preset: {command[1]}.json")
        inputChain()
    elif command[0] == 'run':
        dosave = input("(AMGP_PLT) <run> Would you like to save this map? [y/n] ")
        if dosave == 'y':
            S = True
            NS = input("(AMGP_PLT) <run> Would you like to show this map? [y/n] ")
            if NS == 'n':
                noShow = True
            else:
                noShow = False
            title = input("(AMGP_PLT) <run> If you would like to override the default title, type the override here. Otherwise, hit enter: ")
        else:
            S = False
            title = ''
        save('prev')
        print("(AMGP_PLT) <run> Previous settings saved.")
        extras = {"amgpmodules": amgpmodules, "S": S, "noShow": noShow, "direct": True, "proj": "", "title": title, "altDir": False, "altDirCon": False}
        run(loaded, extras)
        inputChain()
    elif command[0] == 'switch':
        try:
            y = command[1]
        except:
            print("(AMGP_PLT) <error> Please enter a module name to switch to.")
            inputChain()
        if (f'AMGP_{command[1].upper()}' in modules.values()) or (f'AMGP_{command[1].upper()}' in modules.values()):
            for k, v in modules.items():
                if ((k in amgpmenumodules.keys()) or (k in amgpcombomodules.keys())) and (f'AMGP_{command[1].upper()}' == v):
                    try:
                        newMod = amgpmenumodules[k]
                    except:
                        newMod = amgpcombomodules[k]
                    newMod.init(unpack)
                    break
        print("(AMGP_PLT) <error> That is not a valid module to switch to!")
        inputChain()
    
    elif command[0] == 'ping':
        amgp.getPing(amgp.setTime(), amgpmodules.values())
        inputChain()
    elif command[0] == 'refresh':
        init(unpack)
    elif command[0] == 'quit':
        sys.exit("(AMGP_PLT) <quit> The process was terminated.")
    else:
        print("(AMGP_PLT) <error> That is not a valid command!")
        inputChain()
        
#      ------ End inputChain() ------
        
# Save an obs preset
def save(name):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    saveState = {"level":f"{loaded['level']}","date":f"{loaded['date']}","delta":f"{loaded['delta']}","factors":f"{loaded['factors']}","area":f"{loaded['area']}","dpi":f"{loaded['dpi']}","scale":f"{loaded['scale']}","prfactor":f"{loaded['prfactor']}","barbfactor":f"{loaded['barbfactor']}","smoothing":f"{loaded['smoothing']}","projection":f"{loaded['projection']}","timemode":f"{loaded['timemode']}","convmode":f"{loaded['convmode']}","LDS":f"{loaded['LDS']}"}
    data = {"amgp_ver":version,"type":"plt","settings":saveState}
    
    if os.path.isfile(f"{dr}/plot/{name}.json"):
        os.remove(f"{dr}/plot/{name}.json")
    
    with open(f"{dr}/plot/{name}.json", "a") as J:
        json.dump(data, J)

# Load a preset from the config file
def presetLoad(loadedPreset):
    global loaded
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    with open(f"{dr}/plot/{loadedPreset}.json", "r") as J:
        lo = json.load(J)
        loaded = lo["settings"]
    
def setInit():
    global Set
    Set = {'date':'recent','delta':0,'jump':3,'levels':'surface','dloop':0,'fcloop':0}
    
# Dump the loaded preset's contents
def singleLoads():
    print(f"(AMGP_PLT) <loaded> Level: {loaded['level']}")
    print(f"(AMGP_PLT) <loaded> Date: {loaded['date']}")
    print(f"(AMGP_PLT) <loaded> Delta: {loaded['delta']}")
    print(f"(AMGP_PLT) <loaded> Factors: {loaded['factors']}")
    print(f"(AMGP_PLT) <loaded> Area: {loaded['area']}")
    print(f"(AMGP_PLT) <loaded> DPI: {loaded['dpi']}")
    print(f"(AMGP_PLT) <loaded> Scale: {loaded['scale']}")
    print(f"(AMGP_PLT) <loaded> PRF (Point Reduction Scale): {loaded['prfactor']}")
    print(f"(AMGP_PLT) <loaded> BF (Barb Factor): {loaded['barbfactor']}")
    print(f"(AMGP_PLT) <loaded> Smooth: {loaded['smoothing']}")
    print(f"(AMGP_PLT) <loaded> Projection: {loaded['projection']}")
    print(f"(AMGP_PLT) <loaded> TM (Time Mode): {loaded['timemode']}")
    print(f"(AMGP_PLT) <loaded> CM (Convective Mode): {loaded['convmode']}")
    print(f"(AMGP_PLT) <loaded> LDS (Local Datasets): {loaded['LDS']}")
                
def PullFactors(values, amgpmodules):
    
    factorList = values['factors'].split(', ')
    
    plotType = []
    fillType = []
    
    for factor in factorList:
        for module in amgpmodules.values():
            if factor in module.getFactors().keys():
                plotType.append(module.getFactors()[f'{factor}'][0])
                fillType.append(module.getFactors()[f'{factor}'][1])
                
    if (values['level'] == 'surface') and (0 in plotType):
        plotType.append(1)
    if (values['level'] != 'surface') and (0 in plotType):
        plotType.append(2)
    
    congPlotType = [*set(plotType)]
    congFillType = [*set(fillType)]
    
    return [congPlotType, congFillType]

def RetrievePlots(values, Time, amgpmodules, reformLD):
    
    factors = values['factors'].split(', ')
    
    congPlotType = PullFactors(values, amgpmodules)[0]
    
    plotslist = []
    
    for module in amgpmodules.values():
        var = f"{module}".strip("amgp")
        globals()[f"{var}"] = []
        
        for factor in factors:
            if factor in module.getFactors().keys():
                globals()[f"{var}"].append(factor)
        
        if len(globals()[f"{var}"]) > 0:
            plotslist.extend(module.Retrieve(Time, globals()[f"{var}"], values, reformLD))
    
    return plotslist
    
    
# The meat of the program
def run(values, extras):

    amgpmodules = extras["amgpmodules"]
    S = extras["S"]
    noShow = extras["noShow"]
    proj = extras["proj"]
    direct = extras["direct"]
    altDir = extras["altDir"]
    altDirCon = extras["altDirCon"]
    title = extras["title"]
    
    currentTime = amgp.setTime()

    '''
    rewind = 0
    # Handle quickrun overrides
    for k in Override:
        if k == "date":
            values.update({'date':Override[k]})
        if k == "fcHour":
            values.update({'delta':Override[k]})
        if k == "level":
            values.update({'level':Override[k]})
        if k == 'factors':
            values.update({'factors':Override[k]})
        if k == "adtnlRwnd":
            rewind = Override[k]
    
    values.update({'delta':int(values['delta'])})'''
    
    # Level
    level = amgp.GetLevel(values['level']).level
    values['level'] = level
        
    # Date
    Time = amgp.ParseTime(values['date'], PullFactors(values, amgpmodules)[0], currentTime, values['timemode'], values['convmode'])

    #Setting up local data
    avLD = amgp.LocalData()
    reformLD = {}
    for num in values['LDS'].split(", "):
        if int(num) != 0:
            reformLD[avLD[int(num)][0]] = avLD[int(num)][1]

    if reformLD == {}:
        reformLD = None
    
    # Data
    plotslist = RetrievePlots(values, Time, amgpmodules, reformLD)

    if direct:
        amgpmap.SaveMap(amgpmap.Panel(Time, plotslist, values, area_dictionary, amgpmodules, title, version), S, noShow, proj, altDir, altDirCon)
    else:
        return Time, plotslist, values


# --- End Definitions ---