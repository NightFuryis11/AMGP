###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #

#           Distributed under the GPL-3.0 License             #
#                  Created on Mar 09, 2022                    #
#                                                             #
#                 Official Module: AMGP_OBS.py                #
#                     Author: Sam Bailey                      #
#                 Last Revised: Apr 14, 2025                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################

from urllib.request import urlopen

from metpy.plots import StationPlot
from metpy.calc import reduce_point_density
from metpy.units import units
from metpy.io import add_station_lat_lon
from metpy.io import metar
import metpy.plots.wx_symbols as wxsym

import cartopy.crs as ccrs

from siphon.simplewebservice.iastate import IAStateUpperAir

import pandas as pd

from io import StringIO

#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_UTIL as amgp
#-----------------  Definitions -------------------#

def Info():
    return {
        'name':"AMGP_OBS",
        'uid':"00311000"
    }

def Factors():
    return {
        'surface_station_observations':{
            'description':"Surface observed conditions.",
            'options':{
                'components':['observed_temperature', 'observed_dewpoint', 'observed_weather', 'observed_cloud_cover', 'observed_winds', 'observed_pressure', 'station_names'],
                'min_distance_between_points':["1 km", "5 km", "10 km", "15 km", "20 km", "25 km", "50 km", "75 km", "100 km", "250 km", "500 km", "750 km", "1000 km"]
            },
            'time_format':"1h",
            'is_fill':False
        },
        'upper_air_station_observations':{
            'description':"Upper-air observed conditions. Limited to the United States.",
            'options':{
                'components':['observed_temperature', 'observed_dewpoint_depression', 'observed_winds', 'observed_heights', 'station_names'],
                'level':["925 hPa", "850 hPa", "700 hPa", "500 hPa", "300 hPa", "200 hPa"]
            },
            'time_format':"12h",
            'is_fill':False
        }
    }

def Ping():
    try:
        with urlopen('http://bergeron.valpo.edu/archive_surface_data', timeout=3) as conn:
            print("(AMGP_OBS) <ping> Valpo surface archives are online")
    except:
        print("(AMGP_OBS) <ping> Valpo surface archives are offline")
    
    try:
        with urlopen('http://bergeron.valpo.edu/current_surface_data', timeout=3) as conn:
            print("(AMGP_OBS) <ping> Valpo current surface data is online")
    except:
        print("(AMGP_OBS) <ping> Valpo current surface data is offline")
    
    try:
        with urlopen('http://mesonet.agron.iastate.edu', timeout=3) as conn:
            print("(AMGP_OBS) <ping> Iowa State Mesonet is online")
    except:
        print("(AMGP_OBS) <ping> Iowa State Mesonet is offline")

    
def Plot(axis_obj, plotable, map_settings, proj_settings, time):
    map_proj = amgp.ParseProjection(proj_settings)

    if (plotable["name"] == "surface_station_observations") and (plotable["options"]["min_distance_between_points"] != []):
        min_dist = plotable["options"]["min_distance_between_points"][0]
        match min_dist:
            case "1 km":
                min_dist = 1000
            case "5 km":
                min_dist = 5000
            case "10 km":
                min_dist = 10000
            case "15 km":
                min_dist = 15000
            case "20 km":
                min_dist = 20000
            case "25 km":
                min_dist = 25000
            case "50 km":
                min_dist = 50000
            case "75 km":
                min_dist = 75000
            case "100 km":
                min_dist = 100000
            case "250 km":
                min_dist = 250000
            case "500 km":
                min_dist = 500000
            case "750 km":
                min_dist = 750000
            case "1000 km":
                min_dist = 1000000
    else:
        min_dist = 10000
    
    data, data_proj = Data(plotable, time.FormatTimes(plotable["time_format"]))

    points = map_proj.transform_points(data_proj, data['lon'], data['lat'])
    data = data[reduce_point_density(points, min_dist)]

    station_plot = StationPlot(axis_obj, data['lon'], data['lat'], clip_on = True, transform = data_proj, fontsize = 9)

    if plotable["name"] == "surface_station_observations":
        if "observed_temperature" in plotable["options"]["components"]:
            station_plot.plot_parameter("NW", data['temp'], color = 'crimson')
        
        if "observed_dewpoint" in plotable["options"]["components"]:
            station_plot.plot_parameter("SW", data['dewp'], color = 'green')
        
        if "observed_pressure" in plotable["options"]["components"]:
            station_plot.plot_parameter("NE", data['prss'], color = 'darkslategrey', formatter = lambda v: format(v*10, '.0f')[-3:])
        
        if "observed_weather" in plotable["options"]["components"]:
            station_plot.plot_symbol("W", data['wxsym'], wxsym.current_weather, color = "indigo")
        
        if "observed_cloud_cover" in plotable["options"]["components"]:
            station_plot.plot_symbol("C", data["cloud_cover"], wxsym.sky_cover)
            
        if "observed_winds" in plotable["options"]["components"]:   
            station_plot.plot_barb(data['uwnd'], data['vwnd'])
        
        if "station_names" in plotable["options"]["components"]:   
            station_plot.plot_text("SE", data['station'], color = "grey")


    if plotable["name"] == "upper_air_station_observations":
        if plotable["options"]["level"][0] in ["925 hPa", "850 hPa", "700 hPa"]:
            height_formatter = lambda v: format(v, '.0f')[1:]
        elif plotable["options"]["level"][0] in ["500 hPa", "300 hPa"]:
            height_formatter = lambda v: format(v, '.0f')[:-1]
        elif plotable["options"]["level"][0] in ["200 hPa"]:
            height_formatter = lambda v: format(v, '.0f')[1:-1]

        if "observed_temperature" in plotable["options"]["components"]:
            station_plot.plot_parameter("NW", data['temp'], color = 'crimson')
        
        if "observed_dewpoint_depression" in plotable["options"]["components"]:
            station_plot.plot_parameter("SW", data['dewd'], color = 'green')
        
        if "observed_heights" in plotable["options"]["components"]:
            station_plot.plot_parameter("NE", data['hght'], color = 'darkslategrey', formatter = height_formatter)
            
        if "observed_winds" in plotable["options"]["components"]:   
            station_plot.plot_barb(data['uwnd'], data['vwnd'], )
        
        if "station_names" in plotable["options"]["components"]:   
            station_plot.plot_text("SE", data['station'], color = "grey")

    return axis_obj

