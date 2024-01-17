################################################
#                                              #
#       Automated Map Generation Program       #
#            Gridded Data Module               #
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
    return {'name':"AMGP_GRD",
            'uid':"00610600"}

def getFactors():
    return {'height_contours':[5,0],
            'wind_contours':[5,0],
            'temp_contours':[3,0],
            'pressure_contours':[4,0],
            'dew_contours':[4,0],
            'thickness_500_1000':[3,0],
            'gridded_barbs':[3,0],
            'cape_contours':[3,0],
            'cin_contours':[3,0]}

def factors():
    print("(AMGP_GRD) <factors_grd> 'height_contours' - Gridded pressure height contours (upper-air only)")
    print("(AMGP_GRD) <factors_grd> 'wind_contours' - Gridded isotach contours (upper-air only)")
    print("(AMGP_GRD) <factors_grd> 'temp_contours' - Gridded temperature contours")
    print("(AMGP_GRD) <factors_grd> 'pressure_contours' - Gridded pressure contours (surface only)")
    print("(AMGP_GRD) <factors_grd> 'dew_contours' - Gridded dewpoint contours (surface only)")
    print("(AMGP_GRD) <factors_grd> 'thickness_500_1000' - Gridded 500mb to 1000mb thickness contours")
    print("(AMGP_GRD) <factors_grd> 'gridded_barbs' - Gridded winds")
    print("(AMGP_GRD) <factors_grd> 'cape_contours' - Surface-based convective available potential energy contours")
    print("(AMGP_GRD) <factors_grd> 'cin_contours' - Surface-based convective inhibition contours")
    
def ping(Time):
    try:
        with urlopen(f'https://thredds.ucar.edu/thredds', timeout=3) as conn:
            print("(AMGP_GRD) <ping> UCAR Thredds are online")
    except:
        print("(AMGP_GRD) <ping> UCAR Thredds are offline; this effects the following Factors: 'height_contours', 'temp_contours', 'pressure_contours', 'dew_contours', 'thickness_500_1000', 'gridded_barbs', 'cape_contours', 'cin_contours', 'temp_fill', 'wind_speed_fill', 'temp_advect_fill', 'relative_vorticity_fill', 'absolute_vorticity_fill', 'cape_fill', and 'cin_fill' for dates within two weeks")
    
    try:
        with urlopen(f'https://www.ncei.noaa.gov/thredds', timeout=3) as conn:
            print("(AMGP_GRD) <ping> NCEI Thredds are online")
    except:
        print("(AMGP_GRD) <ping> NCEI Thredds are offline; this effects the following Factors: 'height_contours', 'temp_contours', 'pressure_contours', 'dew_contours', 'thickness_500_1000', 'gridded_barbs', 'cape_contours', 'cin_contours', 'temp_fill', 'wind_speed_fill', 'temp_advect_fill', 'relative_vorticity_fill', 'absolute_vorticity_fill', 'cape_fill', and 'cin_fill' for dates beyond two weeks")

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

        if "wind_contours" in factors:
            wind_contours = declarative.ContourPlot()
            wind_contours.data = Data.grd
            wind_contours.field = 'wind_speed_isobaric'
            wind_contours.level = None
            wind_contours.time = None
            wind_contours.contours = list(range(10, 251, 20))
            wind_contours.clabels = True
            wind_contours.linecolor = 'blue'
            wind_contours.linestyle = 'dashed'
            wind_contours.plot_units = 'knot'
            wind_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(wind_contours)
            
        if "height_contours" in factors:
            pressure_heights = declarative.ContourPlot()
            pressure_heights.data = Data.grd
            pressure_heights.field = 'Geopotential_height_isobaric'
            pressure_heights.level = level * units.hPa
            if Data.recent:
                pressure_heights.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                pressure_heights.time = Data.time
            pressure_heights.contours = list(range(0, 14000, steps))
            pressure_heights.clabels = True
            pressure_heights.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(pressure_heights)
    
        if "temp_contours" in factors:
            temp_contours = declarative.ContourPlot()
            temp_contours.data = Data.grd
            temp_contours.field = 'Temperature_isobaric'
            temp_contours.level = level * units.hPa
            if Data.recent:
                temp_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
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
            if Data.recent:
                dew_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                dew_contours.time = Data.time
            dew_contours.contours = list(range(-100, 101, 5))
            dew_contours.linecolor = 'green'
            dew_contours.linestyle = 'dashed'
            dew_contours.clabels = True
            #dew_contours.plot_units = 'degC'
            dew_contours.smooth_contours = int(values['smoothing'])
            partialPlotsList.append(dew_contours)
        
        if "cape_contours" in factors:
            cape_contours = declarative.ContourPlot()
            cape_contours.data = Data.grd
            cape_contours.field = 'Convective_available_potential_energy_surface'
            cape_contours.level = None
            if Data.recent:
                cape_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cape_contours.time = Data.time
            cape_contours.contours = list(range(200, 5001, 200))
            cape_contours.linecolor = 'yellow'
            cape_contours.linestyle = 'dashed'
            cape_contours.clabels = True
            cape_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(cape_contours)
            
        if "cin_contours" in factors:
            cin_contours = declarative.ContourPlot()
            cin_contours.data = Data.grd
            cin_contours.field = 'Convective_inhibition_surface'
            cin_contours.level = None
            if Data.recent:
                cin_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cin_contours.time = Data.time
            cin_contours.contours = list(range(-700, -24, 25))
            cin_contours.linecolor = 'orange'
            cin_contours.linestyle = 'dashed'
            cin_contours.clabels = True
            cin_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(cin_contours)
        
        if "gridded_barbs" in factors:
            barbs = declarative.BarbPlot()
            barbs.data = Data.grd
            if Data.recent:
                barbs.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                barbs.time = Data.time
            barbs.field = ['u-component_of_wind_isobaric', 'v-component_of_wind_isobaric']
            barbs.level = level * units.hPa
            barbs.skip = (int(values['barbfactor']), int(values['barbfactor']))
            barbs.plot_units = 'knot'
            partialPlotsList.append(barbs)
            
    else:   
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
            if Data.recent:
                pressure.time = Data.time + timedelta(hours=int(values['delta']))
            else:
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
            if Data.recent:
                temp_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
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
            if Data.recent:
                dew_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                dew_contours.time = Data.time
            dew_contours.contours = list(range(-100, 101, 10))
            dew_contours.linecolor = 'green'
            dew_contours.linestyle = 'dashed'
            dew_contours.clabels = True
            dew_contours.plot_units = 'degF'
            dew_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(dew_contours)
        
        if "cape_contours" in factors:
            cape_contours = declarative.ContourPlot()
            cape_contours.data = Data.grd
            cape_contours.field = 'Convective_available_potential_energy_surface'
            cape_contours.level = None
            if Data.recent:
                cape_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cape_contours.time = Data.time
            cape_contours.contours = list(range(200, 5001, 200))
            cape_contours.linecolor = 'yellow'
            cape_contours.linestyle = 'dashed'
            cape_contours.clabels = True
            cape_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(cape_contours)
            
        if "cin_contours" in factors:
            cin_contours = declarative.ContourPlot()
            cin_contours.data = Data.grd
            cin_contours.field = 'Convective_inhibition_surface'
            cin_contours.level = None
            if Data.recent:
                cin_contours.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                cin_contours.time = Data.time
            cin_contours.contours = list(range(-700, -24, 25))
            cin_contours.linecolor = 'orange'
            cin_contours.linestyle = 'dashed'
            cin_contours.clabels = True
            cin_contours.smooth_contour = int(values['smoothing'])
            partialPlotsList.append(cin_contours)
            
        if "gridded_barbs" in factors:
            barbs = declarative.BarbPlot()
            barbs.data = Data.grd
            if Data.recent:
                barbs.time = Data.time + timedelta(hours=int(values['delta']))
            else:
                barbs.time = Data.time
            barbs.field = ['u-component_of_wind_height_above_ground', 'v-component_of_wind_height_above_ground']
            barbs.level = 10 * units.m
            barbs.skip = (int(values['barbfactor']), int(values['barbfactor']))
            barbs.plot_units = 'knot'
            partialPlotsList.append(barbs)
    
    return partialPlotsList

