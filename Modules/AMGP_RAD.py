################################################
#                                              #
#       Automated Map Generation Program       #
#                Radar Module                  #
#            Author: Sam Bailey                #
#        Last Revised: Aug 13, 2023            #
#                Version 0.1.0                 #
#             AMGP Version: 0.3.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################



#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

def info():
    return {'name':"AMGP_RAD",
            'uid':"00810800"}

def getFactors():
    return {'radar':[14,1]}

def factors():
    print("(AMGP_RAD) <factors_rad> 'radar' - NEXRAD mosaic for the United States")
    
def ping(Time):
    return None

def Retrieve(Time, factors, values):
    
    partialplotslist = []