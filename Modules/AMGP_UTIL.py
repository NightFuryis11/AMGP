################################################
#                                              #
#       Automated Map Generation Program       #
#             Utilities Module                 #
#            Author: Sam Bailey                #
#        Last Revised: Dec 05, 2023            #
#                Version 0.8.0                 #
#             AMGP Version: 0.4.0              #
#        AMGP Created on Mar 09, 2022          #
#                                              #
################################################

from datetime import datetime, timedelta
import math
import sys
import os
import contextlib
from PIL import Image as PImage
from PIL import ImageDraw, ImageFont, ImageFilter

#----------------- AMGP IMPORTS -------------------#



#------------------ END IMPORTS -------------------#

#--------------- START DEFINITIONS ----------------#

global runtime
runtime = datetime.utcnow()

def info():
    return {'name':"AMGP_UTIL",
            'uid':"00100400"}

class Time(object):
    def __init__(self, Date, plotType, currentTime, timeMode, convMode):
        
        timeFormat = None
        convFormat = None
        rec = False
        
        timeFormats = {0:[8], # Precise to the hour
                       1:[0, 1], # Precise to three hours - used by surface obs
                       2:[3, 4, 5, 6, 7], # Precise to six hours - used by gridded reanalysis data
                       3:[2, 16], # Precise to twelve hours - used by upper-air obs and Skew-Ts
                       4:[17], # Precise to twenty four hours
                       5:[9], # Convective outlook day 1
                       6:[10], # Convective outlook day 2
                       7:[11], # Convective outlook day 3
                       8:[12]} # Probabalistic outlooks days 4-8
                            # Satellite data is taken VERY frequently,
                            # and pulls the closest one to the time it's given,
                            # so it can use any of these time formats.
                            # However, it's default time format is 0, simply so that
                            # the rest of the code doesn't die horribly if sat
                            # data is the only data called for.
        
        for value in plotType:
            for i in range(0, 5):
                if value in timeFormats[i]:
                    timeFormat = i
        
        for value in plotType:
            for i in range(5, 9):
                if value in timeFormats[i]:
                    convFormat = i
        
        splitDate = Date.split(", ")
        if splitDate[0] == 'recent':
            givenTime = currentTime
        elif splitDate[0] == 'today':
            try:
                givenTime = datetime(currentTime.year, currentTime.month, currentTime.day, int(splitDate[1]), int(splitDate[2]))
            except:
                givenTime = datetime(currentTime.year, currentTime.month, currentTime.day, int(splitDate[1]))
        else:
            try:
                givenTime = datetime(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]), int(splitDate[3]), int(splitDate[4]))
            except:
                givenTime = datetime(int(splitDate[0]), int(splitDate[1]), int(splitDate[2]), int(splitDate[3]))
            
        recentness = currentTime - givenTime
        if recentness < timedelta(hours=3):
            flag = 1
            flag2 = 1
        elif recentness < timedelta(hours=6):
            flag = 0
            flag2 = 1
        else:
            flag = 0
            flag2 = 0
        
        if not rec:
            if (givenTime < datetime(1931, 1, 2)):
                ThrowError("AMGP_UTIL", 0, "The date you entered is out of range!", True, True, True)
            if (givenTime < datetime(1979, 1, 1)):
                ThrowError("AMGP_UTIL", 1, "The date you entered is out of range for gridded data.", True, False, False)
            if (givenTime < datetime(2003, 1, 23)):
                ThrowError("AMGP_UTIL", 1, "The date you entered is out of range for convective outlooks", True, False, False)
            if ((recentness) > timedelta(days=13)):
                ThrowError("AMGP_UTIL", 1, "The date you entered is out of range for satelite scans.", True, False, False)
        
        if (timeMode == 'raw') or (timeFormat == None):
            self.category = "raw"
            self.time = givenTime
            # This is basically only good for satelite data when "recent" is used.
        elif timeMode == 'async':
            self.zerotime = datetime(givenTime.year, givenTime.month, givenTime.day, givenTime.hour, givenTime.minute)
            self.onetime = datetime(givenTime.year, givenTime.month, givenTime.day, math.floor(givenTime.hour))
            for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                if givenTime.hour >= hour:
                    Hour = hour
                    self.threetime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            for hour in [18, 12, 6, 0]:
                if givenTime.hour >= hour + (6 * flag2):
                    Hour = hour
                    self.sixtime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            if (flag2 == 1) and (givenTime.hour < 6):
                Hour = 18
                self.sixtime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            for hour in [12, 0]:
                if givenTime.hour >= hour + (3 * flag):
                    Hour = hour
                    self.twelvetime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                    break
            if (flag == 1) and (givenTime.hour < 3):
                    Hour = 12
                    self.twelvetime = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            self.twentyfourtime = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
        elif timeMode == 'sync':
            self.category = "sync"
            Hour = 0
            if timeFormat == 4:
                self.time = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
            elif timeFormat == 3:
                for hour in [12, 0]:
                    if givenTime.hour >= hour + (3 * flag):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
                if (flag == 1) and (givenTime.hour < 3):
                    Hour = 12
                    self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            elif timeFormat == 2:
                for hour in [18, 12, 6, 0]:
                    if givenTime.hour >= hour + (6 * flag2):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
                if (flag2 == 1) and (givenTime.hour < 6):
                    Hour = 18
                    self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            elif timeFormat == 1:
                for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                    if givenTime.hour >= int(hour):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 0:
                self.time = datetime(givenTime.year, givenTime.month,givenTime.day, math.floor(givenTime.hour))
        elif timeMode == 'near':
            self.category = "near"
            Hour = 0
            if timeFormat == 0:
                self.time = datetime(givenTime.year, givenTime.month,givenTime.day, math.floor(givenTime.hour))
            elif timeFormat == 1:
                for hour in [21, 18, 15, 12, 9, 6, 3, 0]:
                    if givenTime.hour >= hour:
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 2:
                for hour in [18, 12, 6, 0]:
                    if givenTime.hour >= hour + (6 * flag2):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
                if givenTime.hour < 6:
                    Hour = 18
                    self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour) - timedelta(days=1)
            elif timeFormat == 3:
                for hour in [12, 0]:
                    if givenTime.hour >= hour + (3 * flag):
                        Hour = hour
                        self.time = datetime(givenTime.year, givenTime.month, givenTime.day, Hour)
                        break
            elif timeFormat == 4:
                self.time = datetime(givenTime.year, givenTime.month, givenTime.day, 0)
        
        if len(splitDate) == 5:
            self.minutes = splitDate[4]
        else:
            self.minutes = 0
        
        if timeMode == "async":
            self.ys = f"{self.onetime.year}"
            self.ms = f"{self.onetime.year}-{self.onetime.strftime('%m')}"
            self.ds = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}"
            self.tsnum = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}-{givenTime.strftime('%H%M')}Z"
            if timeFormat == 0:
                self.category = "async-1"
                self.tsalp = f"{self.onetime.strftime('%b')} {self.onetime.day}, {self.onetime.year} - {self.onetime.hour}Z to {givenTime.strftime('%b')} {givenTime.day}, {givenTime.year} - {givenTime.hour:02d}{givenTime.minute:02d}Z"
                self.recentness = currentTime - self.onetime
            elif timeFormat == 1:
                self.category = "async-3"
                self.tsalp = f"{self.threetime.strftime('%b')} {self.threetime.day}, {self.threetime.year} - {self.threetime.hour}Z to {givenTime.strftime('%b')} {givenTime.day}, {givenTime.year} - {givenTime.hour:02d}{givenTime.minute:02d}Z"
                self.recentness = currentTime - self.threetime
            elif timeFormat == 2:
                self.category = "async-6"
                self.tsalp = f"{self.sixtime.strftime('%b')} {self.sixtime.day}, {self.sixtime.year} - {self.sixtime.hour}Z to {givenTime.strftime('%b')} {givenTime.day}, {givenTime.year} - {givenTime.hour:02d}{givenTime.minute:02d}Z"
                self.recentness = currentTime - self.sixtime
            elif timeFormat == 3:
                self.category = "async-12"
                self.tsalp = f"{self.twelvetime.strftime('%b')} {self.twelvetime.day}, {self.twelvetime.year} - {self.twelvetime.hour}Z to {givenTime.strftime('%b')} {givenTime.day}, {givenTime.year} - {givenTime.hour:02d}{givenTime.minute:02d}Z"
                self.recentness = currentTime - self.twelvetime
            elif timeFormat == 4:
                self.category = "async-24"
                self.tsalp = f"{self.twentyfourtime.strftime('%b')} {self.twentyfourtime.day}, {self.twentyfourtime.year} - {self.twentyfourtime.hour}Z to {givenTime.strftime('%b')} {givenTime.day}, {givenTime.year} - {givenTime.hour:02d}{givenTime.minute:02d}Z"
                self.recentness = currentTime - self.twentyfourtime
        else:
            self.ys = f"{self.time.year}"
            self.ms = f"{self.time.year}-{self.time.strftime('%m')}"
            self.ds = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}"
            self.tsnum = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}-{self.time.strftime('%H%M')}Z"
            self.tsalp = f"{self.time.strftime('%b')} {self.time.day}, {self.time.year} - {self.time.hour:02d}{self.time.minute:02d}Z"
            self.recentness = currentTime - self.time
        
        try:
            self.tsfull = f"{self.time.year}-{self.time.strftime('%m')}-{self.time.strftime('%d')}-{self.time.strftime('%H%M')}Z"
        except AttributeError:
            self.tsfull = f"{self.onetime.year}-{self.onetime.strftime('%m')}-{self.onetime.strftime('%d')}-{self.onetime.strftime('%H%M')}Z"
        
        if convMode == "recent":
            if convFormat == 5:
                if givenTime.hour > 20:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                elif givenTime.hour + (givenTime.minute / 60) > 16.5:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 16, 30)
                elif givenTime.hour > 13:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 13, 0)
                elif givenTime.hour > 12:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 12, 0)
                elif givenTime.hour > 1:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 1, 0)
                else:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0) - timedelta(days=1)
            if convFormat == 6:
                if givenTime.hour + (givenTime.minute / 60) > 17.5:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                elif givenTime.hour > 6:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 6, 0)
                else:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30) - timedelta(days=1)
            if convFormat == 7:
                if givenTime.hour + (givenTime.minute / 60) > 7.5:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                else:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30) - timedelta(days=1)
            if convFormat == 8:
                if givenTime.hour > 9:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day, 3)
                else:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day) - timedelta(days=1)
        elif convMode == "latest":
            if currentTime - givenTime > timedelta(days=1):
                if convFormat == 5:
                    self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                if convFormat == 6:
                    self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                if convFormat == 7:
                    self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                if convFormat == 8:
                    self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day)
            else:
                if convFormat == 5:
                    if givenTime.hour > 20:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0)
                    elif givenTime.hour + (givenTime.minute / 60) > 16.5:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 16, 30)
                    elif givenTime.hour > 13:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 13, 0)
                    elif givenTime.hour > 12:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 12, 0)
                    elif givenTime.hour > 1:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 1, 0)
                    else:
                        self.c1time = datetime(givenTime.year, givenTime.month, givenTime.day, 20, 0) - timedelta(days=1)
                if convFormat == 6:
                    if givenTime.hour + (givenTime.minute / 60) > 17.5:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30)
                    elif givenTime.hour > 6:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 6, 0)
                    else:
                        self.c2time = datetime(givenTime.year, givenTime.month, givenTime.day, 17, 30) - timedelta(days=1)
                if convFormat == 7:
                    if givenTime.hour + (givenTime.minute / 60) > 7.5:
                        self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30)
                    else:
                        self.c3time = datetime(givenTime.year, givenTime.month, givenTime.day, 7, 30) - timedelta(days=1)
                if convFormat == 8:
                    if givenTime.hour > 9:
                        self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day)
                    else:
                        self.ptime = datetime(givenTime.year, givenTime.month, givenTime.day) - timedelta(days=1)
        
        self.timeformat = timeFormat
        self.convformat = convFormat
        
        self.now = currentTime
        
    def ToString(self):
        return f"{self.time.year}, {self.time.month}, {self.time.day}, {self.time.hour}, {self.time.minute}"
    
    def WithMinutes(self):
        return datetime(self.time.year, self.time.month, self.time.day, self.time.hour, self.minutes)
    

