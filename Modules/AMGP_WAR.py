################################################
#                                              #
#       Automated Map Generation Program       #
#        Warnings and Reports Module           #
#            Author: Sam Bailey                #
#        Last Revised: Aug 13, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

import geopandas as gpd
from metpy.plots import PlotGeometry
from datetime import timedelta
from urllib.request import urlopen

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_WAR",
            'uid':"00710700"}

def getFactors():
    return {'warnings':[13,0],
            'torwarnings':[13,0],
            'svrwarnings':[13,0],
            'marwarnings':[13,0],
            'flowarnings':[13,0],
            'watches':[14,0],
            'svrwarnings':[14,0],
            'torwarnings':[14,0],
            'reports':[15,0],
            'hailreports':[15,0],
            'torreports':[15,0]}

def factors():
    print("(AMGP_WAR) <factors_war> 'warnings' - Active NWS tornado, severe thunderstorm, special marine, and flood warnings at the given time.")
    print("(AMGP_WAR) <factors_war> 'torwarnings' - Active NWS tornado warnings at the given time.")
    print("(AMGP_WAR) <factors_war> 'svrwarnings' - Active NWS severe thunderstorm warnings at the given time.")
    print("(AMGP_WAR) <factors_war> 'marwarnings' - Active NWS special marine warnings at the given time.")
    print("(AMGP_WAR) <factors_war> 'flowarnings' - Active NWS flood warnings at the given time.")
    print("(AMGP_WAR) <factors_war> 'watches' - Active NWS tornado and severe thunderstorm watches at the given time.")
    print("(AMGP_WAR) <factors_war> 'svrwatches' - Active NWS severe thunderstorm watches at the given time.")
    print("(AMGP_WAR) <factors_war> 'torwatches' - Active NWS tornado watches at the given time.")
    print("(AMGP_WAR) <factors_war> 'reports' - Local storm reports for within 15 minutes of the given time.")
    print("(AMGP_WAR) <factors_war> 'hailreports' - Local hail reports for within 15 minutes of the given time.")
    print("(AMGP_WAR) <factors_war> 'torreports' - Local tornado reports for within 15 minutes of the given time.")
    
def ping(Time):
    try:
        with urlopen('https://mesonet.agron.iastate.edu/geojson') as conn:
            print("(AMGP_WAR) <ping> Iowa State Mesonet geojson is online")
    except:
        print("(AMGP_WAR) <ping> Iowa State Mesonet geojson is offline; this effects the following Factors: 'warnings', 'torwarnings', 'svrwarnings', 'marwarnings', 'flowarnings', 'watches', 'svrwatches', 'torwatches', 'reports', 'hailreports', and 'torreports'")

