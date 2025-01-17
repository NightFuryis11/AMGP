################################################
#                                              #
#       Automated Map Generation Program       #
#            Gridded Data Module               #
#             Author: Sam Bailey               #
#        Last Revised: Mar 25, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
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

def getFactors():
    return {'height_contours':5,
            'temp_contours':3,
            'pressure_contours':4,
            'dew_contours':4,
            'thickness_500_1000':3,
            'gridded_barbs':3,
            'temp_fill':6,
            'wind_speed_fill':6,
            'temp_advect_fill':6,
            'relative_vorticity_fill':6,
            'absolute_vorticity_fill':7}

def factors():
    print("<factors_grd> 'height_contours' - Gridded pressure height contours (upper-air only)")
    print("<factors_grd> 'temp_contours' - Gridded temperature contours")
    print("<factors_grd> 'temp_fill' - Gridded temperature coloration fill")
    print("<factors_grd> 'wind_speed_fill' - Gridded winds as a plot fill")
    print("<factors_grd> 'temp_advect_fill' - Gridded temperature advection")
    print("<factors_grd> 'relative_vorticity_fill' - Gridded relative vorticity")
    print("<factors_grd> 'absolute_vorticity_fill' - Gridded absolute vorticity (upper-air only)")
    print("<factors_grd> 'pressure_contours' - Gridded pressure contours (surface only)")
    print("<factors_grd> 'dew_contours' - Gridded dewpoint contours (surface only)")
    print("<factors_grd> 'thickness_500_1000' - Gridded 500mb to 1000mb thickness contours")
    print("<factors_grd> 'gridded_barbs' - Gridded winds")

def Retrieve(Time, factors, values):
    
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
        
    Data = FetchData(Time, level)
    
    if level != 'surface':
        if "temp_fill" in factors:
            temp_fill = declarative.FilledContourPlot()
            temp_fill.data = Data.grd
            temp_fill.field = 'Temperature_isobaric'
            temp_fill.level = level * units.hPa
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
            absolute_vorticity_fill.time = Data.time
            absolute_vorticity_fill.contours = list(range(-80, 81, 2))
            absolute_vorticity_fill.colormap = 'PuOr_r'
            absolute_vorticity_fill.colorbar = 'horizontal'
            absolute_vorticity_fill.scale = 1e5
            partialPlotsList.append(absolute_vorticity_fill)
            
        if "thickness_500_1000" in factors:
            thickness_500_1000 = declarative.ContourPlot()
            thickness_500_1000.data = Data.grd
            thickness_500_1000.field = 'thickness_500_1000'
            thickness_500_1000.level = None
            thickness_500_1000.time = None
            thickness_500_1000.contours = list(range(0, 10000, 60))
            thickness_500_1000.clabels = True
            thickness_500_1000.linestyle = 'dashed'
            thickness_500_1000.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(thickness_500_1000)
            
        if "height_contours" in factors:
            pressure_heights = declarative.ContourPlot()
            pressure_heights.data = Data.grd
            pressure_heights.field = 'Geopotential_height_isobaric'
            pressure_heights.level = level * units.hPa
            pressure_heights.time = Data.time
            pressure_heights.contours = list(range(0, 12000, steps))
            pressure_heights.clabels = True
            pressure_heights.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(pressure_heights)
    
        if "temp_contours" in factors:
            temp_contours = declarative.ContourPlot()
            temp_contours.data = Data.grd
            temp_contours.field = 'Temperature_isobaric'
            temp_contours.level = level * units.hPa
            temp_contours.time = Data.time
            temp_contours.contours = list(range(-100, 101, 5))
            temp_contours.linecolor = 'red'
            temp_contours.linestyle = 'dashed'
            temp_contours.clabels = True
            temp_contours.plot_units = 'degC'
            temp_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(temp_contours)

        if "dew_contours" in factors:
            hPaLevel = level * units.hPa
            tmpIsoSel = Data.grd['Temperature_isobaric'].metpy.sel(vertical=hPaLevel)
            rhIsoSel = Data.grd['Relative_humidity_isobaric'].metpy.sel(vertical=hPaLevel)
            Data.grd['Dewpoint_isobaric'] = mpcalc.dewpoint_from_relative_humidity(tmpIsoSel, rhIsoSel)
            dew_contours = declarative.ContourPlot()
            dew_contours.data = Data.grd
            dew_contours.field = 'Dewpoint_isobaric'
            dew_contours.level = None
            dew_contours.time = Data.time
            dew_contours.contours = list(range(-100, 101, 5))
            dew_contours.linecolor = 'green'
            dew_contours.linestyle = 'dashed'
            dew_contours.clabels = True
            #dew_contours.plot_units = 'degC'
            dew_contours.smooth_contours = int(values['smoothing'])
            partialPlotsList.append(dew_contours)
        
        if "gridded_barbs" in factors:
            barbs = declarative.BarbPlot()
            barbs.data = Data.grd
            barbs.time = Data.time
            barbs.field = ['u-component_of_wind_isobaric', 'v-component_of_wind_isobaric']
            barbs.level = level * units.hPa
            barbs.skip = (int(values['barbfactor']), int(values['barbfactor']))
            barbs.plot_units = 'knot'
            partialPlotsList.append(barbs)
            
    else:
        if "temp_fill" in factors:
            temp_fill = declarative.FilledContourPlot()
            temp_fill.data = Data.grd
            temp_fill.field = 'Temperature_height_above_ground'
            temp_fill.level = 2 * units.m
            temp_fill.time = Data.time
            temp_fill.contours = list(range(-68, 133, 2)) # rangeTL_F, rangeTH_F
            temp_fill.colormap = 'coolwarm'
            temp_fill.colorbar = 'horizontal'
            temp_fill.plot_units = 'degF'
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
            
        if "thickness_500_1000" in factors:
            thickness_500_1000 = declarative.ContourPlot()
            thickness_500_1000.data = Data.grd
            thickness_500_1000.field = 'thickness_500_1000'
            thickness_500_1000.level = None
            thickness_500_1000.time = None
            thickness_500_1000.contours = list(range(0, 10000, 60))
            thickness_500_1000.clabels = True
            thickness_500_1000.linestyle = 'dashed'
            thickness_500_1000.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(thickness_500_1000)

        if "pressure_contours" in factors:
            pressure = declarative.ContourPlot()
            pressure.data = Data.grd
            pressure.field = 'Pressure_reduced_to_MSL_msl'
            pressure.level = None
            pressure.time = Data.time
            pressure.contours = list(range(0, 2000, 4))
            pressure.clabels = True
            pressure.plot_units = 'hPa'
            pressure.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(pressure)
            
        if "temp_contours" in factors:
            temp_contours = declarative.ContourPlot()
            temp_contours.data = Data.grd
            temp_contours.field = 'Temperature_height_above_ground'
            temp_contours.level = 2 * units.m
            temp_contours.time = Data.time
            temp_contours.contours = list(range(-100, 101, 10))
            temp_contours.linecolor = 'red'
            temp_contours.linestyle = 'dashed'
            temp_contours.clabels = True
            temp_contours.plot_units = 'degF'
            temp_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(temp_contours)
            
        if "dew_contours" in factors:
            dew_contours = declarative.ContourPlot()
            dew_contours.data = Data.grd
            dew_contours.field = 'Dewpoint_temperature_height_above_ground'
            dew_contours.level = 2 * units.m
            dew_contours.time = Data.time
            dew_contours.contours = list(range(-100, 101, 10))
            dew_contours.linecolor = 'green'
            dew_contours.linestyle = 'dashed'
            dew_contours.clabels = True
            dew_contours.plot_units = 'degF'
            dew_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(dew_contours)
            
        if "gridded_barbs" in factors:
            barbs = declarative.BarbPlot()
            barbs.data = Data.grd
            barbs.time = Data.time
            barbs.field = ['u-component_of_wind_height_above_ground', 'v-component_of_wind_height_above_ground']
            barbs.level = 10 * units.m
            barbs.skip = (int(values['barbfactor']), int(values['barbfactor']))
            barbs.plot_units = 'knot'
            partialPlotsList.append(barbs)
    
    return partialPlotsList