def ParseTime(string, plotType=[-1], currentTimeObj=datetime.utcnow(), timeMode="raw", convMode="recent"):
    return Time(string, plotType, currentTimeObj, timeMode, convMode)

def FromDatetime(datetimeObj, plotType=[-1], currentTimeObj=datetime.utcnow(), timeMode="raw", convMode="recent"):
        customTimeFormat = f"{datetimeObj.year}, {datetimeObj.month}, {datetimeObj.day}, {datetimeObj.hour}, {datetimeObj.minute}"
        newTime = ParseTime(customTimeFormat, plotType, currentTimeObj, timeMode, convMode)
        return newTime

def ToDatetime(time):
    string = f"{time.year}-{time.month}-{time.day}, {time.hour}-{time.minute}-{time.second}"
    return string
    
    

class Levels(object):
    def __init__(self, lvlstring):
        
        self.mslp_formatter = lambda v: format(v*10, '.0f')[-3:]
        
        if lvlstring != 'surface':
            lvlstring = int(lvlstring)
            if (lvlstring == 975) or (lvlstring == 850) or (lvlstring == 700):
                self.height_format = lambda v: format(v, '.0f')[1:]
                self.steps = 30
            elif lvlstring == 500:
                self.height_format = lambda v: format(v, '.0f')[:-1]
                self.steps = 60
            elif lvlstring == 300:
                self.height_format = lambda v: format(v, '.0f')[:-1]
                self.steps = 120
            elif lvlstring == 200:
                self.height_format = lambda v: format(v, '.0f')[1:-1]
                self.steps = 120
                
            self.level = int(lvlstring)
        else:
            self.level = lvlstring

