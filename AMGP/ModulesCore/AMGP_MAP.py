###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #
#                  Created on Mar 09, 2022                    #
#                                                             #
#                  Core Module: AMGP_MAP.py                   #
#                     Author: Sam Bailey                      #
#                 Last Revised: Feb 14, 2025                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################
"""
AMGP_MAP

The core of the map production processes of AMGP.
"""

from cartopy import crs as ccrs
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
import numpy as np
from metpy.plots import plot_areas
from collections import Counter
import os
from datetime import datetime, timezone
from PIL import Image
import uuid

#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_UTIL as amgp
from ModulesCore import AMGP_MENU as amgpmenu
#-----------------  Definitions -------------------#

def Info():
    return {
        "name": "AMGP_MAP",
        "uid": "00300200"
    }

def Run(packed_data : dict, plotables : list, map_settings : dict, proj_settings : dict, style_info : dict, save_loc : str, return_image : bool = False, overrides : dict = {}):
    '''
    The primary engine of AMGP's figure production.

    Parameters
    ----------
    packed_data : dict
        Data passed on from AMGP.py, including the imported modules, AMGP version, and program runtime.
    
    plotables : list
        A list of dicts, each pertaining to a singular plotable factor.
    
    map_settings : dict
        The basic parameters around which a map should be built.
    
    proj_settings : dict
        The details for each map projection.
    
    style_info : dict
        Skeleton parameters for the matplotlib figure style.
    
    return_image : bool, optional, defaults to False
        Whether or not the function should provide the path to the last image created as a return.
    
    overrides : dict, optional, defaults to {}
        Any additional parameters, typically only used by internal functions.
    '''

    #print(plotables)
    #print(map_settings)
    #print(proj_settings)
    version = packed_data["version"]
    data_modules = packed_data["data_modules"]
    runtime = packed_data["runtime"]

    times = []
    for axis in range(0, int(packed_data["styles"][f"{style_info['name']}"].StyleInfo()["axes"])):
        mode = map_settings[axis]["time mode"]['selection'][0]
        timestring = map_settings[axis]["time"]['selection']
        times.append(amgp.Time(runtime, mode, timestring = timestring).AddFormatting(plotables[axis]))
    
    max_times = np.max(np.array([len(x.timelist) for x in times]))
    
    #for k, v in overrides.items():
        #if k == "temp":
            #fig_temp = v

    # print(timestring)
    # times = amgp.Time(runtime, mode, timestring = timestring).AddFormatting(plotables)
    # print(times.timelist)
    # print(times.FormatTimes("20m").timelist)

    #print(data_modules)

    Style = packed_data["styles"][f"{style_info['name']}"]
    projs = []
    for axis_num in range(0, Style.StyleInfo()["axes"]):
        projs.append(amgp.ParseProjection(proj_settings[axis_num]))

    figname = ""
    for figure_num in range(1, max_times + 1):
        fig_fill = False

        StyleFig = Style.StyleTemplate().Prepare(projs)

        fig_hasdate = False

        for axis_num in range(0, StyleFig.axes):
            
            if proj_settings[axis_num]['area']["selection"] != "":
                areaName = proj_settings[axis_num]['area']["selection"].lower()
                strpArea = areaName.replace("+", "")
                strpArea = strpArea.replace("-", "")
                area = amgp.CustomAreas(areaName)
                if area == None:
                    for narea in plot_areas.named_areas:
                        if narea == strpArea:
                            area = plot_areas.named_areas[f"{narea}"].bounds
                splitArea = Counter(areaName)
                factor = (splitArea['+']) - (splitArea['-'])
                scaleFactor = (1 - 2**-factor)/2
                west, east, south, north = area
                newWest = west - (west - east) * scaleFactor
                newEast = east + (west - east) * scaleFactor
                newSouth = south - (south - north) * scaleFactor
                newNorth = north + (south - north) * scaleFactor
                extent = newWest, newEast, newSouth, newNorth

                StyleFig.axis[axis_num].set_extent(extent, crs=ccrs.PlateCarree())

            if projs[axis_num] != None:
                for layer in map_settings[axis_num]['layers']["selection"]:
                    if layer == "states":
                        StyleFig.axis[axis_num].add_feature(cfeat.STATES)
                    if layer == "coastlines":
                        StyleFig.axis[axis_num].add_feature(cfeat.COASTLINE)
                    if layer == "lakes":
                        StyleFig.axis[axis_num].add_feature(cfeat.LAKES)
                    if layer == "oceans":
                        StyleFig.axis[axis_num].add_feature(cfeat.OCEAN)
                    if layer == "country borders":
                        StyleFig.axis[axis_num].add_feature(cfeat.BORDERS)
                    if layer == "rivers":
                        StyleFig.axis[axis_num].add_feature(cfeat.RIVERS)

            for plotable in plotables[axis_num]:
                if plotable["is_fill"]:
                    fig_fill = True
                flag = True
                for _, module in data_modules.items():
                    if (plotable["source_module"] == module.Info()["uid"]) and (plotable["name"] in module.Factors().keys()):
                        StyleFig.axis[axis_num] = module.Plot(StyleFig.axis[axis_num], plotable, map_settings[axis_num], proj_settings[axis_num], amgp.Time(runtime, map_settings[axis_num]["time mode"]['selection'][0], timestring = map_settings[axis_num]["time"]['selection']).AddFormatting(plotables[axis_num]).Index(figure_num - 1))
                        flag = False
                    elif (plotable["source_module"] == module.Info()["uid"]) and (plotable["name"] not in module.Factors().keys()):
                        amgp.ThrowError(f"{module.Info()['name']}", "Plot()", 1, f"The plotable {plotable['name']} was requested, but not found within the identified module {module.Info()['name']}. This shouldn't be able to happen, please investigate further and submit a report.", runtime, True)
                if flag:
                    amgp.ThrowError("AMGP_MAP", "Run()", 0, f"The requested module for plotable {plotable['name']} could not be found.", runtime, True, True, True)
            
            left_title = f"AMGP v{version}"
            if map_settings[axis_num]["append date to title"]["selection"][0] == "Yes":
                center_title = f"{amgp.Time(runtime, map_settings[axis_num]['time mode']['selection'][0], timestring = map_settings[axis_num]['time']['selection']).AddFormatting(plotables[axis_num]).FormatTimes(plotables[axis_num][0]['time_format']).Index(figure_num - 1).timelist[0].strftime('%Y%m%d %H%MZ')} - {map_settings[axis_num]['figure title']['selection']}"
                fig_hasdate = True
            else:
                center_title = f"{map_settings[axis_num]['figure title']['selection']}"
            right_title = f"{map_settings[axis_num]['username']['selection']}"

            StyleFig.axis[axis_num].set_title(left_title, loc = "left")
            StyleFig.axis[axis_num].set_title(center_title, loc = "center")
            StyleFig.axis[axis_num].set_title(right_title, loc = "right")

        # Save and destroy the figure
        production_time = datetime.now(timezone.utc)
        figname = f"{center_title} - Runtime {production_time.strftime('%Y%m%d %H%M%SZ')}.png"

        plot_time = amgp.Time(runtime, map_settings[axis_num]['time mode']['selection'][0], timestring = map_settings[axis_num]['time']['selection']).AddFormatting(plotables[axis_num]).Index(figure_num - 1).timelist[0]

        dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Maps")
        if save_loc == "":
            if fig_hasdate:
                OldDirY = os.path.isdir(f'{dr}{amgp.PathSep()}{plot_time.year}')
                OldDirM = os.path.isdir(f'{dr}{amgp.PathSep()}{plot_time.year}{amgp.PathSep()}{plot_time.month}')
                OldDirD = os.path.isdir(f'{dr}{amgp.PathSep()}{plot_time.year}{amgp.PathSep()}{plot_time.month}{amgp.PathSep()}{plot_time.day}')

                if not OldDirY:
                    os.mkdir(f'{dr}{amgp.PathSep()}{plot_time.year}')
                if not OldDirM:
                    os.mkdir(f'{dr}{amgp.PathSep()}{plot_time.year}{amgp.PathSep()}{plot_time.month}')
                if not OldDirD:
                    os.mkdir(f'{dr}{amgp.PathSep()}{plot_time.year}{amgp.PathSep()}{plot_time.month}{amgp.PathSep()}{plot_time.day}')

                full_path = f'{dr}{amgp.PathSep()}{plot_time.year}{amgp.PathSep()}{plot_time.month}{amgp.PathSep()}{plot_time.day}{amgp.PathSep()}' + figname
                
                StyleFig.figure.savefig(full_path, dpi = int(map_settings[0]["image dpi"]["selection"][0]), bbox_inches = "tight", format = "PNG")
            else:
                full_path = f"{dr}{amgp.PathSep()}Dateless{amgp.PathSep()}{figname}"
                StyleFig.figure.savefig(full_path, dpi = int(map_settings[0]["image dpi"]["selection"][0]), bbox_inches = "tight", format = "PNG")
        else:
            # Ensure the directories exist that the images are to be saved to
            split_save_loc = save_loc.split("/")
            path_flag = 0
            if not save_loc.endswith("/"):
                path_flag += 1
            for i in range(0, len(split_save_loc) - path_flag):
                ppath = ""
                if save_loc.startswith("/"):
                    ppath += "/"
                for piece in split_save_loc[:i+1]:
                    ppath += f"{piece}{amgp.PathSep()}"
                if save_loc.startswith("."):
                    ppath = ppath.replace(".", dr)
                if not os.path.exists(ppath):
                    os.mkdir(ppath)
            
            if save_loc.startswith("."): # Within the AMGP map directories
                if save_loc.startswith("./Temp/"):
                    full_path = f"{dr}{save_loc.replace('.', '').replace('/', amgp.PathSep())}{uuid.uuid4()}.png"
                else:
                    if save_loc.endswith("/"):
                        full_path = f"{dr}{save_loc.replace('.', '').replace('/', amgp.PathSep()).replace('$Y', plot_time.strftime('%Y')).replace('$m', plot_time.strftime('%m')).replace('$d', plot_time.strftime('%d')).replace('$D', plot_time.strftime('%Y-%m-%d')).replace('$t', plot_time.strftime('%H%M%SZ')).replace('$r', runtime.strftime('%Y-%m-%d_%H%M%SZ')).replace('$i', f'{figure_num - 1}').replace('$n', f'{figure_num}')}{amgp.PathSep()}{figname}"
                    else:
                        full_path = f"{dr}{save_loc.replace('.', '').replace('/', amgp.PathSep()).replace('$Y', plot_time.strftime('%Y')).replace('$m', plot_time.strftime('%m')).replace('$d', plot_time.strftime('%d')).replace('$D', plot_time.strftime('%Y-%m-%d')).replace('$t', plot_time.strftime('%H%M%SZ')).replace('$r', runtime.strftime('%Y-%m-%d_%H%M%SZ')).replace('$i', f'{figure_num - 1}').replace('$n', f'{figure_num}')}.png"
                StyleFig.figure.savefig(full_path, dpi = int(map_settings[0]["image dpi"]["selection"][0]), bbox_inches = "tight", format = "PNG")
            else: # Absolute paths elsewhere
                if save_loc.endswith("/"):
                    full_path = f"{dr}{save_loc.replace('.', '').replace('/', amgp.PathSep()).replace('$Y', plot_time.strftime('%Y')).replace('$m', plot_time.strftime('%m')).replace('$d', plot_time.strftime('%d')).replace('$D', plot_time.strftime('%Y-%m-%d')).replace('$t', plot_time.strftime('%H%M%SZ')).replace('$r', runtime.strftime('%Y-%m-%d_%H%M%SZ')).replace('$i', f'{figure_num - 1}').replace('$n', f'{figure_num}')}{amgp.PathSep()}{figname}"
                else:
                    full_path = f"{dr}{save_loc.replace('.', '').replace('/', amgp.PathSep()).replace('$Y', plot_time.strftime('%Y')).replace('$m', plot_time.strftime('%m')).replace('$d', plot_time.strftime('%d')).replace('$D', plot_time.strftime('%Y-%m-%d')).replace('$t', plot_time.strftime('%H%M%SZ')).replace('$r', runtime.strftime('%Y-%m-%d_%H%M%SZ')).replace('$i', f'{figure_num - 1}').replace('$n', f'{figure_num}')}.png"
                StyleFig.figure.savefig(full_path, dpi = int(map_settings[0]["image dpi"]["selection"][0]), bbox_inches = "tight", format = "PNG")
        if packed_data["key"] != None:
            if fig_fill:
                saved_fig = amgp.Water(full_path, "sw")
                saved_fig.save(full_path)
            else:
                saved_fig = amgp.Water(full_path, "c")
                saved_fig.save(full_path)
        StyleFig.Destroy()

    
    if return_image:
        # This is used to display the most recently-made map inside of the AMGP application window.
        return full_path