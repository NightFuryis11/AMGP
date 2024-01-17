################################################
#                                              #
#       Automated Map Generation Program       #
#            Mean-Anomaly Module               #
#            Author: Sam Bailey                #
#        Last Revised: Aug 13, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################



#----------------- AMGP IMPORTS -------------------#

from Modules import AMGP_MAP as amgpmap
from Modules import AMGP_UTIL as amgp
from Modules import AMGP_PLT as amgpplt

#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_ANOM",
            'uid':"01331300"}

def getFactors():
    return {}

def factors():
    return "Blank"

def init(pack):
    print("(AMGP_ANOM) <warning> The Anomaly Module is not yet available for use, please try again later.")
    amgpplt.init(pack)