def GetLevel(lvlstring):
    return Levels(lvlstring)

def setTime():
    currentTime = datetime.utcnow()
    return currentTime
    
def getTime():
    currentTime = datetime.utcnow()
    print(f"(AMGP_UTIL) <time> It is currently {currentTime}Z")
    return currentTime

def ClearTemp():
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Maps")
    for subPath in os.listdir(f"{dr}/Temp"):
        if os.path.isdir(f"{dr}/Temp/{subPath}"):
            ClearTemp(f"{dr}/Temp/{subPath}")
            os.rmdir(f"{dr}/Temp/{subPath}")
        else:
            with contextlib.suppress(FileNotFoundError):
                os.remove(f"{dr}/Temp/{subPath}")

def Watermark(save, version, form):
    if form == 0:
        wid, hei = save.size
        if wid > hei:
            sz = (int(hei * 0.8), int(hei * 0.8))
        if hei > wid:
            sz = (int(wid * 0.8), int(wid * 0.8))
        sz1, sz2 = sz
        dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "")
        wm = PImage.open(f'{dr}/Resources/logo.png')
        wm = wm.convert('RGBA').resize(sz)
        bands = list(wm.split())
        if len(bands) == 4:
            bands[3] = bands[3].point(lambda x: x*0.05)
        wm = PImage.merge(wm.mode, bands)
        left = int((wid-sz1) / 2)
        top = int((hei-sz1) / 2)
        save.paste(wm, (left, top), wm)
        
    if form == 1:
        wid, hei = save.size
        if wid > hei:
            sz = (int(hei * 0.1), int(hei * 0.1))
        if hei > wid:
            sz = (int(wid * 0.1), int(wid * 0.1))
        sz1, sz2 = sz
        dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "")
        wm = PImage.open(f'{dr}/Resources/logo.png')
        wm = wm.convert('RGBA').resize(sz)
        bands = list(wm.split())
        wm = PImage.merge(wm.mode, bands)
        left = int(wid * 0.01)
        top = int(hei * 0.85)
        save.paste(wm, (left, top), wm)
        
    if form == 2:
        wid, hei = save.size
        if wid > hei:
            sz = (int(hei * 0.1), int(hei * 0.1))
        if hei > wid:
            sz = (int(wid * 0.1), int(wid * 0.1))
        sz1, sz2 = sz
        dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "")
        wm = PImage.open(f'{dr}/Resources/logo.png')
        wm = wm.convert('RGBA').resize(sz)
        bands = list(wm.split())
        wm = PImage.merge(wm.mode, bands)
        left = int(wid * 0.89)
        top = int(hei * 0.89)
        save.paste(wm, (left, top), wm)
    return save


