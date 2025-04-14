###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #
#           Distributed under the GPL-3.0 License             #
#                  Created on Mar 09, 2022                    #
#                                                             #
#             Official Module: AMGP_MODEL_FILL.py             #
#                     Author: Sam Bailey                      #
#                 Last Revised: Apr 14, 2025                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################

from datetime import timedelta
from urllib.request import urlopen

from metpy.units import units

import cartopy.crs as ccrs

import xarray as xr
import numpy as np

#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_UTIL as amgp
#-----------------  Definitions -------------------#

def Info():
    return {
        'name':"AMGP_MODEL_FILL",
        'uid':"00510400"
    }

def Factors():
    return {
        'filled_gfs_contours':{
            'description':"Gridded model outputs from the operational GFS model, plotted as filled contours.", #'limit_to_closest_forecast' takes priority over 'forecast_hour'.
            'options':{
                'components':['temperature', 'dewpoint', 'dewpoint_depression', 'vertical', 'wind_magnitude', 'zonal_winds', 'meridional_winds', 'sbcape', 'sbcin', 'mucape', 'mucin', 'mlcape', 'mlcin', 'potential_temperature', 'equivalent_potential_temperature'],
                'level':["surface", "1000 hPa", "925 hPa", "850 hPa", "700 hPa", "500 hPa", "300 hPa", "200 hPa"],
                'resolution':["one_deg", "half-deg", "quarter-deg"],
                #'limit_to_closest_forecast':["Bool"],
                'forecast_hour':[None]
            },
            'time_format':"6h",
            'is_fill':True
        }
    }

def Ping():
    try:
        with urlopen('https://thredds.ucar.edu/thredds', timeout=3) as conn:
            print("(AMGP_MODEL) <ping> UCAR Thredds are online")
    except:
        print("(AMGP_MODEL) <ping> UCAR Thredds are offline")
    
    try:
        with urlopen('https://www.ncei.noaa.gov/thredds', timeout=3) as conn:
            print("(AMGP_MODEL) <ping> NCEI Thredds are online")
    except:
        print("(AMGP_MODEL) <ping> NCEI Thredds are offline")

def Plot(axis_obj, plotable, map_settings, proj_settings, time):
    map_proj = amgp.ParseProjection(proj_settings)

    data, data_proj = Data(plotable, time.FormatTimes(plotable["time_format"]))

    if plotable["name"] == "filled_gfs_contours":
        if "temperature" in plotable["options"]["components"]:
            if plotable["options"]["level"][0] == "surface":
                axis_obj.contourf(data["lon"], data["lat"], data["temp"].m, transform = data_proj, cmap = "bwr", levels = np.arange(-56, 120.1, 4))
            else:
                axis_obj.contourf(data["lon"], data["lat"], data["temp"].m, transform = data_proj, cmap = "bwr", levels = np.arange(-100, 100.1, 2))


    return axis_obj

def Data(plotable, time):

    return_data = {}

    if plotable["name"] == "filled_gfs_contours":
        
        try:
            if plotable["options"]["resolution"][0] == "one_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_{time.timelist[0].strftime('%Y%m%d_%H%M')}.grib2")
            elif plotable["options"]["resolution"][0] == "half_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p5deg/GFS_Global_0p5deg_{time.timelist[0].strftime('%Y%m%d_%H%M')}.grib2")
            elif plotable["options"]["resolution"][0] == "quarter_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/GFS_Global_0p25deg_{time.timelist[0].strftime('%Y%m%d_%H%M')}.grib2")
        except:
            if plotable["options"]["resolution"][0] == "one_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_{(time.timelist[0] - timedelta(hours = 6)).strftime('%Y%m%d_%H%M')}.grib2")
            elif plotable["options"]["resolution"][0] == "half_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p5deg/GFS_Global_0p5deg_{(time.timelist[0] - timedelta(hours = 6)).strftime('%Y%m%d_%H%M')}.grib2")
            elif plotable["options"]["resolution"][0] == "quarter_deg":
                data = xr.open_dataset(f"https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_0p25deg/GFS_Global_0p25deg_{(time.timelist[0] - timedelta(hours = 6)).strftime('%Y%m%d_%H%M')}.grib2")
        
        fhour = int(plotable["options"]["forecast_hour"][0])
        #if plotable["options"]["limit_to_closest_forecast"][0]:


        data = data.sel(time3 = (time.timelist[0] + timedelta(hours = fhour)).replace(tzinfo = None), method = "nearest")
        data = data.sel(time = (time.timelist[0] + timedelta(hours = fhour)).replace(tzinfo = None), method = "nearest")
        
        return_data["lat"] = data.lat
        return_data["lon"] = data.lon

        if plotable["options"]["level"][0] == "surface":
            data = data.sel(height_above_ground3 = 2)
            return_data["temp"] = (data["Temperature_height_above_ground"].values * units("K")).to("degC")
        else:
            if plotable["options"]["level"][0] == "1000 hPa":
                level = 100000
            elif plotable["options"]["level"][0] == "925 hPa":
                level = 92500
            elif plotable["options"]["level"][0] == "850 hPa":
                level = 85000
            elif plotable["options"]["level"][0] == "700 hPa":
                level = 70000
            elif plotable["options"]["level"][0] == "500 hPa":
                level = 50000
            elif plotable["options"]["level"][0] == "300 hPa":
                level = 30000
            elif plotable["options"]["level"][0] == "200 hPa":
                level = 20000

            data = data.sel(isobaric = level)

            return_data["temp"] = (data["Temperature_isobaric"].values * units("K")).to("degC")





    return return_data, ccrs.PlateCarree()