def Retrieve(Time, factors, values, ReformLD=None):
    
    partialPlotsList = []
    if ('warnings' in factors) or ('torwarnings' in factors) or ('svrwarnings' in factors) or ('flowarnings' in factors):
        try:
            try:
                a = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
            except:
                a = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
            a = a.loc[a['phenomena'] == "TO"]

            if ('warnings' in factors) or ('torwarnings' in factors):
                torwarn = PlotGeometry()
                try:
                    torwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
                except:
                    torwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
                torwarnings = torwarnings.loc[torwarnings['phenomena'] == "TO"]
                torwarn.geometry = torwarnings['geometry']
                torwarn.fill = None
                torwarn.stroke = "red"
                partialPlotsList.append(torwarn)

            if ('warnings' in factors) or ('svrwarnings' in factors):
                svrwarn = PlotGeometry()
                try:
                    svrwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
                except:
                    svrwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
                svrwarnings = svrwarnings.loc[svrwarnings['phenomena'] == "SV"]
                svrwarn.geometry = svrwarnings['geometry']
                svrwarn.fill = None
                svrwarn.stroke = "gold"
                partialPlotsList.append(svrwarn)

            if ('warnings' in factors) or ('marwarnings' in factors):
                marwarn = PlotGeometry()
                try:
                    marwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
                except:
                    marwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
                marwarnings = marwarnings.loc[marwarnings['phenomena'] == "MA"]
                marwarn.geometry = marwarnings['geometry']
                marwarn.fill = None
                marwarn.stroke = "orange"
                partialPlotsList.append(marwarn)

            if ('warnings' in factors) or ('flowarnings' in factors):
                flwarn = PlotGeometry()
                try:
                    flwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
                except:
                    flwarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
                flwarnings = flwarnings.loc[flwarnings['phenomena'] == "FL"].loc[flwarnings['significance'] == "W"]
                flwarn.geometry = flwarnings['geometry']
                flwarn.fill = None
                flwarn.stroke = "green"
                partialPlotsList.append(flwarn)

                flawarn = PlotGeometry()
                try:
                    flawarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.time:%Y}-{Time.time:%m}-{Time.time:%d}T{Time.time:%H}:{Time.time:%M}:{Time.time:%S}Z")
                except:
                    flawarnings = gpd.read_file(f"https://mesonet.agron.iastate.edu/geojson/sbw.geojson?ts={Time.zerotime:%Y}-{Time.zerotime:%m}-{Time.zerotime:%d}T{Time.zerotime:%H}:{Time.zerotime:%M}:{Time.zerotime:%S}Z")
                flawarnings = flawarnings.loc[flawarnings['phenomena'] == "FL"].loc[flawarnings['significance'] == "A"]
                flawarn.geometry = flawarnings['geometry']
                flawarn.fill = None
                flawarn.stroke = "lime"
                partialPlotsList.append(flawarn)
        except:
            print("(AMGP_WAR) <warning> Warnings are not available for this time!")
            
    if ('watches' in factors) or ('torwatches' in factors) or ('svrwatches' in factors):
        try:
            try:
                b = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.time:%Y%m%d%H%M}')
            except:
                b = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.zerotime:%Y%m%d%H%M}')
            b = b.loc[b['type'] == "SVR"]

            if ("watches" in factors) or ("svrwatches" in factors):
                svwat = PlotGeometry()
                try:
                    svwatches = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.time:%Y%m%d%H%M}')
                except:
                    svwatches = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.zerotime:%Y%m%d%H%M}')
                svwatches = svwatches.loc[svwatches['type'] == "SVR"]
                svwat.geometry = svwatches['geometry']
                svwat.fill = None
                svwat.stroke = "lightpink"
                partialPlotsList.append(svwat)

            if ("watches" in factors) or ("torwatches" in factors):
                towat = PlotGeometry()
                try:
                    towatches = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.time:%Y%m%d%H%M}')
                except:
                    towatches = gpd.read_file(f'http://mesonet.agron.iastate.edu/json/spcwatch.py?ts={Time.zerotime:%Y%m%d%H%M}')
                towatches = towatches.loc[towatches['type'] == "TOR"]
                towat.geometry = towatches['geometry']
                towat.fill = None
                towat.stroke = "yellow"
                partialPlotsList.append(towat)
        except:
            print("(AMGP_WAR) <warning> Watches are not available for this time!")
    
    if ('reports' in factors) or ('torreports' in factors) or ('hailreports' in factors):
        try:
            try:
                c = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.time-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.time+timedelta(minutes=15)):%Y%m%d%H%M}&wfos=')
            except:
                c = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.zerotime-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.zerotime):%Y%m%d%H%M}&wfos=')
            c = c.loc[c['type'] == "T"]

            if ("reports" in factors) or ("hailreports" in factors):
                harep = PlotGeometry()
                try:
                    hareps = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.time-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.time):%Y%m%d%H%M}&wfos=')
                except:
                    hareps = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.zerotime-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.zerotime):%Y%m%d%H%M}&wfos=')
                hareps = hareps.loc[hareps['type'] == "H"]
                harep.geometry = hareps['geometry']
                harep.fill = "blue"
                partialPlotsList.append(harep)

            if ("reports" in factors) or ("torreports" in factors):
                torep = PlotGeometry()
                try:
                    toreps = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.time-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.time):%Y%m%d%H%M}&wfos=')
                except:
                    toreps = gpd.read_file(f'http://mesonet.agron.iastate.edu/geojson/lsr.php?sts={(Time.zerotime-timedelta(minutes=15)):%Y%m%d%H%M}&ets={(Time.zerotime):%Y%m%d%H%M}&wfos=')
                toreps = toreps.loc[toreps['type'] == "T"]
                torep.geometry = toreps['geometry']
                torep.fill = "red"
                partialPlotsList.append(torep)
        except:
            print("(AMGP_WAR) <warning> Reports are not available for this time!")
    
    return partialPlotsList