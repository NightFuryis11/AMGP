################################################
#                                              #
#       Automated Map Generation Program       #
#         Convective Outlooks Module           #
#            Author: Sam Bailey                #
#        Last Revised: Aug 25, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.4.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

import geopandas as gpd
from datetime import datetime, timedelta
from metpy.plots import PlotGeometry
from urllib.request import urlopen

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_CONV",
            'uid':"00910900"}

# Day1 at 0100, 1200, 1300, 1630, 2000
# Day2 at 0600, 1730
# Day3 at 0730

def getFactors():
    return {'day1':[9,0],
            'day2':[10,0],
            'day3':[11,0],
            'day4':[12,0],
            'day5':[12,0],
            'day6':[12,0],
            'day7':[12,0],
            'day8':[12,0],
            'conv_fill':[-1,1]}

def factors():
    print("(AMGP_CONV) <factors_conv> 'day1' - The Categorical Outlook for day 1 issued on the given date. Issued at 0100Z, 1200Z, 1300Z, 1630Z, and 2000Z")
    print("(AMGP_CONV) <factors_conv> 'day2' - The Categorical Outlook for day 2 issued on the given date. Issued at 0600Z and 1730Z")
    print("(AMGP_CONV) <factors_conv> 'day3' - The Categorical Outlook for day 3 issued on the given date. Issued at 0730Z")
    print("(AMGP_CONV) <factors_conv> 'day#' - The Probabalistic Outlook for day 4 to 8 issued on the given date. Issued around 9Z")
    print("(AMGP_CONV) <factors_conv> 'conv_fill' - A modifier on any convective product that will fill the area with color, instead of leaving it hollow.")
    
def ping(Time):
    
    tDay = Time - timedelta(days=1)
    
    try:
        with urlopen(f'https://www.spc.noaa.gov/products') as conn:
            print("(AMGP_CONV) <ping> NOAA Convective Outlooks are online")
    except:
        print("(AMGP_CONV) <ping> NOAA Convective Outlooks are offline; this effects the following Factors: 'day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7', 'day8', and 'conv_fill'")

def Retrieve(Time, factors, values, LocalData=None):
    
    partialPlotsList = []
    
    if 'day1' in factors:
        d1conv = PlotGeometry()
        d1otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/outlook/archive/{Time.c1time:%Y}/day1otlk_{Time.c1time:%Y%m%d}_{Time.c1time:%H%M}_cat.lyr.geojson')
        d1conv.geometry = d1otlk['geometry']
        if 'conv_fill' in factors:
            d1conv.fill = d1otlk['fill']
        else:
            d1conv.fill = None
        d1conv.stroke = d1otlk['stroke']
        d1conv.labels = d1otlk['LABEL']
        d1conv.label_fontsize = 'large'
        partialPlotsList.append(d1conv)
        
    if 'day2' in factors:
        d2conv = PlotGeometry()
        d2otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/outlook/archive/{Time.c2time:%Y}/day2otlk_{Time.c2time:%Y%m%d}_{Time.c2time:%H%M}_cat.lyr.geojson')
        d2conv.geometry = d2otlk['geometry']
        if 'conv_fill' in factors:
            d2conv.fill = d2otlk['fill']
        else:
            d2conv.fill = None
        d2conv.stroke = d2otlk['stroke']
        d2conv.labels = d2otlk['LABEL']
        d2conv.label_fontsize = 'large'
        partialPlotsList.append(d2conv)
        
    if 'day3' in factors:
        d3conv = PlotGeometry()
        d3otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/outlook/archive/{Time.c3time:%Y}/day3otlk_{Time.c3time:%Y%m%d}_{Time.c3time:%H%M}_cat.lyr.geojson')
        d3conv.geometry = d3otlk['geometry']
        if 'conv_fill' in factors:
            d3conv.fill = d3otlk['fill']
        else:
            d3conv.fill = None
        d3conv.stroke = d3otlk['stroke']
        d3conv.labels = d3otlk['LABEL']
        d3conv.label_fontsize = 'large'
        partialPlotsList.append(d3conv)
        
    if 'day4' in factors:
        d4prob = PlotGeometry()
        d4otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/exper/day4-8/archive/{Time.ptime:%Y}/day4prob_{Time.ptime:%Y%m%d}.lyr.geojson')
        d4prob.geometry = d4otlk['geometry']
        if 'conv_fill' in factors:
            d4prob.fill = d4otlk['fill']
        else:
            d4prob.fill = None
        d4prob.stroke = d4otlk['stroke']
        d4prob.labels = d4otlk['LABEL']
        d4prob.label_fontsize = 'large'
        partialPlotsList.append(d4prob)
    
    if 'day5' in factors:
        d5prob = PlotGeometry()
        d5otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/exper/day4-8/archive/{Time.ptime:%Y}/day5prob_{Time.ptime:%Y%m%d}.lyr.geojson')
        d5prob.geometry = d5otlk['geometry']
        if 'conv_fill' in factors:
            d5prob.fill = d5otlk['fill']
        else:
            d5prob.fill = None
        d5prob.stroke = d5otlk['stroke']
        d5prob.labels = d5otlk['LABEL']
        d5prob.label_fontsize = 'large'
        partialPlotsList.append(d5prob)
    
    if 'day6' in factors:
        d6prob = PlotGeometry()
        d6otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/exper/day4-8/archive/{Time.ptime:%Y}/day6prob_{Time.ptime:%Y%m%d}.lyr.geojson')
        d6prob.geometry = d6otlk['geometry']
        if 'conv_fill' in factors:
            d6prob.fill = d6otlk['fill']
        else:
            d6prob.fill = None
        d6prob.stroke = d6otlk['stroke']
        d6prob.labels = d6otlk['LABEL']
        d6prob.label_fontsize = 'large'
        partialPlotsList.append(d6prob)
        
    if 'day7' in factors:
        d7prob = PlotGeometry()
        d7otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/exper/day4-8/archive/{Time.ptime:%Y}/day7prob_{Time.ptime:%Y%m%d}.lyr.geojson')
        d7prob.geometry = d7otlk['geometry']
        if 'conv_fill' in factors:
            d7prob.fill = d7otlk['fill']
        else:
            d7prob.fill = None
        d7prob.stroke = d7otlk['stroke']
        d7prob.labels = d7otlk['LABEL']
        d7prob.label_fontsize = 'large'
        partialPlotsList.append(d7prob)
        
    if 'day8' in factors:
        d8prob = PlotGeometry()
        d8otlk = gpd.read_file(f'https://www.spc.noaa.gov/products/exper/day4-8/archive/{Time.ptime:%Y}/day8prob_{Time.ptime:%Y%m%d}.lyr.geojson')
        d8prob.geometry = d8otlk['geometry']
        if 'conv_fill' in factors:
            d8prob.fill = d8otlk['fill']
        else:
            d8prob.fill = None
        d8prob.stroke = d8otlk['stroke']
        d8prob.labels = d8otlk['LABEL']
        d8prob.label_fontsize = 'large'
        partialPlotsList.append(d8prob)
    
    return partialPlotsList