def getPing(Now, Modules):
    for module in Modules:
        module.ping(Now)

def LocalData():
    #dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "LocalData")
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/../LDS_Directories.txt") as LDSes:
        LDF = {}
        n = 1
        for line in LDSes:
            if not line.startswith("#"):
                dr = line.replace("\n", "")
                LDFa, n = SearchDir(dr, n)
                LDF = {**LDF, **LDFa}
    return LDF

def SearchDir(dir, cur_n=1, cur_LDF={}):
    LDF = {}
    n = cur_n
    for res in os.scandir(dir):
        if res.is_file():
            if "%" in res.path:
                sfile = res.path.split("%")
                s2file = sfile[1].split(".")[0]
                LDF[n] = [res.path, s2file.split("+")]
                n += 1
        else:
            if "%" in res.path.split("/")[len(res.path.split("/"))-1]:
                check = res.path.split("/")[len(res.path.split("/"))-1].split("%")
                checks = check[1].split("+")
                for afile in os.scandir(res.path):
                    LDF[n] = [afile.path, checks]
                    n += 1
            else:
                LDFa, non = SearchDir(res.path, n, cur_LDF | LDF)
                LDF | LDFa
    return cur_LDF | LDF, n
                        

def PrintLocalData(LDF):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "LocalData")
    if len(LDF.items()):
        print("(AMGP_UTIL) <lds> The following local data files are available:")
        for obj in LDF.items():
            print(f"(AMGP_UTIL) <lds> {obj[0]} - {obj[1][0].split(f'/')[len(obj[1][0].split(f'/'))-1]}")


