################################################
#                                              #
#       Automated Map Generation Program       #
#            Gridded Fill Module               #
#             Author: Sam Bailey               #
#        Last Revised: Aug 25, 2023            #
#                Version 0.2.0                 #
#             AMGP Version: 0.4.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
from io import StringIO
from urllib.request import urlopen

from metpy.io import add_station_lat_lon
from metpy.io import metar
from metpy.plots import declarative
from metpy.units import units
import metpy.calc as mpcalc
import os
import pandas as pd
import numpy as np
import xarray as xr

from Modules import AMGP_UTIL as amgp

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_GRDF",
            'uid':"01011000"}

def getFactors():
    return {'temp_fill':[6,1],
            'snow_temp_fill':[7,1],
            'snow_temp_contours':[7,1],
            'wind_speed_fill':[6,1],
            'temp_advect_fill':[6,1],
            'relative_vorticity_fill':[6,1],
            'absolute_vorticity_fill':[7,1],
            'cape_fill':[6,1],
            'cin_fill':[6,1]}

def factors():
    print("(AMGP_GRDF) <factors_grdf> 'temp_fill' - Gridded temperature coloration fill")
    print("(AMGP_GRDF) <factors_grdf> 'wind_speed_fill' - Gridded winds as a plot fill")
    print("(AMGP_GRDF) <factors_grdf> 'temp_advect_fill' - Gridded temperature advection")
    print("(AMGP_GRDF) <factors_grdf> 'relative_vorticity_fill' - Gridded relative vorticity")
    print("(AMGP_GRDF) <factors_grdf> 'absolute_vorticity_fill' - Gridded absolute vorticity (upper-air only)")
    print("(AMGP_GRDF) <factors_grdf> 'cape_fill' - Surface-based convective available potential energy")
    print("(AMGP_GRDF) <factors_grdf> 'cin_fill' - Surface-based convective inhibition")
    print("(AMGP_GRDF) <factors_grdf> 'snow_temp_fill' - Gridded temperature coloration fill for LE days (upper-air only)")
    print("(AMGP_GRDF) <factors_grdf> 'snow_temp_contours' - Gridded temperature contours for LE days (upper-air only)")
    
def ping(Time):
    return None

