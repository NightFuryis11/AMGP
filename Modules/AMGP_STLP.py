################################################
#                                              #
#       Automated Map Generation Program       #
#            Skew-T Log-P Module               #
#            Author: Sam Bailey                #
#        Last Revised: May 09, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.plots import SkewT, Hodograph
from metpy.units import units, pandas_dataframe_to_unit_arrays
import numpy as np
from siphon.simplewebservice.wyoming import WyomingUpperAir

#----------------- AMGP IMPORTS -------------------#

from Modules import AMGP_MAP as amgpmap
from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_STLP",
            'uid':"01231200"}

def init(pack):
    print("(AMGP_STLP) <menu_init> Opened the Skew-T Log-P interface <menu_init>")
    global unpack
    unpack = pack
    amgp.getTime()
    loop()
        
def loop():
    global loaded
    loaded = {}
    loaded['date'] = input("date: ")
    loaded['station'] = input("station :")
    data(loaded, unpack['ver'])

def load(preset):
    global loaded
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Presets")
    with open(f"{dr}/stlp/{preset}.json", "r") as J:
        lo = json.load(J)
        loaded = lo["settings"]

def loadings():
    print(f"<loaded> Date: {loaded['date']}")
    print(f"<loaded> Factors: {loaded['factors']}")
    print(f"<loaded> Station: {loaded['station']}")

def data(loaded, version):
    Time = amgp.ParseTime(loaded['date'],[16],datetime.utcnow(),'raw','recent')
    dat = WyomingUpperAir.request_data(Time.time, loaded['station'])
    data = pandas_dataframe_to_unit_arrays(dat)
    sub = data['pressure'].m > 90
    p = data['pressure'][sub]
    T = data['temperature'][sub]
    Td = data['dewpoint'][sub]
    u = data['u_wind'][sub]
    v = data['v_wind'][sub]
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    cape, cin = mpcalc.cape_cin(p, T, Td, prof)
    ip500 = list(p.m).index(500)
    LI = T[ip500] - prof[ip500]
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(3, 3)
    skew = SkewT(fig, rotation=45, subplot=gs[:, :2])
    skew.plot(p, T, 'r')
    skew.plot(p, Td, 'g')
    skew.plot_barbs(p[::2], u[::2], v[::2], y_clip_radius=0.03)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-40, 50)
    skew.plot(p, prof, 'k', linewidth=2)
    skew.plot(lcl_pressure, lcl_temperature, '_', color='black', markersize=24, markeredgewidth=3, markerfacecolor='black')
    skew.plot_dry_adiabats(t0=np.arange(233,555,10)*units.K)
    skew.plot_moist_adiabats(colors='tab:green')
    skew.plot_mixing_lines(colors='tab:blue')
    ax = fig.add_subplot(gs[0, -1])
    h = Hodograph(ax, component_range=60.)
    h.add_grid(increment=20)
    wind_speed = data['speed'].values * units.knots
    wind_dir = data['direction'].values * units.degrees
    u, v = mpcalc.wind_components(wind_speed, wind_dir)
    h.plot(u, v)
    plt.title(f'Station: K{station}', loc='left')
    plt.title('Skew-T/Log-p', loc='center')
    plt.title(f'{Time.time.ToString()} UTC', loc='right')
    plt.savefig('HW10-1.png', bbox_inches='tight', dpi=150)