def ThrowError(moduleName, type, text, log=True, exit=False, echo=False):
    if type == 0:
        Type = "error"
    elif type == 1:
        Type = "warning"
    elif type == 2:
        Type = "alert"
    
    if echo:
        print(f"(AMGP_UTIL) <{Type}> {moduleName} threw '{text}'")
        
    if log:
        dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "Logs")
        with open(f"{dr}/ErrorLogs/{runtime.replace(microsecond=0)}.log", "a+") as logfile:
            logfile.write(f"{moduleName} produced code {type} at {datetime.utcnow()}: " + text + "\n")

    if exit:
        sys.exit()


def ArcDist(lat1, lon1, lat2, lon2):
    radius = 6378100
    delX = math.cos(math.radians(lat2)) * math.cos(math.radians(lon2)) - math.cos(math.radians(lat1)) * math.cos(math.radians(lon1))
    delY = math.cos(math.radians(lat2)) * math.sin(math.radians(lon2)) - math.cos(math.radians(lat1)) * math.sin(math.radians(lon1))
    delZ = math.sin(math.radians(lat2)) - math.sin(math.radians(lat1))
    C = math.sqrt(delX**2 + delY**2 + delZ**2)
    angle = 2 * math.asin(C/2)
    dist = radius * angle
    return dist