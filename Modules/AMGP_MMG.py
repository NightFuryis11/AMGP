################################################
#                                              #
#       Automated Map Generation Program       #
#           Multi-Mode .gif Module             #
#            Author: Sam Bailey                #
#        Last Revised: Aug 13, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
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
import time

from tkinter import *
from tkinter import ttk

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=UserWarning)

#----------------- AMGP IMPORTS -------------------#

from Modules import AMGP_MAP as amgpmap
from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_MMG",
            'uid':"00420300"}

def init(pack):
    print("<menu_init> Opened the Multi-Mode Gif interface <menu_init>")
    global unpack
    unpack = pack
    global mname
    mname = info()["name"]
    amgp.getTime()
    imports(unpack)
    obsLoad('default')
    mmgLoad('default')
    loadings()
    multiMode()

def partialInit(pack):
    global unpack
    unpack = pack
    imports(unpack)

def imports(unpack):
    for module in unpack['datamods'].values():
        import_module(module.__name__)

def multiMode():
    global loadedObs
    global loadedMMG
    print("(AMGP_MMG) <menu> Input commands, or type 'help'.")
    comm = input("(AMGP_MMG) <input> ")
    
    command = comm.split(" ")
    
    '''if command[0] == "help":'''
    
    if command[0] == "list":
        print("(AMGP_MMG) <list> Type 'time' to set and print the current time.")
        print("(AMGP_MMG) <list> Type 'preset list' to list all available presets.")
        print("(AMGP_MMG) <list> Type 'preset obs {name}' to load a preset from the plotting module.")
        print("(AMGP_MMG) <list> Type 'preset mmg {name}' to load an MMG preset.")
        print("(AMGP_MMG) <list> Type 'edit {parameter} {value}' to change the value of any parameter.")
        print("(AMGP_MMG) <list> Type 'save obs {name}' to save the individual map settings as a plotting module preset.")
        print("(AMGP_MMG) <list> Type 'save mmg {name}' to save the recursion settings as an MMG preset.")
        print("(AMGP_MMG) <list> Type 'run' to run with the current settings.")
        print("(AMGP_MMG) <list> Type 'switch {module}' to change to a different menu module.")
        print("(AMGP_MMG) <list> Type 'quit' to exit without running.")
    
    if command[0] == 'time':
        amgp.getTime()
        multiMode()
    elif command[0] == 'preset':
        if command[1] == 'list':
            plotkeys = []
            multikeys = []
            for item in unpack['presets']:
                spi = item[0].split("-")
                if spi[0] == "plot":
                    plotkeys.append(spi[1])
                if spi[0] == "mmg":
                    plotkeys.append(spi[1])
            print("(AMGP_MMG) <presets> Below is the list of all currently loaded presets:")
            for item in plotkeys:
                print(f"(AMGP_MMG) <presets> (obs) {item}")
            for item in multikeys:
                print(f"(AMGP_MMG) <presets> (mmg) {item}")
            multiMode()
        elif command[1] == 'obs':
            try:
                obsLoad(command[2])
                loadings()
            except:
                print("(AMGP_MMG) <error> That is not a valid obs preset name!")
            multiMode()
        elif command[1] == 'mmg':
            try:
                mmgLoad(command[2])
                loadings()
            except:
                print("(AMGP_MMG) <error> That is not a valid mmg preset name!")
            multiMode()
        else:
            print("(AMGP_MMG) <error> That is not a valid command!")
            multiMode()
    elif command[0] == 'edit':
        if command[1] in ["Level", "Date", "Delta", "Factors", "Area", "DPI", "Scale", "PRF", "BF", "Smooth", "Projection", "TM", "CM", "LDS", "EndDate", "DeltaLoop", "TimeStep"]:
            if command[1] == "Level":
                loadedObs.update({'level':command[2]})
            if command[1] == "Date":
                if command[2] == 'recent':
                    loadedObs.update({'date':command[2]})
                elif command[2] == "today":
                    loadedObs.update({'date':f'{command[2]}, {command[3]}'})
                else:
                    try:
                        loadedObs.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}, {command[6]}'})
                    except:
                        loadedObs.update({'date':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            if command[1] == "Delta":
                loadedObs.update({'delta':command[2]})
            if command[1] == "Factors":
                blankFactors = []
                count = 0
                if command[2] == "add":
                    blankFactors = loadedObs['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            blankFactors.append(command[count])
                        count += 1
                elif command[2] == "remove":
                    blankFactors = loadedObs['factors'].split(', ')
                    for item in command:
                        if count > 2:
                            if command[count] in blankFactors:
                                blankFactors.pop(blankFactors.index(command[count]))
                            else:
                                print("(AMGP_MMG) <error> That is not a valid factor to remove!")
                                multiMode()
                        count += 1
                else:
                    for item in command:
                        if count > 1:
                            blankFactors.append(command[count])
                        count += 1
                fullFactors = ', '.join(blankFactors)
                loadedObs.update({'factors':fullFactors})
            if command[1] == "Area":
                loadedObs.update({'area':command[2]})
            if command[1] == "DPI":
                loadedObs.update({'dpi':command[2]})
            if command[1] == "Scale":
                loadedObs.update({'scale':command[2]})
            if command[1] == "PRF":
                loadedObs.update({'prfactor':command[2]})
            if command[1] == 'BF':
                loadedObs.update({'barbfactor':command[2]})
            if command[1] == "Smooth":
                loadedObs.update({'smoothing':command[2]})
            if command[1] == "Projection":
                loadedObs.update({'projection':command[2]})
            if command[1] == "TM":
                if command[2] not in ["raw","sync","async","near"]:
                    print("(AMGP_MMG) <error> That is not a valid value for the Time Mode!")
                    multiMode()
                loadedObs.update({'timemode':command[2]})
            if command[1] == "CM":
                if command[2] not in ["recent","latest"]:
                    print("(AMGP_MMG) <error> That is not a valid value for the Convective Mode!")
                    multiMode()
                loadedObs.update({'convmode':command[2]})
            if command[1] == "LDS":
                count = 0
                partialLDS = []
                for item in command:
                    if count > 1:
                        partialLDS.append(command[count])
                    count += 1
                fullLDS = ", ".join(partialLDS)
                loadedObs.update({'LDS':fullLDS})
            if command[1] == "EndDate":
                if command[2] == 'recent':
                    loadedMMG.update({'end':command[2]})
                elif command[2] == "today":
                    loadedMMG.update({'end':f'{command[2]}, {command[3]}'})
                else:
                    try:
                        loadedMMG.update({'end':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}, {command[6]}'})
                    except:
                        loadedMMG.update({'end':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            if command[1] == "DeltaLoop":
                loadedMMG.update({'dl':command[2]})
            if command[1] == "TimeStep":
                try:
                    loadedMMG.update({'ts':f'{command[2]}, {command[3]}, {command[4]}'})
                except:
                    loadedMMG.update({'ts':f'{command[2]}, {command[3]}, {command[4]}, {command[5]}'})
            if command[1] == "DeltaMax":
                loadedMMG.update({'dm':command[2]})
            loadings()
            multiMode()
        else:
            print("(AMGP_MMG) <error> That is not a valid parameter to edit!")
            multiMode()
    elif command[0] == 'run':
        try:
            dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Batches")
            with open(f"{dr}/{command[1]}.txt", "r") as setIn:
                for line in setIn:
                    batch = json.load(line)
                    alt = input("(AMGP_MMG) <run> Would you like to save this Batch in a separate location [(y)/n]: ")
                    if alt == 'n':
                        proj = input("(AMGP_MMG) <run> Would you like to save these maps to a project directory? If so, type the name: ")
                        altDir = False
                    else:
                        proj = input("(AMGP_MMG) <run> Give the full path you would like to save these maps to: ")
                        altDir = True
                    title = input("(AMGP_MMG) <run> Would you like to use a simplified title? [y/(n)] ")
                    saveSet("mmg", "prev")
                    saveSet("obs", "prev")
                    print("(AMGP_MMG) <run> Saved previous settings!")
                    for bunch in batch.values():
                        bunchRunO = bunch["OBS"]
                        bunchRunM = bunch["MMG"]
                        bunchRun = {"OBS": bunchRunO, "MMG": bunchRunM}
                        run(bunchRun, proj, title, altDir)
        except:
            proj = input("(AMGP_MMG) <run> Would you like to save these maps to a project directory? If so, type the name: ")
            title = input("(AMGP_MMG) <run> Would you like to use a simplified title? [y/(n)] ")
            saveSet("mmg", "prev")
            saveSet("obs", "prev")
            print("(AMGP_MMG) <run> Saved previous settings!")
            print(loadedObs, loadedMMG)
            totdat = {"OBS": loadedObs, "MMG": loadedMMG}
            run(totdat, {"proj": proj, "title": title, "altDir": False, "altDirCon": False})
        loadings()
        multiMode()
    elif command[0] == 'save':
        saveSet(command[1], command[2])
        multiMode()
    elif command[0] == 'switch':
        try:
            y = command[1]
        except:
            print("(AMGP_MMG) <error> Please enter a module name to switch to.")
            multiMode()
        if (f'AMGP_{command[1].upper()}' in unpack['modulenames'].values()) or (f'AMGP_{command[1].upper()}' in unpack['modulenames'].values()):
            for k, v in unpack['modulenames'].items():
                if ((k in unpack['menumods'].keys()) or (v in unpack['combomods'].keys())) and (f'AMGP_{command[1].upper()}' == v):
                    try:
                        newMod = unpack['menumods'][k]
                    except:
                        newMod = unpack['combomods'][k]
                    newMod.init(unpack)
                    break
        print("(AMGP_MMG) <error> That is not a valid module to switch to!")
        multiMode()
    elif command[0] == 'quit':
        sys.exit("(AMGP_MMG) <quit> Process terminated")
        

def obsLoad(preset):
    global loadedObs
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    with open(f"{dr}/plot/{preset}.json", "r") as J:
        lo = json.load(J)
        loadedObs = lo["settings"]

def mmgLoad(preset):
    global loadedMMG
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    with open(f"{dr}/mmg/{preset}.json", "r") as J:
        lo = json.load(J)
        loadedMMG = lo["settings"]

def loadings():
    print(f"(AMGP_MMG) <loaded> Level: {loadedObs['level']}")
    print(f"(AMGP_MMG) <loaded> Date: {loadedObs['date']}")
    print(f"(AMGP_MMG) <loaded> Delta: {loadedObs['delta']}")
    print(f"(AMGP_MMG) <loaded> Factors: {loadedObs['factors']}")
    print(f"(AMGP_MMG) <loaded> Area: {loadedObs['area']}")
    print(f"(AMGP_MMG) <loaded> DPI: {loadedObs['dpi']}")
    print(f"(AMGP_MMG) <loaded> Scale: {loadedObs['scale']}")
    print(f"(AMGP_MMG) <loaded> PRF (Point Reduction Scale): {loadedObs['prfactor']}")
    print(f"(AMGP_MMG) <loaded> BF (Barb Factor): {loadedObs['barbfactor']}")
    print(f"(AMGP_MMG) <loaded> Smooth: {loadedObs['smoothing']}")
    print(f"(AMGP_MMG) <loaded> Projection: {loadedObs['projection']}")
    print(f"(AMGP_MMG) <loaded> TM (Time Mode): {loadedObs['timemode']}")
    print(f"(AMGP_MMG) <loaded> CM (Convective Mode): {loadedObs['convmode']}")
    print(f"(AMGP_MMG) <loaded> LDS (Local Datasets): {loadedObs['LDS']}")
    print(f"(AMGP_MMG) <loaded> EndDate: {loadedMMG['end']}")
    print(f"(AMGP_MMG) <loaded> DeltaLoop: {loadedMMG['dl']}")
    print(f"(AMGP_MMG) <loaded> TimeStep: {loadedMMG['ts']}")
    print(f"(AMGP_MMG) <loaded> DeltaMax: {loadedMMG['dm']}")
    
def saveSet(cat, name):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    if cat == "plt":
        saveState = {"level":f"{loadedObs['level']}","date":f"{loadedObs['date']}","delta":f"{loadedObs['delta']}","factors":f"{loadedObs['factors']}","area":f"{loadedObs['area']}","dpi":f"{loadedObs['dpi']}","scale":f"{loadedObs['scale']}","prfactor":f"{loadedObs['prfactor']}","barbfactor":f"{loadedObs['barbfactor']}","smoothing":f"{loadedObs['smoothing']}","projection":f"{loadedObs['projection']}","timemode":f"{loadedObs['timemode']}","convmode":f"{loadedObs['convmode']}","LDS":f"{loadedObs['LDS']}"}
        data = {"amgp_ver":unpack['ver'],"type":"plt","settings":saveState}

        if os.path.isfile(f"{dr}/plot/{name}.json"):
            os.remove(f"{dr}/plot/{name}.json")

        with open(f"{dr}/plot/{name}.json", "a") as J:
            json.dump(data, J)
        
        print(f"(AMGP_MMG) <save> Loaded obs settings saved to Presets/plot as preset: {name}.json")
    
    if cat == "mmg":
        saveState = {"end":f"{loadedMMG['end']}","dl":f"{loadedMMG['dl']}","ts":f"{loadedMMG['ts']}","dm":f"{loadedMMG['dm']}"}
        data = {"amgp_ver":unpack['ver'],"type":"mmg","settings":saveState}

        if os.path.isfile(f"{dr}/mmg/{name}.json"):
            os.remove(f"{dr}/mmg/{name}.json")

        with open(f"{dr}/mmg/{name}.json", "a") as J:
            json.dump(data, J)
            
        print(f"(AMGP_MMG) <save> Loaded mmg settings saved to Presets/mmg as preset: {name}.json")

def stepCounter(ts):
    splits = ts.split(", ")
    return timedelta(days=int(splits[0]),hours=int(splits[1]),minutes=int(splits[2]))
    

def run(totdat, extras):
    obs = totdat["OBS"]
    mmg = totdat["MMG"]
    proj = extras["proj"]
    title = extras["title"]
    altDir = extras["altDir"]
    altDirCon = extras["altDirCon"]

    startDate = amgp.ParseTime(obs['date']).time
    endDate = amgp.ParseTime(mmg['end']).time
    while startDate <= endDate:
        obs['date'] = f"{startDate.year}, {startDate.month}, {startDate.day}, {startDate.hour}, {startDate.minute}"
        delta = 0
        while delta <= int(mmg['dm']):
            modObs = obs
            modObs['delta'] = delta
            Time, plotslist, values = amgpplt.run(modObs, {"amgpmodules": unpack['datamods'], "S": True, "noShow": True, "proj": proj, "direct": False, "title": title, "altDir": altDir, "altDirCon": altDirCon})
            if title == "y":
                amgpmap.SaveMap(amgpmap.Panel(Time, plotslist, values, unpack['customareas'], unpack['datamods'], f'{modObs["date"]} - {delta} hour forecast', unpack['ver']), True, True, proj, altDir, altDirCon)
            else:
                amgpmap.SaveMap(amgpmap.Panel(Time, plotslist, values, unpack['customareas'], unpack['datamods'], '', unpack['ver']), True, True, proj, altDir, altDirCon)
            if "cancel" not in plotslist:
                print(f"(AMGP_MMG) <run> Made a map for {startDate.year}, {startDate.month}, {startDate.day}, {startDate.hour}, {startDate.minute} + {delta}")
            if int(mmg['dl']) != 0:
                delta = delta + int(mmg['dl'])
            else:
                delta = delta + 1
        startDate = startDate + stepCounter(mmg['ts'])