################################################
#                                              #
#       Automated Map Generation Program       #
#          Snow Calculation Module             #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.2.0                 #
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
import math
from time import sleep
from requests import HTTPError
from metpy.units import units, pandas_dataframe_to_unit_arrays
from metpy.plots import PlotGeometry
from metpy.plots import declarative
import metpy.calc as mpcalc
from siphon.simplewebservice.wyoming import WyomingUpperAir
from shapely.geometry import Point
from matplotlib import colors as mplc

from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#
#--------------- START DEFINITIONS ----------------#

def info():
    return {"name":"AMGP_SCAL",
            "uid":"01511050"}

def getFactors():
    return {'snow_per_meter':[18,1],
           'snow_deriv':[19,1],
           'snow_grad':[20,1],
           'tscalc':[-1, 0]}

def factors():
    print("(AMGP_SCAL) <factors_scal> 'snow_per_meter' - Spacial distribution of the snowfall.")
    print("(AMGP_SCAL) <factors_scal> 'snow_deriv' - Spatial condensation of the snowfall.")
    print("(AMGP_SCAL) <factors_scal> 'snow_grad' - Special spatial condensation of the snowfall.")

def ping(Time):
    return

def Retrieve(Time, factors, values, LocalData=None):

    partialPlotsList = []

    if "snow_per_meter" in factors or "snow_deriv" in factors or "snow_grad" in factors:
        Data = FetchData(Time, factors, values, LocalData)
    
        if Data.valid:
            dat = SnowCalc(Data)
            
            if "snow_per_meter" in factors:
                calc = declarative.FilledContourPlot()
                calc.data = dat
                calc.field = "SnowPerMeter"
                calc.level = None
                calc.time = None
                calc.colorbar = 'horizontal'
                calc.colormap = 'Blues'
                #calc.plot_units = "cm/m"
                #calc.scale = 1e4
                calc.image_range = mplc.PowerNorm(gamma=0.35)
                calc.contours = list(numpy.arange(0, 1e-3+5e-5, 5e-6))
                partialPlotsList.append(calc)
    
            if "snow_deriv" in factors:
                calc = declarative.FilledContourPlot()
                calc.data = dat
                calc.field = "SnowPerMeterSquared"
                calc.level = None
                calc.time = None
                calc.colorbar = 'horizontal'
                calc.colormap = 'Purples'
                #calc.plot_units = "cm/m^s"
                #calc.scale = 1e4
                #calc.image_range = mplc.LogNorm(vmin=1e-12,vmax=1e-8)
                calc.image_range = mplc.PowerNorm(gamma=0.25)
                calc.contours = list(numpy.arange(0, 1e-8+1e-10, 1e-11))
                partialPlotsList.append(calc)
    
            if "snow_grad" in factors:
                calc = declarative.FilledContourPlot()
                calc.data = dat
                calc.field = "SnowGradient"
                calc.level = None
                calc.time = None
                calc.colorbar = 'horizontal'
                calc.colormap = 'PuBu'
                #calc.plot_units = "cm/m^s"
                #calc.scale = 1e4
                #calc.image_range = mplc.LogNorm(vmin=1e-12,vmax=1e-8)
                #calc.image_range = mplc.PowerNorm(gamma=0.25)
                calc.contours = list(numpy.arange(0, 1e-4+1e-7, 1e-7))
                partialPlotsList.append(calc)
        else:
            partialPlotsList.append("cancel")

    if "tscalc" in factors:
        stlpcalc(Time, LocalData)
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
                if "1050" in Dataset[1]:
    
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
                        data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}',index_col=data_index_rc,low_memory=False)
                    else:
                        data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}',low_memory=False)
    
                    index = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_ind.{Dataset[0].split(".")[1]}')
    
                    try:
                        self.d_ind = f"{Time.time.month}/{Time.time.day}/{Time.time.year}"
                    except:
                        self.d_ind = f"{Time.twelvetime.month}/{Time.twelvetime.day}/{Time.twelvetime.year}"
                        
                    
                    try:
                        if data.loc[self.d_ind]["LSsnowmax"] < 2 or data.loc[self.d_ind]["SNUM"] != 1:
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
                                self.labels.append(f"{data.loc[self.d_ind][index.iat[n,0]]} - {data.loc[self.d_ind][index.iat[n,1]]}")
                                self.fullstore[n] = (loc.iat[n,station_lat_rc], loc.iat[n,station_lon_rc], data.loc[self.d_ind][index.iat[n,0]], data.loc[self.d_ind][index.iat[n,1]])
                                if (data.loc[self.d_ind][index.iat[n,1]] > data.loc[self.d_ind][index.iat[n,0]]) or ((data.loc[self.d_ind][index.iat[n,1]] > 0) and (numpy.isnan(data.loc[self.d_ind][index.iat[n,0]]))):
                                    if data.loc[self.d_ind][index.iat[n,1]] > 0:
                                        color = "#A3DDFF"
                                        if data.loc[self.d_ind][index.iat[n,1]] > 3.8:
                                            color = "#86BEFF"
                                            if data.loc[self.d_ind][index.iat[n,1]] > 7.6:
                                                color = "#57CAFF"
                                                if data.loc[self.d_ind][index.iat[n,1]] > 15.2:
                                                    color = "#38FFF8"
                                                    if data.loc[self.d_ind][index.iat[n,1]] > 30:
                                                        color = "#476FFF"
                                elif (data.loc[self.d_ind][index.iat[n,0]] > data.loc[self.d_ind][index.iat[n,1]]) or ((data.loc[self.d_ind][index.iat[n,0]] > 0) and (numpy.isnan(data.loc[self.d_ind][index.iat[n,1]]))):
                                    if data.loc[self.d_ind][index.iat[n,0]] > 0.25:
                                        color = "#BCFFB5"
                                        if data.loc[self.d_ind][index.iat[n,0]] > 1.2:
                                            color = "#82F776"
                                            if data.loc[self.d_ind][index.iat[n,0]] > 2.5:
                                                color = "#65EF57"
                                                if data.loc[self.d_ind][index.iat[n,0]] > 5.0:
                                                    color = "#2DD82E"
                                                    if data.loc[self.d_ind][index.iat[n,0]] > 7.6:
                                                        color = "#10B211"
                                    else:
                                        color = "#FFFFFF"
                                else:
                                    color = "#FFFFFF"
                                if (data.loc[self.d_ind][index.iat[n,0]] > 0.25) or (data.loc[self.d_ind][index.iat[n,1]] > 0):
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
                                self.labels.append(f"{data.loc[self.d_ind][index.iat[m,0]]} - {data.loc[self.d_ind][index.iat[m,1]]}")
                                if
                                m += 1
                            except:
                                flag2 = False
                        '''
        except:
            self.valid = False
            amgp.ThrowError("AMGP_SCAL", 0, "Attempted to run the Snow Calculation module without providing a dataset.", datetime.utcnow(), True, False, True)
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
    lat1 = 44.74 - 0.0126*20
    latstep = 0.0126
    lon1 = -92.85 - 0.023675*20
    lonstep = 0.023675

    for i in list(range(0, 340)):
        lat.append(lat1 + latstep*i)
        for j in list(range(0, 440)):
            points.append([lat1 + latstep*i, lon1 + lonstep*j])
    for j in list(range(0, 440)):
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

    '''spmm = []
    p = 0
    q = 0
    for lat1 in lat:
        latsnowderiv = []
        p += 1
        for lon1 in lon:
            lonsnowderiv = []
            q += 1
            for i in lat:
                for j in lon:
                    dist = amgp.ArcDist(lat1, lon1, i, j)
                    if dist != 0:
                        snowpm = spm[p-1][q-1]
                        lonsnowderiv.append(snowpm/dist)
                    else:
                        lonsnowderiv.append(0)

            latsnowderiv.append(sum(lonsnowderiv)/len(lonsnowderiv))

        q = 0
        spmm.append(latsnowderiv)'''

    sg = np.gradient(spm, lat, lon)

    sgm = []
    for i in range(0, len(sg[0]), 1):
        pout = []
        for j in range(0, len(sg[0][0]), 1):
            pout.append(math.sqrt(sg[0][i][j] * sg[0][i][j] + sg[1][i][j] * sg[1][i][j]))
        sgm.append(pout)

    #da = xr.DataArray(spm, coords=[lat, lon], dims=["lat", "lon"], name="SnowPerMeter")
    #
    #datset = xr.Dataset({"SnowPerMeter": da})

    dataset = xr.Dataset(
        {
            "SnowPerMeter": (['lat', 'lon'], spm),
            #"SnowPerMeterSquared": (['lat', 'lon'], spmm),
            "SnowGradient": (['lat', 'lon'], sgm)
        },
        coords={
            "lat":(['lat'], lat),
            "lon":(['lon'], lon),
            "reftime": pandas.Timestamp(f"{Time.twentyfourtime.year}-{Time.twentyfourtime.month}-{Time.twentyfourtime.day}")
        },
        attrs={"description":"Snow accumulation proximity averaged over distance from each point"}
    ).metpy.parse_cf().set_coords(['lat', 'lon'])

    #dataset["SnowPerMeter"] = dataset["SnowPerMeter"].metpy.convert_coordinate_units('lat', 'degrees_east')
    #dataset["SnowPerMeter"] = dataset["SnowPerMeter"].metpy.convert_coordinate_units('lon', 'degrees_north')
    #dataset["SnowPerMeterSquared"] = dataset["SnowPerMeterSquared"].metpy.convert_coordinate_units('lat', 'degrees_east')
    #dataset["SnowPerMeterSquared"] = dataset["SnowPerMeterSquared"].metpy.convert_coordinate_units('lon', 'degrees_north')
    return(dataset)


def stlpcalc(Time, LocalData):
    try:
        for Dataset in LocalData.items():
            if "1050" in Dataset[1]:
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
                    data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}',index_col=data_index_rc,low_memory=False)
                else:
                    data = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_dat.{Dataset[0].split(".")[1]}',low_memory=False)
    
                index = pandas.read_csv(filepath_or_buffer=f'{Dataset[0].split(".")[0].split("%")[0]}_ind.{Dataset[0].split(".")[1]}')

                

                try:
                    year = Time.time.year
                    month = Time.time.month
                    day = Time.time.day
                except:
                    year = Time.twelvetime.year
                    month = Time.twelvetime.month
                    day = Time.twelvetime.day
                hour = 0

                d_ind = f"{month}/{day}/{year}"

                try:
                    data.loc[f"{d_ind}"]
                except KeyError:
                    return
                
                KGRB = GetGRB(year, month, day)
                if KGRB != None:
                    sKGRB = KGRB["pressure"].m > 90

                    GRB_P = KGRB["pressure"][sKGRB].magnitude.tolist()
                    GRB_T = KGRB["temperature"][sKGRB].magnitude.tolist()
                    GRB_Td = KGRB["dewpoint"][sKGRB].magnitude.tolist()
                    GRB_z = KGRB["height"][sKGRB].magnitude.tolist()
                    GRB_u = KGRB["u_wind"][sKGRB].magnitude.tolist()
                    GRB_v = KGRB["u_wind"][sKGRB].magnitude.tolist()

                    plain_GRB_P = KGRB["pressure"][sKGRB].magnitude  * units("hPa")
                    plain_GRB_T = KGRB["temperature"][sKGRB].magnitude * units("degC")

                    try:
                        GRB_parcel = mpcalc.parcel_profile(GRB_P * units("hPa"), (GRB_T[0] * units("degC")), (GRB_Td[0] * units("degC"))).to("degC")
                        data.loc[[f"{d_ind}"], ["KGRB_LI"]] = mpcalc.lifted_index(GRB_P * units("hPa"), GRB_T * units("degC"), GRB_parcel)
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_LI"]] = "null_data"
    
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_T_SFC"]] = GRB_T[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_T_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_Td_SFC"]] = GRB_Td[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_Td_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_z_SFC"]] = GRB_z[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_z_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_u_SFC"]] = GRB_u[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_u_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_v_SFC"]] = GRB_v[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_v_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_P_SFC"]] = GRB_P[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_P_SFC"]] = "null_data"

                    try:
                        GRB_P_LCL, GRB_T_LCL = mpcalc.lcl(GRB_P[0] * units("hPa"), GRB_T[0] * units("degC"), GRB_Td[0] * units("degC"))
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KGRB_P_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_T_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_z_LCL"]] = "null_data"
                    else:
                        data.loc[[f"{d_ind}"], ["KGRB_P_LCL"]] = GRB_P_LCL
                        data.loc[[f"{d_ind}"], ["KGRB_T_LCL"]] = GRB_T_LCL
                        mod_GRB_P = np.append(plain_GRB_P[plain_GRB_P > GRB_P_LCL], GRB_P_LCL)
                        mod_GRB_T = np.append(plain_GRB_T[plain_GRB_P > GRB_P_LCL], GRB_T_LCL)
                        data.loc[[f"{d_ind}"], ["KGRB_z_LCL"]] = mpcalc.thickness_hydrostatic(mod_GRB_P, mod_GRB_T)

                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_T_925"]] = GRB_T[GRB_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KGRB_Td_925"]] = GRB_Td[GRB_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KGRB_z_925"]] = GRB_z[GRB_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KGRB_u_925"]] = GRB_u[GRB_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KGRB_v_925"]] = GRB_v[GRB_P.index(925)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KGRB_T_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_Td_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_z_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_u_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_v_925"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_T_850"]] = GRB_T[GRB_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KGRB_Td_850"]] = GRB_Td[GRB_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KGRB_z_850"]] = GRB_z[GRB_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KGRB_u_850"]] = GRB_u[GRB_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KGRB_v_850"]] = GRB_v[GRB_P.index(850)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KGRB_T_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_Td_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_z_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_u_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_v_850"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_T_700"]] = GRB_T[GRB_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KGRB_Td_700"]] = GRB_Td[GRB_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KGRB_z_700"]] = GRB_z[GRB_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KGRB_u_700"]] = GRB_u[GRB_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KGRB_v_700"]] = GRB_v[GRB_P.index(700)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KGRB_T_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_Td_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_z_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_u_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_v_700"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KGRB_T_500"]] = GRB_T[GRB_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KGRB_Td_500"]] = GRB_Td[GRB_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KGRB_z_500"]] = GRB_z[GRB_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KGRB_u_500"]] = GRB_u[GRB_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KGRB_v_500"]] = GRB_v[GRB_P.index(500)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KGRB_T_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_Td_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_z_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_u_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KGRB_v_500"]] = "null_data"
                        
                else:
                    data.loc[[f"{d_ind}"], ["KGRB_LI"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_T_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_Td_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_u_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_v_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_P_SFC"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_P_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_T_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_LCL"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_T_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_Td_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_u_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_v_925"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_T_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_Td_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_u_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_v_850"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_T_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_Td_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_u_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_v_700"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KGRB_T_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_Td_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_z_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_u_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KGRB_v_500"]] = "null_data"
                    
                KAPX = GetAPX(year, month, day)
                if KAPX != None:
                    sKAPX = KAPX["pressure"].m > 90

                    APX_P = KAPX["pressure"][sKAPX].magnitude.tolist()
                    APX_T = KAPX["temperature"][sKAPX].magnitude.tolist()
                    APX_Td = KAPX["dewpoint"][sKAPX].magnitude.tolist()
                    APX_z = KAPX["height"][sKAPX].magnitude.tolist()
                    APX_u = KAPX["u_wind"][sKAPX].magnitude.tolist()
                    APX_v = KAPX["u_wind"][sKAPX].magnitude.tolist()

                    plain_APX_P = KAPX["pressure"][sKAPX].magnitude * units("hPa")
                    plain_APX_T = KAPX["temperature"][sKAPX].magnitude * units("degC")

                    try:
                        APX_parcel = mpcalc.parcel_profile(APX_P * units("hPa"), (APX_T[0] * units("degC")), (APX_Td[0] * units("degC"))).to("degC")
                        data.loc[[f"{d_ind}"], ["KAPX_LI"]] = mpcalc.lifted_index(APX_P * units("hPa"), APX_T * units("degC"), APX_parcel)
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_LI"]] = "null_data"
    
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_T_SFC"]] = APX_T[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_T_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_Td_SFC"]] = APX_Td[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_Td_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_z_SFC"]] = APX_z[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_z_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_u_SFC"]] = APX_u[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_u_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_v_SFC"]] = APX_v[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_v_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_P_SFC"]] = APX_P[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_P_SFC"]] = "null_data"

                    try:
                        APX_P_LCL, APX_T_LCL = mpcalc.lcl(APX_P[0] * units("hPa"), APX_T[0] * units("degC"), APX_Td[0] * units("degC"))
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KAPX_P_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_T_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_z_LCL"]] = "null_data"
                    else:
                        data.loc[[f"{d_ind}"], ["KAPX_P_LCL"]] = APX_P_LCL
                        data.loc[[f"{d_ind}"], ["KAPX_T_LCL"]] = APX_T_LCL
                        mod_APX_P = np.append(plain_APX_P[plain_APX_P > APX_P_LCL], APX_P_LCL)
                        mod_APX_T = np.append(plain_APX_T[plain_APX_P > APX_P_LCL], APX_T_LCL)
                        data.loc[[f"{d_ind}"], ["KAPX_z_LCL"]] = mpcalc.thickness_hydrostatic(mod_APX_P, mod_APX_T)

                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_T_925"]] = APX_T[APX_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KAPX_Td_925"]] = APX_Td[APX_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KAPX_z_925"]] = APX_z[APX_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KAPX_u_925"]] = APX_u[APX_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KAPX_v_925"]] = APX_v[APX_P.index(925)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KAPX_T_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_Td_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_z_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_u_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_v_925"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_T_850"]] = APX_T[APX_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KAPX_Td_850"]] = APX_Td[APX_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KAPX_z_850"]] = APX_z[APX_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KAPX_u_850"]] = APX_u[APX_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KAPX_v_850"]] = APX_v[APX_P.index(850)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KAPX_T_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_Td_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_z_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_u_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_v_850"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_T_700"]] = APX_T[APX_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KAPX_Td_700"]] = APX_Td[APX_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KAPX_z_700"]] = APX_z[APX_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KAPX_u_700"]] = APX_u[APX_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KAPX_v_700"]] = APX_v[APX_P.index(700)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KAPX_T_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_Td_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_z_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_u_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_v_700"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KAPX_T_500"]] = APX_T[APX_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KAPX_Td_500"]] = APX_Td[APX_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KAPX_z_500"]] = APX_z[APX_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KAPX_u_500"]] = APX_u[APX_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KAPX_v_500"]] = APX_v[APX_P.index(500)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KAPX_T_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_Td_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_z_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_u_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KAPX_v_500"]] = "null_data"
                        
                else:
                    data.loc[[f"{d_ind}"], ["KAPX_LI"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_T_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_Td_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_u_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_v_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_P_SFC"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_P_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_T_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_LCL"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_T_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_Td_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_u_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_v_925"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_T_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_Td_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_u_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_v_850"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_T_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_Td_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_u_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_v_700"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KAPX_T_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_Td_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_z_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_u_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KAPX_v_500"]] = "null_data"

                
                KINL = GetINL(year, month, day)
                if KINL != None:
                    sKINL = KINL["pressure"].m > 90

                    INL_P = KINL["pressure"][sKINL].magnitude.tolist()
                    INL_T = KINL["temperature"][sKINL].magnitude.tolist()
                    INL_Td = KINL["dewpoint"][sKINL].magnitude.tolist()
                    INL_z = KINL["height"][sKINL].magnitude.tolist()
                    INL_u = KINL["u_wind"][sKINL].magnitude.tolist()
                    INL_v = KINL["u_wind"][sKINL].magnitude.tolist()

                    plain_INL_P = KINL["pressure"][sKINL].magnitude * units("hPa")
                    plain_INL_T = KINL["temperature"][sKINL].magnitude * units("degC")

                    try:
                        INL_parcel = mpcalc.parcel_profile(INL_P * units("hPa"), (INL_T[0] * units("degC")), (INL_Td[0] * units("degC"))).to("degC")
                        data.loc[[f"{d_ind}"], ["KINL_LI"]] = mpcalc.lifted_index(INL_P * units("hPa"), INL_T * units("degC"), INL_parcel)
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_LI"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KINL_T_SFC"]] = INL_T[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_T_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KINL_Td_SFC"]] = INL_Td[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_Td_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KINL_z_SFC"]] = INL_z[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_z_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KINL_u_SFC"]] = INL_u[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_u_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KINL_v_SFC"]] = INL_v[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_v_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["KINL_P_SFC"]] = INL_P[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_P_SFC"]] = "null_data"

                    try:
                        INL_P_LCL, INL_T_LCL = mpcalc.lcl(INL_P[0] * units("hPa"), INL_T[0] * units("degC"), INL_Td[0] * units("degC"))
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["KINL_P_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_T_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_z_LCL"]] = "null_data"
                    else:
                        data.loc[[f"{d_ind}"], ["KINL_P_LCL"]] = INL_P_LCL
                        data.loc[[f"{d_ind}"], ["KINL_T_LCL"]] = INL_T_LCL
                        mod_INL_P = np.append(plain_INL_P[plain_INL_P > INL_P_LCL], INL_P_LCL)
                        mod_INL_T = np.append(plain_INL_T[plain_INL_P > INL_P_LCL], INL_T_LCL)
                        data.loc[[f"{d_ind}"], ["KINL_z_LCL"]] = mpcalc.thickness_hydrostatic(mod_INL_P, mod_INL_T)

                    try:
                        data.loc[[f"{d_ind}"], ["KINL_T_925"]] = INL_T[INL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KINL_Td_925"]] = INL_Td[INL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KINL_z_925"]] = INL_z[INL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KINL_u_925"]] = INL_u[INL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["KINL_v_925"]] = INL_v[INL_P.index(925)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KINL_T_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_Td_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_z_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_u_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_v_925"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KINL_T_850"]] = INL_T[INL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KINL_Td_850"]] = INL_Td[INL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KINL_z_850"]] = INL_z[INL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KINL_u_850"]] = INL_u[INL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["KINL_v_850"]] = INL_v[INL_P.index(850)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KINL_T_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_Td_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_z_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_u_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_v_850"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KINL_T_700"]] = INL_T[INL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KINL_Td_700"]] = INL_Td[INL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KINL_z_700"]] = INL_z[INL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KINL_u_700"]] = INL_u[INL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["KINL_v_700"]] = INL_v[INL_P.index(700)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KINL_T_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_Td_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_z_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_u_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_v_700"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["KINL_T_500"]] = INL_T[INL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KINL_Td_500"]] = INL_Td[INL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KINL_z_500"]] = INL_z[INL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KINL_u_500"]] = INL_u[INL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["KINL_v_500"]] = INL_v[INL_P.index(500)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["KINL_T_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_Td_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_z_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_u_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["KINL_v_500"]] = "null_data"
                        
                else:
                    data.loc[[f"{d_ind}"], ["KINL_LI"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_T_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_Td_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_u_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_v_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_P_SFC"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_P_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_T_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_LCL"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_T_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_Td_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_u_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_v_925"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_T_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_Td_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_u_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_v_850"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_T_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_Td_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_u_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_v_700"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["KINL_T_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_Td_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_z_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_u_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["KINL_v_500"]] = "null_data"
                    
                CWPL = GetWPL(year, month, day)
                if CWPL != None:
                    sCWPL = CWPL["pressure"].m > 90
    
                    WPL_P = CWPL["pressure"][sCWPL].magnitude.tolist()
                    WPL_T = CWPL["temperature"][sCWPL].magnitude.tolist()
                    WPL_Td = CWPL["dewpoint"][sCWPL].magnitude.tolist()
                    WPL_z = CWPL["height"][sCWPL].magnitude.tolist()
                    WPL_u = CWPL["u_wind"][sCWPL].magnitude.tolist()
                    WPL_v = CWPL["u_wind"][sCWPL].magnitude.tolist()

                    plain_WPL_P = CWPL["pressure"][sCWPL].magnitude * units("hPa")
                    plain_WPL_T = CWPL["temperature"][sCWPL].magnitude * units("degC")
                    
                    try:
                        WPL_parcel = mpcalc.parcel_profile(WPL_P * units("hPa"), (WPL_T[0] * units("degC")), (WPL_Td[0] * units("degC"))).to("degC")
                        data.loc[[f"{d_ind}"], ["CWPL_LI"]] = mpcalc.lifted_index(WPL_P * units("hPa"), WPL_T * units("degC"), WPL_parcel)
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_LI"]] = "null_data"
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["CWPL_LI"]] = "null_data"
    
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_T_SFC"]] = WPL_T[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_T_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_Td_SFC"]] = WPL_Td[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_Td_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_z_SFC"]] = WPL_z[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_z_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_u_SFC"]] = WPL_u[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_u_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_v_SFC"]] = WPL_v[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_v_SFC"]] = "null_data"
                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_P_SFC"]] = WPL_P[0]
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_P_SFC"]] = "null_data"

                    try:
                        WPL_P_LCL, WPL_T_LCL = mpcalc.lcl(WPL_P[0] * units("hPa"), WPL_T[0] * units("degC"), WPL_Td[0] * units("degC"))
                    except IndexError:
                        data.loc[[f"{d_ind}"], ["CWPL_P_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_T_LCL"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_z_LCL"]] = "null_data"
                    else:
                        data.loc[[f"{d_ind}"], ["CWPL_P_LCL"]] = WPL_P_LCL
                        data.loc[[f"{d_ind}"], ["CWPL_T_LCL"]] = WPL_T_LCL
                        mod_WPL_P = np.append(plain_WPL_P[plain_WPL_P > WPL_P_LCL], WPL_P_LCL)
                        mod_WPL_T = np.append(plain_WPL_T[plain_WPL_P > WPL_P_LCL], WPL_T_LCL)
                        data.loc[[f"{d_ind}"], ["CWPL_z_LCL"]] = mpcalc.thickness_hydrostatic(mod_WPL_P, mod_WPL_T)

                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_T_925"]] = WPL_T[WPL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["CWPL_Td_925"]] = WPL_Td[WPL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["CWPL_z_925"]] = WPL_z[WPL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["CWPL_u_925"]] = WPL_u[WPL_P.index(925)]
                        data.loc[[f"{d_ind}"], ["CWPL_v_925"]] = WPL_v[WPL_P.index(925)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["CWPL_T_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_Td_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_z_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_u_925"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_v_925"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_T_850"]] = WPL_T[WPL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["CWPL_Td_850"]] = WPL_Td[WPL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["CWPL_z_850"]] = WPL_z[WPL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["CWPL_u_850"]] = WPL_u[WPL_P.index(850)]
                        data.loc[[f"{d_ind}"], ["CWPL_v_850"]] = WPL_v[WPL_P.index(850)]
                    except ValueError:
                        data.loc[[f"{d_ind}"], ["CWPL_T_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_Td_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_z_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_u_850"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_v_850"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_T_700"]] = WPL_T[WPL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["CWPL_Td_700"]] = WPL_Td[WPL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["CWPL_z_700"]] = WPL_z[WPL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["CWPL_u_700"]] = WPL_u[WPL_P.index(700)]
                        data.loc[[f"{d_ind}"], ["CWPL_v_700"]] = WPL_v[WPL_P.index(700)]
                    except:
                        data.loc[[f"{d_ind}"], ["CWPL_T_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_Td_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_z_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_u_700"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_v_700"]] = "null_data"

                    try:
                        data.loc[[f"{d_ind}"], ["CWPL_T_500"]] = WPL_T[WPL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["CWPL_Td_500"]] = WPL_Td[WPL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["CWPL_z_500"]] = WPL_z[WPL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["CWPL_u_500"]] = WPL_u[WPL_P.index(500)]
                        data.loc[[f"{d_ind}"], ["CWPL_v_500"]] = WPL_v[WPL_P.index(500)]
                    except:
                        data.loc[[f"{d_ind}"], ["CWPL_T_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_Td_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_z_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_u_500"]] = "null_data"
                        data.loc[[f"{d_ind}"], ["CWPL_v_500"]] = "null_data"
                
                else:
                    data.loc[[f"{d_ind}"], ["CWPL_LI"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_T_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_Td_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_u_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_v_SFC"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_P_SFC"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_P_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_T_LCL"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_LCL"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_T_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_Td_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_u_925"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_v_925"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_T_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_Td_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_u_850"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_v_850"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_T_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_Td_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_u_700"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_v_700"]] = "null_data"
    
                    data.loc[[f"{d_ind}"], ["CWPL_T_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_Td_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_z_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_u_500"]] = "null_data"
                    data.loc[[f"{d_ind}"], ["CWPL_v_500"]] = "null_data"

                data.to_csv("/scratch/sbailey4/LocalData/LSSnow_dat.csv")
                print(f"(AMGP_SCAL) <run> Calculations completed for {month}/{day}/{year} at {datetime.utcnow()}.")
    except AttributeError:
            amgp.ThrowError("AMGP_SCAL", 0, "Attempted to apply STLP data without providing a dataset.", True, False, True)

def GetGRB(year, month, day):
    def FetchGRB(year, month, day):
        try:
            GRB = pandas_dataframe_to_unit_arrays(WyomingUpperAir.request_data(datetime(year=year, month=month, day=day, hour=0), "GRB"))
        except ValueError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Green Bay sounding data unavailable for {year}-{month}-{day}.", True, False, False)
            GRB = None
        except HTTPError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Green Bay sounding data for {year}-{month}-{day} unsuccessful. Retrying.", True, False, False)
            sleep(1)
            GRB = FetchGRB(year, month, day)
        except IndexError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Green Bay did the weird thing on {year}-{month}-{day}.", True, False, True)
            GRB = None
        return GRB
    return FetchGRB(year, month, day)


def GetAPX(year, month, day):
    def FetchAPX(year, month, day):
        try:
            APX = pandas_dataframe_to_unit_arrays(WyomingUpperAir.request_data(datetime(year=year, month=month, day=day, hour=0), "APX"))
        except ValueError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Gaylord sounding data unavailable for {year}-{month}-{day}.", True, False, False)
            APX = None
        except HTTPError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Gaylord sounding data for {year}-{month}-{day} unsuccessful. Retrying.", True, False, False)
            sleep(1)
            APX = FetchAPX(year, month, day)
        except IndexError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Gaylord did the weird thing on {year}-{month}-{day}.", True, False, True)
            APX = None
        return APX
    return FetchAPX(year, month, day)


def GetINL(year, month, day):
    def FetchINL(year, month, day):
        try:
            INL = pandas_dataframe_to_unit_arrays(WyomingUpperAir.request_data(datetime(year=year, month=month, day=day, hour=0), "INL"))
        except ValueError:
            amgp.ThrowError("AMGP_SCAL", 2, f"International Falls sounding data unavailable for {year}-{month}-{day}.", True, False, False)
            INL = None
        except HTTPError:
            amgp.ThrowError("AMGP_SCAL", 2, f"International Falls sounding data for {year}-{month}-{day} unsuccessful. Retrying.", True, False, False)
            sleep(1)
            INL = FetchINL(year, month, day)
        except IndexError:
            amgp.ThrowError("AMGP_SCAL", 2, f"International Falls did the weird thing on {year}-{month}-{day}.", True, False, True)
            INL = None
        return INL
    return FetchINL(year, month, day)


def GetWPL(year, month, day):
    def FetchWPL(year, month, day):
        try:
            WPL = pandas_dataframe_to_unit_arrays(WyomingUpperAir.request_data(datetime(year=year, month=month, day=day, hour=0), "WPL"))
        except ValueError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Pebble Lake sounding data unavailable for {year}-{month}-{day}.", True, False, False)
            WPL = None
        except HTTPError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Pebble Lake sounding data for {year}-{month}-{day} unsuccessful. Retrying.", True, False, False)
            sleep(1)
            WPL = FetchWPL(year, month, day)
        except IndexError:
            amgp.ThrowError("AMGP_SCAL", 2, f"Pebble Lake did the weird thing on {year}-{month}-{day}.", True, False, True)
            WPL = None
        return WPL
    return FetchWPL(year, month, day)