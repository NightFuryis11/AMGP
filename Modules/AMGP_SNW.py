################################################
#                                              #
#       Automated Map Generation Program       #
#          Snow Observation Module             #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.4.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime
import geopandas
import pandas
import numpy
import xarray as xr
import numpy as np
import metpy
from metpy.plots import PlotGeometry
from metpy.plots import declarative
from shapely.geometry import Point

from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#
#--------------- START DEFINITIONS ----------------#

def info():
    return {"name":"AMGP_SNW",
            "uid":"01410450"}

def getFactors():
    return {'snow_stations':[17,0]}

def factors():
    print("(AMGP_SNW) <factors_snw> 'snow_stations' - 24hr rain and snow amounts for select stations.")

def ping(Time):
    return

def Retrieve(Time, factors, values, LocalData=None):

    partialPlotsList = []

    Data = FetchData(Time, factors, values, LocalData)

    if Data.valid:
    
        if "snow_stations" in factors:
            snw = PlotGeometry()
            snw.geometry = Data.geo
            snw.fill = Data.fills
            snw.labels = Data.labels
            snw.label_edgecolor = Data.text
            snw.label_facecolor = Data.face
            partialPlotsList.append(snw)

    else:
        partialPlotsList.append("cancel")

    return partialPlotsList

class Data(object):
    def __init__(self, Time, Factors, values, LocalData):

        self.geo = []
        self.labels = []
        self.fills = []
        self.text = []
        self.face = []
        self.fullstore = {}
        self.time = Time

        try:
            for Dataset in LocalData.items():
                if "450" in Dataset[1]:
    
                    self.valid = True
                    
                    form = pandas.read_csv(filepath_or_buffer=Dataset[0])
                    
                    if form.iat[0,0] == "col":
                        location_is_column = True
                    else:
                        location_is_column = False
    
                    station_lat_rc = form.iat[0,1]
                    station_lon_rc = form.iat[0,2]
    
                    if form.iat[0,3] == "col":
                        data_is_column = True
                    else:
                        data_is_column = False
    
                    data_index_rc = form.iat[0,4]
                    data_index_format = form.iat[0,5]
                    data_year_rc = form.iat[0,6]
                    data_month_rc = form.iat[0,7]
                    data_day_rc = form.iat[0,8]
    
                    location_index_rc = form.iat[0,9]
                    location_index_format = form.iat[0,10]
    
                    if location_is_column:
                        loc = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_loc.{Dataset[0].split(".")[1]}')
                    else:
                        loc = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_loc.{Dataset[0].split(".")[1]}',index_col=location_index_rc)
    
                    if data_is_column:
                        data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}',index_col=data_index_rc)
                    else:
                        data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}')
    
                    index = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_ind.{Dataset[0].split(".")[1]}')
    
                    try:
                        d_ind = f"{Time.time.month}/{Time.time.day}/{Time.time.year}"
                    except:
                        d_ind = f"{Time.twelvetime.month}/{Time.twelvetime.day}/{Time.twelvetime.year}"
                        
                    
                    try:
                        if data.loc[d_ind]["LSsnowmax"] < 2 or data.loc[d_ind]["SNUM"] != 1:
                            self.valid = False
                    except:
                        self.valid = False
    
                    if self.valid:
                        n = 0
                        flag1 = True
                        while flag1:
                            try:
                                color = ''
                                self.geo.append(Point(loc.iat[n,station_lon_rc],loc.iat[n,station_lat_rc]))
                                self.labels.append(f"{data.loc[d_ind][index.iat[n,0]]} - {data.loc[d_ind][index.iat[n,1]]}")
                                self.fullstore[n] = (loc.iat[n,station_lat_rc], loc.iat[n,station_lon_rc], data.loc[d_ind][index.iat[n,0]], data.loc[d_ind][index.iat[n,1]])
                                if (data.loc[d_ind][index.iat[n,1]] > data.loc[d_ind][index.iat[n,0]]) or ((data.loc[d_ind][index.iat[n,1]] > 0) and (numpy.isnan(data.loc[d_ind][index.iat[n,0]]))):
                                    if data.loc[d_ind][index.iat[n,1]] > 0:
                                        color = "#A3DDFF"
                                        if data.loc[d_ind][index.iat[n,1]] > 3.8:
                                            color = "#86BEFF"
                                            if data.loc[d_ind][index.iat[n,1]] > 7.6:
                                                color = "#57CAFF"
                                                if data.loc[d_ind][index.iat[n,1]] > 15.2:
                                                    color = "#38FFF8"
                                                    if data.loc[d_ind][index.iat[n,1]] > 30:
                                                        color = "#476FFF"
                                elif (data.loc[d_ind][index.iat[n,0]] > data.loc[d_ind][index.iat[n,1]]) or ((data.loc[d_ind][index.iat[n,0]] > 0) and (numpy.isnan(data.loc[d_ind][index.iat[n,1]]))):
                                    if data.loc[d_ind][index.iat[n,0]] > 0.25:
                                        color = "#BCFFB5"
                                        if data.loc[d_ind][index.iat[n,0]] > 1.2:
                                            color = "#82F776"
                                            if data.loc[d_ind][index.iat[n,0]] > 2.5:
                                                color = "#65EF57"
                                                if data.loc[d_ind][index.iat[n,0]] > 5.0:
                                                    color = "#2DD82E"
                                                    if data.loc[d_ind][index.iat[n,0]] > 7.6:
                                                        color = "#10B211"
                                    else:
                                        color = "#FFFFFF"
                                else:
                                    color = "#FFFFFF"
                                if (data.loc[d_ind][index.iat[n,0]] > 0.25) or (data.loc[d_ind][index.iat[n,1]] > 0):
                                    self.face.append("#000000")
                                else:
                                    self.face.append("#9C9C9C")
                                if (loc.iat[n,station_lon_rc] == -90.1955) and (loc.iat[n,station_lat_rc] == 46.4625):
                                    self.fills.append("#FFFFFF")
                                    self.geo[len(self.geo)-1] = Point(loc.iat[n,station_lon_rc],loc.iat[n,station_lat_rc]+0.15)
                                else:
                                    self.fills.append(color)
                                self.text.append(color)
                                n += 1
                            except:
                                flag1 = False
                        '''
                        m = 0
                        flag2 = True
                        while flag2:
                            try:
                                self.labels.append(f"{data.loc[d_ind][index.iat[m,0]]} - {data.loc[d_ind][index.iat[m,1]]}")
                                if
                                m += 1
                            except:
                                flag2 = False
                        '''
        except:
            self.valid = False
            amgp.ThrowError("AMGP_SNW", 0, "Attempted to run the Snow Plotting module without providing a dataset.", True, False, True)