class Data(object):
    def __init__(self, Time, level):
        
        if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
            self.time = Time.time
        else:
            self.time = Time.sixtime
        
        if (Time.recentness < timedelta(days=14)):
            self.grd = xr.open_dataset('https://thredds.ucar.edu/thredds/dodsC/grib'f'/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_{self.time:%Y%m%d}_{self.time:%H%M}.grib2').metpy.parse_cf()
        elif (self.time >= datetime(2004, 3, 2)):
            try:
                self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files/'f'{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
            except:
                try:
                    self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-g3-anl-files-old/'f'{self.time:%Y%m/%Y%m%d}/gfsanl_3_{self.time:%Y%m%d_%H}00_000.grb').metpy.parse_cf()
                except:
                    try:
                        self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files-old/'f'{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
                    except:
                        print("<warning> Gridded data could not be found for the date you have selected!")
                        self.grd = None
        elif (self.time >= datetime(1979, 1, 1)):
            self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-narr-a-files/'f'{self.time:%Y%m/%Y%m%d}/narr-a_221_{self.time:%Y%m%d_%H}00_000.grb').metpy.parse_cf().metpy.assign_latitude_longitude()
        else:
            print("<warning> The date you have selected has no gridded data available!")
            self.grd = None
        
        if level == 'surface':
            tmpk = self.grd.Temperature_height_above_ground.metpy.sel(vertical=2*units.m, time=self.time)
            uwind = self.grd['u-component_of_wind_height_above_ground'].metpy.sel(vertical=10*units.m, time=self.time)
            vwind = self.grd['v-component_of_wind_height_above_ground'].metpy.sel(vertical=10*units.m, time=self.time)
            self.grd['wind_speed_height_above_ground'] = mpcalc.wind_speed(uwind, vwind)
        else:
            tmpk = self.grd.Temperature_isobaric.metpy.sel(vertical=level*units.hPa, time=self.time)
            uwind = self.grd['u-component_of_wind_isobaric'].metpy.sel(vertical=level*units.hPa, time=self.time)
            vwind = self.grd['v-component_of_wind_isobaric'].metpy.sel(vertical=level*units.hPa, time=self.time)
            self.grd['wind_speed_isobaric'] = mpcalc.wind_speed(uwind, vwind)
        self.grd['relative_vorticity'] = mpcalc.vorticity(uwind, vwind)
        self.grd['temperature_advection'] = mpcalc.advection(tmpk, uwind, vwind)
        hght_500 = self.grd.Geopotential_height_isobaric.metpy.sel(time=self.time, vertical=500 * units.hPa).metpy.quantify()
        hght_1000 = self.grd.Geopotential_height_isobaric.metpy.sel(time=self.time, vertical=1000 * units.hPa).metpy.quantify()
        self.grd['thickness_500_1000'] = (hght_500 - hght_1000).metpy.dequantify()
        

def FetchData(Time, level):
    return Data(Time, level)