def Data(plotable, time):

    if plotable["name"] == "surface_station_observations":
        if time.timelist[0].year < 2019:
            data = pd.read_csv(f'http://bergeron.valpo.edu/archive_surface_data/{time.timelist[0]:%Y}/{time.timelist[0]:%Y%m%d}_metar.csv', parse_dates=['date_time'], na_values=[-9999], low_memory=False)
            data['wxsym'] = data.present_weather
        else:
            try:
                data = StringIO(urlopen(f'http://bergeron.valpo.edu/current_surface_data/{time.timelist[0]:%Y%m%d%H}_sao.wmo').read().decode('utf-8', 'backslashreplace'))
                data = metar.parse_metar_file(data, year=time.timelist[0].year, month=time.timelist[0].month)
            except:
                data = pd.read_csv(f'http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?data=all&tz=Etc/UTC&format=comma&latlon=yes&year1={time.timelist[0].year}&month1={time.timelist[0].month}&day1={time.timelist[0].day}&hour1={time.timelist[0].hour}&minute1={time.timelist[0].minute}&year2={time.timelist[0].year}&month2={time.timelist[0].month}&day2={time.timelist[0].day}&hour2={time.timelist[0].hour}&minute2={time.timelist[0].minute}', skiprows=5, na_values=['M'], low_memory=False).replace('T', 0.00001).groupby('station').tail(1)
                data = metar.parse_metar_file(StringIO('\n'.join(val for val in data.metar)), year=time.timelist[0].year, month=time.timelist[0].month)
                data['date_time'] = time.timelist[0]
            data['wxsym'] = data.current_wx1_symbol
        data['temp'] = (data.air_temperature.values * units.degC).to('degF')
        data['dewp'] = (data.dew_point_temperature.values * units.degC).to('degF')
        data['prss'] = data.air_pressure_at_sea_level.values * units.hPa
        data['elev'] = data.elevation.values * units.m
        data['lat'] = data.latitude
        data['lon'] = data.longitude
        data['wdir'] = data.wind_direction
        data['wspd'] = data.wind_speed.values * units('kts')
        data['uwnd'] = data.eastward_wind.values * units('kts')
        data['vwnd'] = data.northward_wind.values * units('kts')
        data['cloud_cover'] = data.cloud_coverage
        data['station'] = data.station_id
        data['dt'] = data.date_time
    
    elif plotable["name"] == "upper_air_station_observations":
        data = add_station_lat_lon(IAStateUpperAir.request_all_data(time.timelist[0])).dropna(subset=['latitude', 'longitude'])

        # It looks like the IAState site thinks the data it gets is in m/s, converts to "knots"
        #     to get values that are way to high, and passes it on. This undoes that calculation.
        data["speed"] = ((data["speed"].values * units("kts")).to("m/s")).m * units("kts")
        data["u_wind"] = ((data["u_wind"].values * units("kts")).to("m/s")).m * units("kts")
        data["v_wind"] = ((data["v_wind"].values * units("kts")).to("m/s")).m * units("kts")

        data = data[data.pressure == int(plotable["options"]["level"][0][:3])]
        data = data[data.station != 'KVER']
        data['temp'] = data.temperature.values * units.degC
        data['dewp'] = data.dewpoint.values * units.degC
        data['dewd'] = (data.temperature.values * units.degC) - (data.dewpoint.values * units.degC)
        data['prss'] = data.pressure.values * units.hPa
        data['hght'] = data.height.values * units.m
        data['lat'] = data.latitude
        data['lon'] = data.longitude
        data['wdir'] = data.direction
        data['wspd'] = data.speed.values * units('kts')
        data['uwnd'] = data.u_wind.values * units('kts')
        data['vwnd'] = data.v_wind.values * units('kts')
        data['dt'] = time.timelist[0]

    data_proj = ccrs.PlateCarree()  

    return data, data_proj