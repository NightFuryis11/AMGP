################################################
#                                              #
#       Automated Map Generation Program       #
#           Map Generation Module              #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.4.0                 #
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

from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_MAP",
            'uid':"00300200"}
    
# The meat of the program
def Panel(Time, plotslist, values, area_dictionary, amgpmodules, titleOverride, version):

    #exit clause
    if "cancel" in plotslist:
        return {'panelSize':(0, 0),'panel':None,'timeObj':Time,'values':None, 'titlebits':None,'filltype':[0],'ver':version, 'valid':False}
    
    # Panel Preparation
    panel = declarative.MapPanel()
    panel.layout = (1, 1, 1)
    level = values['level']
    
    # Parse custom zoom feature
    simArea = values['area'].replace("+", "")
    simArea = simArea.replace("-", "")
    if simArea in area_dictionary:
        splitArea = Counter(values['area'])
        factor = (splitArea['+']) - (splitArea['-'])
        scaleFactor = (1 - 2**-factor)/2
        west, east, south, north = area_dictionary[f'{simArea}']
        newWest = west - (west - east) * scaleFactor
        newEast = east + (west - east) * scaleFactor
        newSouth = south - (south - north) * scaleFactor
        newNorth = north + (south - north) * scaleFactor
        modArea = newWest, newEast, newSouth, newNorth
    
        panel.area = modArea
    else:
        try:
            panel.area = f'{values["area"]}'
        except:
            print("(AMGP_MAP) <error> The panel area you have put in does not exist!")
            amgpplt.inputChain()

    # Figuring out the data display area
    areaZero = list(panel.area)
    areaScaleA = 1.1
    areaScaleB = 0.9
    if areaZero[0] < 0:
        areaZero[0] = 360 + (areaZero[0] * areaScaleA)
    if areaZero[1] < 0:
        areaZero[1] = 360 + (areaZero[1] * areaScaleB)
    areaZero[2] = areaZero[2] * areaScaleB
    areaZero[3] = areaZero[3] * areaScaleA
    latSlice = slice(areaZero[3], areaZero[2])
    lonSlice = slice(areaZero[0], areaZero[1])
    
    panel.layers = ['states', 'coastline', 'borders']
    
    # Parsing the panel.area into a list, and doing math on it.
    areaList = list(panel.area)
    areaMap = map(int, areaList)
    mapList = list(areaMap)
    diffLat = int(mapList[1])-int(mapList[0])
    diffLon = int(mapList[3])-int(mapList[2])
    avgDiff = ((diffLat + diffLon)//2)
    scaledDiff = math.floor(avgDiff*float(values['scale']))

    # Determining projection
    midLon = (mapList[1]+mapList[0])//2
    midLat = (mapList[3]+mapList[2])//2
    if values['projection'] == '' or values['projection'] == 'custom':
        projection = ccrs.LambertConformal(central_longitude = midLon, central_latitude = midLat)
    elif values['projection'] == 'satelite':
        projection = None
    else:
        projection = values['projection']
    panel.projection = projection
    
    # Data acquisition and packaging
    panel.plots = plotslist
    
    plotTypes = amgpplt.PullFactors(values, amgpmodules)[0]
    fillTypes = amgpplt.PullFactors(values, amgpmodules)[1]
    
    # Automatic panel titles
    if titleOverride != '':
        title = titleOverride
        titlebits = str(title)
    else:
        titlebits = []
        
        if (0 in plotTypes) and (1 not in plotTypes) and (2 not in plotTypes):
            titlebits.append("Obs")
        if (1 in plotTypes) and (2 not in plotTypes):
            titlebits.append("Surface Obs")
        if (1 not in plotTypes) and (2 in plotTypes):
            titlebits.append(f"{level}mb Obs")
            
        if ((3 in plotTypes) or (6 in plotTypes)) and (4 not in plotTypes) and ((5 not in plotTypes) and (7 not in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Model")
        if (4 in plotTypes) and ((5 not in plotTypes) and (7 not in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Surface Model")
        if (4 not in plotTypes) and ((5 in plotTypes) or (7 in plotTypes)):
            titlebits.append(f"{values['delta']} Hour Upper-air Model")
        
        if 8 in plotTypes:
            titlebits.append("Sat")
        
        if 9 in plotTypes:
            titlebits.append("Day 1 Outlook")
        if 10 in plotTypes:
            titlebits.append("Day 2 Outlook")
        if 11 in plotTypes:
            titlebits.append("Day 3 Outlook")
        if 12 in plotTypes:
            if "day4prob" in values['factors']:
                titlebits.append("Day 4 Probability")
            if "day5prob" in values['factors']:
                titlebits.append("Day 5 Probability")
            if "day6prob" in values['factors']:
                titlebits.append("Day 6 Probability")
            if "day7prob" in values['factors']:
                titlebits.append("Day 7 Probability")
            if "day8prob" in values['factors']:
                titlebits.append("Day 8 Probability")
        
        if 13 in plotTypes:
            titlebits.append("Warnings")
        if 14 in plotTypes:
            titlebits.append("Watches")
        if 15 in plotTypes:
            titlebits.append("Storm Reports")

        #if 17 in plotTypes:
        #    titlebits.append("Rain/Snow by Site")
        if 18 in plotTypes:
            titlebits.append("SnowPerMeter")
        if 19 in plotTypes:
            titlebits.append("SnowPerMeter^2")
        
        if Time.category == 'raw':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Raw for Time"
        if Time.category == 'sync':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Synced"
        if (Time.category == 'async-1') or (Time.category == 'async-3') or (Time.category == 'async-6') or (Time.category == 'async-12') or (Time.category == 'async-24'):
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Asyncronous"
        if Time.category == 'near':
            title = f"{Time.tsalp} - {', '.join(titlebits)} - Nearest per Item"
    
    panel.left_title = f"AMGP v{version}"
    panel.title = f"{values['area']} - {title}"
    if level == 'surface':
        panel.right_title = "Surface"
    else:
        panel.right_title = f"{level}mb"
    
    panel.title_fontsize = (scaledDiff**0.75) * 1.5
                            
    return {'panelSize':(scaledDiff, scaledDiff),'panel':panel,'timeObj':Time,'values':values, 'titlebits':titlebits,'filltype':fillTypes,'ver':version, 'valid':True}
    
def SaveMap(product, doSave, noShow, proj='', altDir=False, altDirCon=False):

    if doSave == "FALSE":
        doSave = False
    elif doSave == "TRUE":
        doSave = True
    if noShow == "FALSE":
        noShow = False
    elif noShow == "TRUE":
        noShow = True
    if altDir == "FALSE":
        altDir = False
    elif altDir == "TRUE":
        altDir = True
    if altDirCon == "FALSE":
        altDirCon = False
    elif altDirCon == "TRUE":
        altDirCon = True

    yearstamp = product['timeObj'].ys
    monthstamp = product['timeObj'].ms
    daystamp = product['timeObj'].ds
    timestampNum = product['timeObj'].tsnum
    timestampAlp = product['timeObj'].tsalp
    cat = product['timeObj'].category
    currentTime = product['timeObj'].now
    fill = 0
    version = product['ver']
    if 1 in product['filltype']:
        fill = 1
    
    nowstamp = amgp.ParseTime("recent", [-1], currentTime, "raw", "latest").tsfull

    if product['valid'] == True:
        pc = declarative.PanelContainer()
        pc.size = product['panelSize']
        pc.panels = [product['panel']]
        
        # Saving the map
        if (proj == '') and (altDir==False):
            dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
            OldDirY = os.path.isdir(f'{dr}/{yearstamp}')
            OldDirM = os.path.isdir(f'{dr}/{yearstamp}/{monthstamp}')
            OldDirD = os.path.isdir(f'{dr}/{yearstamp}/{monthstamp}/{daystamp}')
            
            if doSave:
                if type(product['titlebits']) == str:
                    inst = product['titlebits']
                elif type(product['titlebits']) == list:
                    inst = ', '.join(product['titlebits'])
    
                if OldDirY == False:
                    os.mkdir(f'{dr}/{yearstamp}')
                if OldDirM == False:
                    os.mkdir(f'{dr}/{yearstamp}/{monthstamp}')
                if OldDirD == False:
                    os.mkdir(f'{dr}/{yearstamp}/{monthstamp}/{daystamp}')
                pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
                save = PImage.open(f"{dr}/Temp/Temp.png").convert('RGBA')
                save = amgp.Watermark(save, version, fill)
                save.save(f"{dr}/{yearstamp}/{monthstamp}/{daystamp}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
                if noShow == False:
                    save.show()
                print("(AMGP_MAP) <run> Map successfully saved!")
            else:
                if os.path.isdir(f"{dr}/Temp") == False:
                    os.mkdir(f"{dr}/Temp")
                pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
                save = PImage.open(f'{dr}/Temp/Temp.png').convert('RGBA')
                save = amgp.Watermark(save, version, fill)
                save.show()
            amgp.ClearTemp()
        elif (altDir==False):
            dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
            OldDir = os.path.isdir(f'{dr}/Projects/{proj}')
            
            if type(product['titlebits']) == str:
                inst = product['titlebits']
            elif type(product['titlebits']) == list:
                inst = ', '.join(product['titlebits'])
    
            if OldDir == False:
                os.mkdir(f'{dr}/Projects/{proj}')
            pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
            save = PImage.open(f"{dr}/Temp/Temp.png").convert('RGBA')
            save = amgp.Watermark(save, version, fill)
            save.save(f"{dr}/Projects/{proj}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
            amgp.ClearTemp()
        else:
            if altDirCon:
                if type(product['titlebits']) == str:
                    inst = product['titlebits']
                elif type(product['titlebits']) == list:
                    inst = ', '.join(product['titlebits'])
                dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
                pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
                save = PImage.open(f"{dr}/Temp/Temp.png").convert('RGBA')
                save = amgp.Watermark(save, version, fill)
    
                OldDirY = os.path.isdir(f'{proj}/{yearstamp}')
                OldDirM = os.path.isdir(f'{proj}/{yearstamp}/{monthstamp}')
                OldDirD = os.path.isdir(f'{proj}/{yearstamp}/{monthstamp}/{daystamp}')

                if OldDirY == False:
                    os.mkdir(f'{proj}/{yearstamp}')
                if OldDirM == False:
                    os.mkdir(f'{proj}/{yearstamp}/{monthstamp}')
                if OldDirD == False:
                    os.mkdir(f'{proj}/{yearstamp}/{monthstamp}/{daystamp}')
                
                save.save(f"{proj}/{yearstamp}/{monthstamp}/{daystamp}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
                amgp.ClearTemp()
            else:
                if type(product['titlebits']) == str:
                    inst = product['titlebits']
                elif type(product['titlebits']) == list:
                    inst = ', '.join(product['titlebits'])
                dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
                pc.save(f"{dr}/Temp/Temp.png", dpi=int(product['values']['dpi']), bbox_inches='tight')
                save = PImage.open(f"{dr}/Temp/Temp.png").convert('RGBA')
                save = amgp.Watermark(save, version, fill)
                save.save(f"{proj}/{timestampNum}; {product['values']['area']}; {inst} - {cat}; {nowstamp}.png")
                amgp.ClearTemp()
        
    else:
        amgp.ThrowError("AMGP_MAP", 2, f"Map for {product['timeObj'].ds} cancelled.", True, False, False)


# --- End Definitions ---