#	latitude	longitude
#	46.4625	-90.1955
#[A3DDFF, 86BEFF, 57CAFF, 38FFF8, 476FFF]
                    


def FetchData(Time, Factors, values, LocalData):
    return Data(Time, Factors, values, LocalData)

def SnowCalc(dat):
    data = dat.fullstore
    Time = dat.time
    lat=[]
    lon=[]
    points=[]
    spm = []
    lat1 = 44.74 - 0.126*2
    latstep = 0.126
    lon1 = -92.85 - 0.23675*2
    lonstep = 0.23675

    for i in list(range(0, 34)):
        lat.append(lat1 + latstep*i)
        for j in list(range(0, 44)):
            points.append([lat1 + latstep*i, lon1 + lonstep*j])
    for j in list(range(0, 44)):
        lon.append(lon1 + lonstep*j)

    spm = []
    for lat1 in lat:
        latsnowpermeter = []
        for lon1 in lon:
            snowpermeter = []
            for datapoint in data.values():
                dlat = datapoint[0]
                dlon = datapoint[1]
                snow = datapoint[3]
                dist = amgp.ArcDist(lat1, lon1, dlat, dlon)
                if numpy.isnan(snow):
                    snow = 0
                snowpermeter.append(snow/dist)
    
            latsnowpermeter.append(sum(snowpermeter)/len(snowpermeter))
        spm.append(latsnowpermeter)

    #da = xr.DataArray(spm, coords=[lat, lon], dims=["lat", "lon"], name="SnowPerMeter")
    #
    #datset = xr.Dataset({"SnowPerMeter": da})

    dataset = xr.Dataset(
        {
            "SnowPerMeter": (['lat', 'lon'], spm)
        },
        coords={
            "lat":(['lat'], lat),
            "lon":(['lon'], lon),
            "reftime": pandas.Timestamp(f"{Time.twentyfourtime.year}-{Time.twentyfourtime.month}-{Time.twentyfourtime.day}")
        },
        attrs={"description":"Snow accumulation proximity averaged over distance from each point"}
    ).metpy.parse_cf().set_coords(['lat', 'lon'])

    dataset["SnowPerMeter"] = dataset["SnowPerMeter"].metpy.convert_coordinate_units('lat', 'degrees_east')
    dataset["SnowPerMeter"] = dataset["SnowPerMeter"].metpy.convert_coordinate_units('lon', 'degrees_north')
    return(dataset)