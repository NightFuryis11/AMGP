################################################
#                                              #
#      Automated Map Generation Program        #
#           Satelite Data Module               #
#            Author: Sam Bailey                #
#        Last Revised: Aug 13, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from siphon.catalog import TDSCatalog
import numpy as np
import os
from metpy.plots import declarative
import xarray as xr
from datetime import datetime
from urllib.request import urlopen

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_SAT",
            'uid':"01111100"}

def getFactors():
    return {'sat_channel_2':[8,1],
            'sat_channel_9':[8,1],
            'sat_channel_14':[8,1],
            'sat_truecolor':[8,1],
            'sat_west':[-1,1]}

def factors():
    print("(AMGP_SAT) <factors_sat> 'sat_west' - Switches all satelite data to GOES West instead of GOES East")
    print("(AMGP_SAT) <factors_sat> 'sat_channel_2' - Visible satelite data")
    print("(AMGP_SAT) <factors_sat> 'sat_channel_9' - Water vapor satelite data")
    print("(AMGP_SAT) <factors_sat> 'sat_channel_14' - Infrared satelite data")
    print("(AMGP_SAT) <factors_sat> 'sat_truecolor' - Simulated true-color satelite data")
    
def ping(Time):
    try:
        with urlopen('https://thredds.ucar.edu/thredds/catalog/satellite/goes/east/products/CloudAndMoistureImagery') as conn:
            print("(AMGP_SAT) <ping> GOES East is online")
    except:
        print("(AMGP_SAT) <ping> GOES East is offline; this effects the following Factors: 'sat_channel_2', 'sat_channel_9', 'sat_channel_14', and 'sat_truecolor'")

    try:
        with urlopen('https://thredds.ucar.edu/thredds/catalog/satellite/goes/west/products/CloudAndMoistureImagery') as conn:
            print("(AMGP_SAT) <ping> GOES West is online")
    except:
        print("(AMGP_SAT) <ping> GOES West is offline; this effects the following Factors: 'sat_channel_2', 'sat_channel_9', 'sat_channel_14', and 'sat_truecolor' when 'sat_west' is true")

def Retrieve(Time, factors, values, LocalData=None):
    
    partialPlotsList = []

    sat_sel = 'east'

    if "sat_west" in factors:
        sat_sel = 'west'
    
    if "sat_channel_2" in factors:
        sat_dat_2 = FetchData(sat_sel, 2, Time,'CONUS').dat
        sat_img = declarative.ImagePlot()
        sat_img.data = sat_dat_2
        sat_img.field = "Sectorized_CMI"
        sat_img.colormap = 'Greys_r'
        partialPlotsList.append(sat_img)
        
    if "sat_channel_9" in factors:
        sat_dat_9 = FetchData(sat_sel, 9, Time,'CONUS').dat
        sat_img = declarative.ImagePlot()
        sat_img.data = sat_dat_9
        sat_img.field = "Sectorized_CMI"
        sat_img.colorbar = 'horizontal'
        sat_img.colormap = 'WVCIMSS_r'
        sat_img.image_range = (200, 280)
        partialPlotsList.append(sat_img)
        
    if "sat_channel_14" in factors:
        sat_dat_14 = FetchData(sat_sel, 14, Time,'CONUS').dat
        sat_img = declarative.ImagePlot()
        sat_img.data = sat_dat_14
        sat_img.field = "Sectorized_CMI"
        sat_img.colorbar = 'horizontal'
        sat_img.colormap = 'ir_drgb_r'
        partialPlotsList.append(sat_img)
        
    if "sat_truecolor" in factors:
        sat_trc = MakeTruecolorSat(FetchData(sat_sel, 1, Time,'CONUS'), FetchData(sat_sel, 2, Time,'CONUS'), FetchData(sat_sel, 3, Time,'CONUS'))
        sat_imgtrc = declarative.ImagePlot()
        sat_imgtrc.data = sat_trc.dat
        sat_imgtrc.field = "truecolor"
        partialPlotsList.append(sat_imgtrc)
    
    return partialPlotsList

class Data(object):
    def __init__(self, sat, channel, Time, sector):
        
        if (Time.category == 'sync') or (Time.category == 'raw') or (Time.category == 'near'):
            time = Time.time
        else:
            time = Time.onetime
        
        catalog = TDSCatalog(f'https://thredds.ucar.edu/thredds/catalog/satellite/goes/{sat}/products/CloudAndMoistureImagery/{sector}/Channel{channel:02d}/{time:%Y%m%d}/catalog.xml')
        sateliteFormatHour = time.strftime('%Y%j%H')
        files = []
        times = []
        for file in catalog.datasets:
            if sateliteFormatHour in file:
                times.append(datetime.strptime(file.split('_')[3][1:-3], '%Y%j%H%M'))
                files.append(file)
        fileSearch = np.abs(np.array(times) - time)
        index = list(catalog.datasets).index(files[np.argmin(fileSearch)])
        self.dat = catalog.datasets[index].remote_access(use_xarray=True)
        if channel == 2:
            self.dat['Sectorized_CMI'].values = np.sqrt(self.dat['Sectorized_CMI'].values)
        self.dtm = self.dat.time.values.astype('datetime64[ms]').astype('O')
        
        #print(self.dat.keys())
    
def FetchData(sat, channel, Time, sector):
    return Data(sat, channel, Time, sector)

class TruecolorSat(object):
    def __init__(self, B, R, Veg):
        B_dat = np.power(np.clip(B.dat["Sectorized_CMI"].data, 0, 1), 1/2.2)
        R_dat = np.power(np.clip(R.dat["Sectorized_CMI"].data[::2,::2], 0, 1), 1/2.2)
        Veg_dat = np.power(np.clip(Veg.dat["Sectorized_CMI"].data, 0, 1), 1/2.2)
        
        G_dat = (R_dat * 0.45) + (Veg_dat * 0.1) + (B_dat * 0.45)
        G_dat = np.clip(G_dat, 0, 1)
        
        TrueGreen = B
        RGB = np.dstack([R_dat, G_dat, B_dat])
        TrueGreen.dat["truecolor"] = xr.DataArray(RGB, coords=[TrueGreen.dat.y, TrueGreen.dat.x, [2, 1, 3]], dims=['y', 'x', 'channel'])
        TrueGreen.dat.truecolor.attrs = B.dat.Sectorized_CMI.attrs
        self.dat = TrueGreen.dat
        self.dtm = TrueGreen.dtm
        
def MakeTruecolorSat(B, R, Veg):
    return TruecolorSat(B, R, Veg)