def Retrieve(Time, factors, values, LocalData=None):
    
    partialPlotsList = []
    
    LVL = amgp.GetLevel(values['level'])
    level = LVL.level
    if level != "surface":
        steps = LVL.steps
        
    if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
        time = Time.time
        time = Time.time
    else:
        timesfc = Time.threetime
        timeua = Time.twelvetime
        
    Data = FetchData(Time, level, int(values['delta']), LocalData)
    
    if level != 'surface':
        if "snow_temp_fill" in factors:
            snow_temp_fill = declarative.ContourPlot()
            snow_temp_fill.data = Data.grd
            snow_temp_fill.field = 'air'
            snow_temp_fill.level = level * units.hPa
            if Data.recent:
                snow_temp_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                snow_temp_fill.time = Data.time
            snow_temp_fill.contours = list(range(-32, 91, 2)) # rangeTL, rangeTH
            snow_temp_fill.colormap = 'coolwarm'
            snow_temp_fill.colorbar = 'horizontal'
            snow_temp_fill.plot_units = 'degF'
            partialPlotsList.append(snow_temp_fill)

        if "snow_temp_contours" in factors:
            snow_temp_contours = declarative.ContourPlot()
            snow_temp_contours.data = Data.grd
            snow_temp_contours.field = 'air'
            snow_temp_contours.level = level * units.hPa
            if Data.recent:
                snow_temp_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                snow_temp_contours.time = Data.time
            snow_temp_contours.linecolor = 'salmon'
            snow_temp_contours.linestyle = 'dashed'
            snow_temp_contours.contours = list(range(-32, 91, 2)) # rangeTL, rangeTH
            snow_temp_contours.plot_units = 'degF'
            partialPlotsList.append(snow_temp_contours)
        
        if "temp_fill" in factors:
            temp_fill = declarative.FilledContourPlot()
            temp_fill.data = Data.grd
            temp_fill.field = 'Temperature_isobaric'
            temp_fill.level = level * units.hPa
            if Data.recent:
                temp_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                temp_fill.time = Data.time
            temp_fill.contours = list(range(-100, 101, 1)) # rangeTL, rangeTH
            temp_fill.colormap = 'coolwarm'
            temp_fill.colorbar = 'horizontal'
            temp_fill.plot_units = 'degC'
            partialPlotsList.append(temp_fill)
            
        if "wind_speed_fill" in factors:
            wind_speed_fill = declarative.FilledContourPlot()
            wind_speed_fill.data = Data.grd
            wind_speed_fill.field = 'wind_speed_isobaric'
            wind_speed_fill.level = None
            wind_speed_fill.time = None
            wind_speed_fill.contours = list(range(10, 241, 20))
            wind_speed_fill.colormap = 'BuPu'
            wind_speed_fill.colorbar = 'horizontal'
            wind_speed_fill.plot_units = 'knot'
            partialPlotsList.append(wind_speed_fill)
            
        if "temp_advect_fill" in factors:
            temp_advect_fill = declarative.FilledContourPlot()
            temp_advect_fill.data = Data.grd
            temp_advect_fill.field = 'temperature_advection'
            temp_advect_fill.level = None
            temp_advect_fill.time = None
            temp_advect_fill.contours = list(np.arange(-29, 30, 0.1))
            temp_advect_fill.colormap = 'bwr'
            temp_advect_fill.colorbar = 'horizontal'
            temp_advect_fill.scale = 3
            temp_advect_fill.plot_units = 'degC/hour'
            partialPlotsList.append(temp_advect_fill)
            
        if "relative_vorticity_fill" in factors:
            relative_vorticity_fill = declarative.FilledContourPlot()
            relative_vorticity_fill.data = Data.grd
            relative_vorticity_fill.field = 'relative_vorticity'
            relative_vorticity_fill.level = None
            relative_vorticity_fill.time = None
            relative_vorticity_fill.contours = list(range(-80, 81, 2))
            relative_vorticity_fill.colormap = 'PuOr_r'
            relative_vorticity_fill.colorbar = 'horizontal'
            relative_vorticity_fill.scale = 1e5
            partialPlotsList.append(relative_vorticity_fill)
            
        if "absolute_vorticity_fill" in factors:
            absolute_vorticity_fill = declarative.FilledContourPlot()
            absolute_vorticity_fill.data = Data.grd
            absolute_vorticity_fill.field = 'Absolute_vorticity_isobaric'
            absolute_vorticity_fill.level = level * units.hPa
            if Data.recent:
                absolute_vorticity_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                absolute_vorticity_fill.time = Data.time
            absolute_vorticity_fill.contours = list(range(-80, 81, 2))
            absolute_vorticity_fill.colormap = 'PuOr_r'
            absolute_vorticity_fill.colorbar = 'horizontal'
            absolute_vorticity_fill.scale = 1e5
            partialPlotsList.append(absolute_vorticity_fill)
            
        if "cape_fill" in factors:
            cape_fill = declarative.FilledContourPlot()
            cape_fill.data = Data.grd
            cape_fill.field = 'Convective_available_potential_energy_surface'
            cape_fill.level = None
            if Data.recent:
                cape_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cape_fill.time = Data.time
            cape_fill.contours = list(range(0, 5001, 25))
            cape_fill.colormap = 'YlOrRd'
            cape_fill.colorbar = 'horizontal'
            partialPlotsList.append(cape_fill)
        
        if "cin_fill" in factors:
            cin_fill = declarative.FilledContourPlot()
            cin_fill.data = Data.grd
            cin_fill.field = 'Convective_inhibition_surface'
            cin_fill.level = None
            if Data.recent:
                cin_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cin_fill.time = Data.time
            cin_fill.contours = list(range(-700, 1, 25))
            cin_fill.colormap = 'OrRd_r'
            cin_fill.colorbar = 'horizontal'
            partialPlotsList.append(cin_fill)
            
    else:
        if "temp_fill" in factors:
            temp_fill = declarative.FilledContourPlot()
            temp_fill.data = Data.grd
            temp_fill.field = 'Temperature_height_above_ground'
            temp_fill.level = 2 * units.m
            if Data.recent:
                temp_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                temp_fill.time = Data.time
            temp_fill.contours = list(range(-68, 133, 2)) # rangeTL_F, rangeTH_F
            temp_fill.colormap = 'coolwarm'
            temp_fill.colorbar = 'horizontal'
            temp_fill.plot_units = 'degF'
            print(Data.grd.coords.to_dataset())
            partialPlotsList.append(temp_fill)
            
        if "wind_speed_fill" in factors:
            wind_speed_fill = declarative.FilledContourPlot()
            wind_speed_fill.data = Data.grd
            wind_speed_fill.field = 'wind_speed_height_above_ground'
            wind_speed_fill.level = None
            wind_speed_fill.time = None
            wind_speed_fill.contours = list(range(10, 201, 20))
            wind_speed_fill.colormap = 'BuPu'
            wind_speed_fill.colorbar = 'horizontal'
            wind_speed_fill.plot_units = 'knot'
            partialPlotsList.append(wind_speed_fill)
            
        if "temp_advect_fill" in factors:
            temp_advect_fill = declarative.FilledContourPlot()
            temp_advect_fill.data = Data.grd
            temp_advect_fill.field = 'temperature_advection'
            temp_advect_fill.level = None
            temp_advect_fill.time = None
            temp_advect_fill.contours = list(np.arange(-29, 30, 0.1))
            temp_advect_fill.colormap = 'bwr'
            temp_advect_fill.colorbar = 'horizontal'
            temp_advect_fill.scale = 3
            temp_advect_fill.plot_units = 'degC/hour'
            partialPlotsList.append(temp_advect_fill)
            
        if "relative_vorticity_fill" in factors:
            relative_vorticity_fill = declarative.FilledContourPlot()
            relative_vorticity_fill.data = Data.grd
            relative_vorticity_fill.field = 'relative_vorticity'
            relative_vorticity_fill.level = None
            relative_vorticity_fill.time = None
            relative_vorticity_fill.contours = list(range(-40, 41, 2))
            relative_vorticity_fill.colormap = 'PuOr_r'
            relative_vorticity_fill.colorbar = 'horizontal'
            relative_vorticity_fill.scale = 1e5
            partialPlotsList.append(relative_vorticity_fill)
            
        if "cape_fill" in factors:
            cape_fill = declarative.FilledContourPlot()
            cape_fill.data = Data.grd
            cape_fill.field = 'Convective_available_potential_energy_surface'
            cape_fill.level = None
            if Data.recent:
                cape_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cape_fill.time = Data.time
            cape_fill.contours = list(range(0, 5001, 25))
            cape_fill.colormap = 'YlOrRd'
            cape_fill.colorbar = 'horizontal'
            partialPlotsList.append(cape_fill)
        
        if "cin_fill" in factors:
            cin_fill = declarative.FilledContourPlot()
            cin_fill.data = Data.grd
            cin_fill.field = 'Convective_inhibition_surface'
            cin_fill.level = None
            if Data.recent:
                cin_fill.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cin_fill.time = Data.time
            cin_fill.contours = list(range(-700, 1, 25))
            cin_fill.colormap = 'OrRd_r'
            cin_fill.colorbar = 'horizontal'
            partialPlotsList.append(cin_fill)
    
    return partialPlotsList