class Data(object):
    def __init__(self, Time, level, delta, LocalData):
        
        self.recent = False
        
        if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
            self.time = Time.time
        else:
            self.time = Time.sixtime

        #self.grd = xr.open_dataset("reanalysis_jan1996.nc")

        if LocalData != None:
            for Dataset in LocalData.items():
                if "600" in Dataset[1]:
                    self.grd = xr.open_dataset(Dataset[0])
        else:
            if (Time.recentness < timedelta(days=14)):
                self.grd = xr.open_dataset(f'https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_{self.time:%Y%m%d}_{self.time:%H%M}.grib2').metpy.parse_cf()
                self.recent = True
            elif (self.time >= datetime(2004, 3, 2)):
                try:
                    # More recent model data, from Oct 2022 to roughly 3 days prior to present; goes out to 384 hours.
                    self.grd = xr.open_dataset(f'https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files/{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
                except:
                    try:
                        # Slightly older model data, from Mar 2003 to May 2020; goes out to 6 hours.
                        self.grd = xr.open_dataset(f'https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-g3-anl-files-old/{self.time:%Y%m/%Y%m%d}/gfsanl_3_{self.time:%Y%m%d_%H}00_000.grb').metpy.parse_cf()
                    except:
                        try:
                            # Intermediate data, from June 2016 to May 2020; forecast hours unknown.
                            self.grd = xr.open_dataset(f'https://www.ncei.noaa.gov/thredds/dodsC/model-gfs-003-files-old/{self.time:%Y%m/%Y%m%d}/gfs_3_{self.time:%Y%m%d_%H}00_{delta:03d}.grb2').metpy.parse_cf()
                        except:
                            print("(AMGP_GRD) <warning> Gridded data could not be found for the date you have selected!")
                            self.grd = None
            elif (self.time >= datetime(1979, 1, 1)):
                self.grd = xr.open_dataset('https://www.ncei.noaa.gov/thredds/dodsC/model-narr-a-files/'f'{self.time:%Y%m/%Y%m%d}/narr-a_221_{self.time:%Y%m%d_%H}00_000.grb2').metpy.parse_cf().metpy.assign_latitude_longitude()
            else:
                print("(AMGP_GRD) <warning> The date you have selected has no gridded data available!")
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
            print("(AMGP_GRD) <warning> Derived variables could not be calculated using the current dataset(s)")

        try:
            self.grd["Geopotential_height_isobaric"] = self.grd["hgt"]
            self.Converted = "hgt"
        except:
            self.Converted = None
        

def FetchData(Time, level, delta, LocalData):
    return Data(Time, level, delta, LocalData)