class Data(object):
    def __init__(self, Time, level, delta, LocalData):
        
        self.recent = False
        
        if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
            self.time = Time.time
        else:
            self.time = Time.sixtime

        #self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-g3-anl-files-old/201801/20180101/gfsanl_3_20180101_0000_000.grb2').metpy.parse_cf()

        if LocalData != None:
            for Dataset in LocalData.items():
                if "1000" in Dataset[1]:
                    self.grd = xr.open_dataset(Dataset[0])
        else:
            if (Time.recentness < timedelta(days=14)):
                self.grd = xr.open_dataset(f'https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_{self.time:%Y%m%d}_{self.time:%H%M}.grib2').metpy.parse_cf()
                self.recent = True
            elif (self.time >= datetime(2004, 3, 2)):
                try:
                    self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files/'f'{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
                except:
                    try:
                        self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-g3-anl-files-old/'f'{self.time:%Y%m/%Y%m%d}/gfsanl_3_{self.time:%Y%m%d_%H}00_000.grb2').metpy.parse_cf()
                    except:
                        try:
                            self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files-old/'f'{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
                        except:
                            print("(AMGP_GRDF) <warning> Gridded data could not be found for the date you have selected!")
                            self.grd = None
            elif (self.time >= datetime(1979, 1, 1)):
                self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-narr-a-files/'f'{self.time:%Y%m/%Y%m%d}/narr-a_221_{self.time:%Y%m%d_%H}00_000.grb').metpy.parse_cf().metpy.assign_latitude_longitude()
            else:
                print("(AMGP_GRDF) <warning> The date you have selected has no gridded data available!")
                self.grd = None
        try:
            if level == 'surface':
                tmpk = self.grd.Temperature_height_above_ground.metpy.sel(vertical=2*units.m, time=self.time + timedelta(hours=delta))
                uwind = self.grd['u-component_of_wind_height_above_ground'].metpy.sel(vertical=10*units.m, time=self.time + timedelta(hours=delta))
                vwind = self.grd['v-component_of_wind_height_above_ground'].metpy.sel(vertical=10*units.m, time=self.time + timedelta(hours=delta))
                self.grd['wind_speed_height_above_ground'] = mpcalc.wind_speed(uwind, vwind)
            else:
                tmpk = self.grd.Temperature_isobaric.metpy.sel(vertical=level*units.hPa, time=self.time + timedelta(hours=delta))
                uwind = self.grd['u-component_of_wind_isobaric'].metpy.sel(vertical=level*units.hPa, time=self.time + timedelta(hours=delta))
                vwind = self.grd['v-component_of_wind_isobaric'].metpy.sel(vertical=level*units.hPa, time=self.time + timedelta(hours=delta))
                self.grd['wind_speed_isobaric'] = mpcalc.wind_speed(uwind, vwind)
            self.grd['relative_vorticity'] = mpcalc.vorticity(uwind, vwind)
            self.grd['temperature_advection'] = mpcalc.advection(tmpk, uwind, vwind)
            hght_500 = self.grd.Geopotential_height_isobaric.metpy.sel(time=self.time + timedelta(hours=delta), vertical=500 * units.hPa).metpy.quantify()
            hght_1000 = self.grd.Geopotential_height_isobaric.metpy.sel(time=self.time + timedelta(hours=delta), vertical=1000 * units.hPa).metpy.quantify()
            self.grd['thickness_500_1000'] = (hght_500 - hght_1000).metpy.dequantify()
        except:
            print("(AMGP_GRDF) <warning> Derived variables could not be calculated using the current dataset(s)")

        try:
            self.grd["Geopotential_height_isobaric"] = self.grd["hgt"]
            self.Converted = "hgt"
        except:
            self.Converted = None
        

def FetchData(Time, level, delta, LocalData):
    return Data(Time, level, delta, LocalData)