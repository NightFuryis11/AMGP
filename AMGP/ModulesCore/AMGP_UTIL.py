###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #
#           Distributed under the GPL-3.0 License             #
#                  Created on Mar 09, 2022                    #
#                                                             #
#                  Core Module: AMGP_UTIL.py                  #
#                     Author: Sam Bailey                      #
#                 Last Revised: Apr 14, 2024                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################
"""
AMGP_UTIL

The Automated Map Generation Program's Utilities Module

The technical bits that make AMGP streamlined for the user,
chunking out many clunky-to-deal-with processes like those
dealt with via the all-important `Time` object, which packs
many `datetime.datetime` objects inside of it.
"""

#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_MENU as amgpmenu
#-----------------  Definitions -------------------#

import sys
import os
import math

import json

from cartopy import crs as ccrs

from datetime import datetime, timedelta, timezone

from PIL import Image, ImageTk

import pickle as pkl

import numpy as np

def GetPing(data_modules):
    for module in data_modules.values():
        module.Ping()

def LocalData():
    #dr = os.path.dirname(os.path.realpath(__file__)).replace("Modules", "LocalData")
    with open(f"{os.path.dirname(os.path.realpath(__file__))}{PathSep()}..{PathSep()}LDS_Directories.txt") as LDSes:
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
            if "%" in res.path.split(f"{PathSep()}")[len(res.path.split(f"{PathSep()}"))-1]:
                check = res.path.split(f"{PathSep()}")[len(res.path.split(f"{PathSep()}"))-1].split("%")
                checks = check[1].split("+")
                for afile in os.scandir(res.path):
                    LDF[n] = [afile.path, checks]
                    n += 1
            else:
                LDFa, non = SearchDir(res.path, n, cur_LDF | LDF)
                LDF | LDFa
    return cur_LDF | LDF, n

def CustomAreas(code : str):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Resources")
    with open(f"{dr}{PathSep()}amgp_area_definitions.json", "r") as J:
        file_data = json.load(J)
        if code in file_data.keys():
            area = file_data[code].replace(" ", "").split(",")
            unpacked = (float(area[0]), float(area[1]), float(area[2]), float(area[3]))
            return unpacked
        J.close()
    
    if not os.path.isfile(f"{dr}{PathSep()}user_area_definitions.json"):
        with open(f"{dr}{PathSep()}user_area_definitions.json", "w+") as F:
            json.dump({}, F)

    with open(f"{dr}{PathSep()}user_area_definitions.json", "r") as J:
        file_data = json.load(J)
        if code in file_data.keys():
            area = file_data[code].replace(" ", "").split(",")
            unpacked = (float(area[0]), float(area[1]), float(area[2]), float(area[3]))
            return unpacked
        J.close()
    return None

def SavePreset(preset_name, source_module_name, plotables, map_settings, projections, associated_style, save_location):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Presets")

    if not os.path.isdir(dr):
        os.mkdir(dr)

    data = {"version":amgpmenu.Version(), "type":source_module_name, "plotables":plotables, "projections":projections, "map_settings":map_settings, "style":associated_style, "save":save_location}
    if preset_name != "":
        if not os.path.isdir(f"{dr}{PathSep()}{source_module_name}"):
            os.mkdir(f"{dr}{PathSep()}{source_module_name}")
        
        if os.path.isfile(f"{dr}{PathSep()}{source_module_name}{PathSep()}{preset_name}.json"):
            os.remove(f"{dr}{PathSep()}{source_module_name}{PathSep()}{preset_name}.json")
        
        with open(f"{dr}{PathSep()}{source_module_name}{PathSep()}{preset_name}.json", "w+") as J:
            json.dump(data, J)

def ListPresets(source_module_name):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Presets")

    presets = []

    if not os.path.isdir(f"{dr}{PathSep()}{source_module_name}"):
        preset = None
    else:
        for preset in os.listdir(f"{dr}{PathSep()}{source_module_name}"):
            if preset.endswith('.json'):
                presets.append(f"{preset.replace('.json','')}")
    
    return presets

def LoadPreset(preset_name, source_module_name):
    dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Presets")

    if source_module_name == None:
        with open(preset_name, "r") as J:
            preset_data = json.load(J)
    else:
        with open(f"{dr}{PathSep()}{source_module_name}{PathSep()}{preset_name}.json", "r") as J:
            preset_data = json.load(J)

    return_preset_data = {}

    for k, v in preset_data.items():
        return_preset_data[k] = None
        if (type(v) == dict) and (k != "style"):
            return_preset_data[k] = {}
            for x, y in v.items():
                return_preset_data[k][int(x)] = y
        else:
            return_preset_data[k] = v

    return return_preset_data

def ListStyles():
    styles = []
    
    for style in os.listdir(f'{os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Styles")}'):
        if style.endswith('.py'):
            styles.append(f"{style.replace('.py','')}")
    
    return styles

def PathSep():
    if os.name == "posix":
        delim = "/"
    elif os.name == "nt":
        delim = "\\"
    return delim

def ModuleFromUID(uid, module_list):
    for _, module in module_list.items():
        if uid == module.Info()["uid"]:
            return module

def AreaDictionary(ret = True):
    if os.path.isfile(f"{os.path.dirname(os.path.realpath(__file__))}{PathSep()}..{PathSep()}config.json"):
        with open(f"{os.path.dirname(os.path.realpath(__file__))}{PathSep()}..{PathSep()}config.json", "r") as cfg:
            config = json.load(cfg)
    
        global area_dictionary
        area_dictionary = {k: tuple(map(float, v.split(", "))) for k, v in dict(config["areas"]).items()}

        if ret:
            return area_dictionary
        
def ImgResize(image_path : str, target_dim : tuple):
    preview_image = Image.open(image_path).convert("RGBA")

    w, h = preview_image.size
    i_ratio = w / h

    tw, th = target_dim

    t_ratio = tw / th

    h_ratio = th / h

    w_ratio = tw / w

    if i_ratio < t_ratio:
        r_w = round(w * h_ratio)
        r_h = round(h * h_ratio)
        #r_w = tw
        #r_h = round(tw * (1 / i_ratio))
    else:
        r_w = round(w * w_ratio)
        r_h = round(h * w_ratio)
        #r_h = th
        #r_w = round(th * i_ratio)
    preview_image = preview_image.resize((r_w, r_h), Image.Resampling.NEAREST)

    return preview_image

def Water(fig_path : str, location : str):
    wm_str = f'{os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Resources")}{PathSep()}logo.png'
    fig = Image.open(fig_path)
    fig_width, fig_height = fig.size
    if location.lower() in ["c", "center"]:
        opacity = 0.08
        wm = ImgResize(wm_str, (fig_width * 0.8, fig_height * 0.8))
        bands = list(wm.split())
        if len(bands) == 4:
            bands[3] = bands[3].point(lambda x: x*opacity)
        wm = Image.merge(wm.mode, bands)
        wm_width, wm_height = wm.size
        left = int((fig_width-wm_width) / 2)
        top = int((fig_height-wm_height) / 2)
        fig.paste(wm, (left, top), wm)
        bands2 = list(fig.split())
        if len(bands2) == 4:
            bands2[3] = bands2[3].point(lambda x: x*(1/opacity))
        fig = Image.merge(fig.mode, bands2)
    elif location.lower().replace(" ", "") in ["sw", "southwest", "bottomleft"]:
        opacity = 0.8
        wm = ImgResize(wm_str, (fig_width * 0.15, fig_height * 0.15))
        bands = list(wm.split())
        if len(bands) == 4:
            bands[3] = bands[3].point(lambda x: x*opacity)
        wm = Image.merge(wm.mode, bands)
        wm_width, wm_height = wm.size
        left = int(fig_width/40)
        top = int(fig_height - ((fig_height / 40) * 7))
        fig.paste(wm, (left, top), wm)
        bands2 = list(fig.split())
        if len(bands2) == 4:
            bands2[3] = bands2[3].point(lambda x: x*(1/opacity))
        fig = Image.merge(fig.mode, bands2)


    return fig

def TKIMG(image_path : str, target_dim : tuple):
    tkimg_file = ImageTk.PhotoImage(ImgResize(image_path, target_dim))
    return tkimg_file

class Factor(object):
    """
    The Factor object holds details about each plotable data source that modules return.

    Calling the base class merely initializes an empty object; data should be filled using one of the in-built methods.
    """
    def __init__(self):
        self.source_module = None
        self.name = None
        self.description = None
        self.options = None
        self.time_format = None
        self.is_fill = None
    
    def NewFactor(self, module : object, factor_name : str, factor_details : dict):
        """
        Turn dictionary parameters into object attributes for easier use.

        Parameters
        ----------
        module : object
            The source imported module of the factor stored as a variable.
        
        factor_name : string
            The name of the factor to be plotted.
        
        factor_details : dict
            The attributes of the given factor, stored as a dictionary.

            Expected keys are "description", "time_format", "is_fill", and "options".
        
        Returns
        -------
        self : object
            The factor with updated attributes.
        """
        self.source_module = module.Info()["uid"]
        self.name = factor_name
        self.description = factor_details["description"]
        self.time_format = factor_details["time_format"]
        self.is_fill = factor_details["is_fill"]
        option_dict = {}
        for option_name, options in factor_details["options"].items():
            option_dict[f"{option_name}"] = options
        self.options = option_dict
        return self

    def AsObject(self, dictionary : dict):
        self.source_module = dictionary["source_module"]
        self.name = dictionary["name"]
        self.options = dictionary["options"]
        self.time_format = dictionary["time_format"]
        self.is_fill = dictionary["is_fill"]
        self.description = dictionary["description"]
        return self

    def AsDict(self):
        dict_form = {"source_module":self.source_module,
                     "name":self.name,
                     "description":self.description,
                     "options":self.options,
                     "time_format":self.time_format,
                     "is_fill": self.is_fill}
        return dict_form
    
def GetFactors(data_modules):
    factors = []
    for _, module in data_modules.items():
        for factor, attributes in module.Factors().items():
            factor_obj = Factor().NewFactor(module, factor, attributes)
            factors.append(factor_obj)
    return factors

class Time(object):
    """
    The Time object is the core of how AMGP manages data organization and pulling by managing factor formats on both a bulk and individual basis.
    Time objects can handle many datetime objects at once, and will format them based on the used factors.

    Parameters
    ----------
    runtime : datetime.datetime

    mode : string

    kwargs
        Expected kwargs are:
            timestring : string
            starttime : datetime.datetime
            endtime : datetime.datetime
            interval : datetime.timedelta

        timestring is mutually-exclusive with all other kwargs

    Returns
    -------
    self : amgp.Time

    Methods
    -------
    AddFormatting()

    Index()

    FormatTimes()
    """
    def __init__(self, runtime : datetime, mode : str = None, **kwargs):
        self.start_time = None
        self.end_time = None
        self.interval = None
        self.time_mode = mode
        self.timelist = []
        self.entries = None
        self.format_sources = {}
        self.formats = []
        self.runtime = runtime
    
        if "timestring" in kwargs:
            def ParseTS(ts : str, delta : bool = False):
                if delta:
                    dt = datetime.strptime(ts, "%H:%M:%S")
                    dt = timedelta(days=0, hours = dt.hour, minutes = dt.minute)
                elif ts == "recent":
                    dt = datetime.now(timezone.utc)
                else:
                    dt = datetime.strptime(ts, "%Y%m%d-%H:%M:%S")
                
                return dt
            
            timestring = kwargs["timestring"]

            tslist = timestring.split(" ")

            startindex = None
            endindex = None
            intervalindex = None

            for index in range(0, len(tslist)):
                if tslist[index].lower() == "to":
                    startindex = index - 1
                    endindex = index + 1
                    try:
                        if tslist[index + 2].lower() == "interval":
                            intervalindex = index + 3
                    except:
                        pass
            
            if startindex == None:
                startindex = 0
            
            self.start_time = ParseTS(tslist[startindex])

            if endindex:
                self.end_time = ParseTS(tslist[endindex])
            
            if intervalindex:
                self.interval = ParseTS(tslist[intervalindex], True)
        
        if "starttime" in kwargs:
            self.start_time = kwargs["starttime"]

        if "endtime" in kwargs:
            self.end_time = kwargs["endtime"]
        
        if "interval" in kwargs:
            self.interval = kwargs["interval"]
        
        if (("timestring" in kwargs) and (("starttime" in kwargs) or ("endtime" in kwargs) or ("interval" in kwargs))):
            ThrowError("AMGP_UTIL", "time_object", 0, "An attempt to make a Time Object was made with multiple conflicting methods of timesetting.", runtime, True, True, False)
        
        #print(self.start_time, self.end_time, self.interval)

        if (self.end_time == None) and (self.interval == None):
            self.timelist = [self.start_time]
        else:
            if (self.end_time != None) and (self.interval == None):
                self.interval = timedelta(minutes=5)
            c_time = self.start_time
            while c_time <= self.end_time:
                self.timelist.append(c_time)
                c_time = c_time + self.interval
        
        self.entries = len(self.timelist)

    def AddFormatting(self, used_factors : list):
        """
        Parameters
        ----------
        self : amgp.Time
            This is a function for an AMGP Time object

        used_factors : list
            The output from AMGP_MENU which contains all relevant details about the selected plotting factors

        Returns
        -------
        self : amgp.Time
            self.formats is modified to contain data on which time formats the selected factors use
        """

        if used_factors == []:
            return self

        for factor in used_factors:
            #print(used_factors)
            self.format_sources[f"{factor['source_module']}-{factor['name']}"] = factor["time_format"]
        
        for _, format in self.format_sources.items():
            if (format not in self.formats) and (type(format) == str):
                self.formats.append(format)
            elif type(format) == list:
                for item in format:
                    self.formats.append(item)
        
        return self

    def Index(self, index : int):
        """
        Parameters
        ----------
        self : amgp.Time
            This is a function for an AMGP Time object
        
        index : int
            The index of self.timelist to be selected

        Returns
        -------
        self : amgp.Time
            self.timelist is cut down to be only a single datetime.datetime object within a list
        """
        self.timelist = [self.timelist[index]]
        return self

    def FormatTimes(self, formatter : str):
        """
        The AMGP Time object's most important function, and formats the datetime objects within self.timelist to conform to the parameters required
        by the data to be retrieved. Requires AddFormatting() to be run on the Time object first.

        Parameters
        ----------
        self : amgp.Time
            This is a function for an AMGP Time object
        
        formatter : string
            The string formatter designating what kind of repition is used by the given factor
            If time_mode is raw or sync, formatter won't change the effect of the function
        """

        if self.formats == []:
            ThrowError("AMGP_UTIL", "Time.FormatTimes()", 1, "The FormatTimes() function cannot be run on a Time object prior to the AddFormatting() function being run on said Time object.", self.runtime, True, False, True)
            return self

        for i in range(0, len(self.timelist)):
            self.timelist[i] = self.timelist[i].replace(microsecond = 0)

        if self.time_mode != "raw":
            for i in range(0, len(self.timelist)):
                if self.time_mode == "sync":
                    if "24h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = 0, minute = 0, second = 0)
                    elif "12h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 12, minute = 0, second = 0)
                    elif "8h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 8, minute = 0, second = 0)
                    elif "6h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 6, minute = 0, second = 0)
                    elif "4h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 4, minute = 0, second = 0)
                    elif "3h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 3, minute = 0, second = 0)
                    elif "2h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 2, minute = 0, second = 0)
                    elif "1h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(minute = 0, second = 0)
                    elif "45m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) % 60, second = 0)
                    elif "40m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) % 60, second = 0)
                    elif "30m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) % 60, second = 0)
                    elif "20m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) % 60, second = 0)
                    elif "15m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) % 60, second = 0)
                    elif "10m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) % 60, second = 0)
                    elif "5m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) % 60, second = 0)
                    elif "1m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(second = 0)
                
                elif self.time_mode == "nearest":
                    if "1m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(second = 0)
                    elif "5m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) % 60, second = 0)
                    elif "10m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) % 60, second = 0)
                    elif "15m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) % 60, second = 0)
                    elif "20m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) % 60, second = 0)
                    elif "30m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) % 60, second = 0)
                    elif "40m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) % 60, second = 0)
                    elif "45m" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) % 60, second = 0)
                    elif "1h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(minute = 0, second = 0)
                    elif "2h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 2, minute = 0, second = 0)
                    elif "3h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 3, minute = 0, second = 0)
                    elif "4h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 4, minute = 0, second = 0)
                    elif "6h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 6, minute = 0, second = 0)
                    elif "8h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 8, minute = 0, second = 0)
                    elif "12h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 12, minute = 0, second = 0)
                    if "24h" in self.formats:
                        self.timelist[i] = self.timelist[i].replace(hour = 0, minute = 0, second = 0)

                elif self.time_mode == "async":
                    if formatter == "24h":
                        self.timelist[i] = self.timelist[i].replace(hour = 0, minute = 0, second = 0)
                    elif formatter == "12h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 12, minute = 0, second = 0)
                    elif formatter == "8h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 8, minute = 0, second = 0)
                    elif formatter == "6h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 6, minute = 0, second = 0)
                    elif formatter == "4h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 4, minute = 0, second = 0)
                    elif formatter == "3h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 3, minute = 0, second = 0)
                    elif formatter == "2h":
                        self.timelist[i] = self.timelist[i].replace(hour = self.timelist[i].hour - self.timelist[i].hour % 2, minute = 0, second = 0)
                    elif formatter == "1h":
                        self.timelist[i] = self.timelist[i].replace(minute = 0, second = 0)
                    elif formatter == "45m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 45)) % 60, second = 0)
                    elif formatter == "40m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 40)) % 60, second = 0)
                    elif formatter == "30m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 30)) % 60, second = 0)
                    elif formatter == "20m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 20)) % 60, second = 0)
                    elif formatter == "15m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 15)) % 60, second = 0)
                    elif formatter == "10m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 10)) % 60, second = 0)
                    elif formatter == "5m":
                        self.timelist[i] = self.timelist[i].replace(hour = math.floor((((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) / 60), minute = (((self.timelist[i].hour * 60) + self.timelist[i].minute) - (((self.timelist[i].hour * 60) + self.timelist[i].minute) % 5)) % 60, second = 0)
                    elif formatter == "1m":
                        self.timelist[i] = self.timelist[i].replace(second = 0)

                if formatter == "day1":
                    if ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 20*60 + 0:
                        self.timelist[i] = self.timelist[i].replace(hour = 20, minute = 0, second = 0)
                    elif ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 16*60 + 30:
                        self.timelist[i] = self.timelist[i].replace(hour = 16, minute = 30, second = 0)
                    elif ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 13*60 + 0:
                        self.timelist[i] = self.timelist[i].replace(hour = 13, minute = 0, second = 0)
                    elif ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 6*60 + 0:
                        self.timelist[i] = self.timelist[i].replace(hour = 6, minute = 0, second = 0)
                    elif ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 1*60 + 0:
                        self.timelist[i] = self.timelist[i].replace(hour = 1, minute = 0, second = 0)
                    else:
                        self.timelist[i] = self.timelist[i].replace(hour = 20, minute = 0, second = 0) - timedelta(days=1)
                elif formatter == "day2":
                    if ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 17*60 + 30:
                        self.timelist[i] = self.timelist[i].replace(hour = 17, minute = 30, second = 0)
                    elif ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 8*60 + 0:
                        self.timelist[i] = self.timelist[i].replace(hour = 8, minute = 0, second = 0)
                    else:
                        self.timelist[i] = self.timelist[i].replace(hour = 17, minute = 30, second = 0) - timedelta(days=1)
                elif formatter == "day3":
                    if ((self.timelist[i].hour * 60) + self.timelist[i].minute) >= 7*60 + 30:
                        self.timelist[i] = self.timelist[i].replace(hour = 7, minute = 30, second = 0)
                    else:
                        self.timelist[i] = self.timelist[i].replace(hour = 7, minute = 30, second = 0) - timedelta(days=1)
                elif (formatter == "day4") or (formatter == "day5") or (formatter == "day6") or (formatter == "day7") or (formatter == "day8"):
                    self.timelist[i] = self.timelist[i].replace(hour = 0, minute = 0, second = 0)

        return self

def ParseProjection(proj_dict):

    if proj_dict["central_longitude"]["selection"] != "":
        clon = int(proj_dict["central_longitude"]["selection"])
    else:
        clon = None
    
    if proj_dict["central_latitude"]["selection"] != "":
        clat = int(proj_dict["central_latitude"]["selection"])
    else:
        clat = None
    
    if proj_dict["standard_parallel_1"]["selection"] != "":
        spar_1 = int(proj_dict["standard_parallel_1"]["selection"])
    else:
        spar_1 = None
    
    if proj_dict["standard_parallel_2"]["selection"] != "":
        spar_2 = int(proj_dict["standard_parallel_2"]["selection"])
    else:
        spar_2 = None
    
    spar = []
    for sp in [spar_1, spar_2]:
        if sp != None:
            spar.append(sp)
    
    if proj_dict["satellite_height"]["selection"] != "":
        sath = int(proj_dict["satellite_height"]["selection"])
    else:
        sath = None

    if proj_dict["projection"]["selection"][0] == "Lambert Conformal":
        if spar == []:
            proj = ccrs.LambertConformal(central_latitude = clat, central_longitude = clon)
        else:
            proj = ccrs.LambertConformal(central_latitude = clat, central_longitude = clon, standard_parallels = spar)
    elif proj_dict["projection"]["selection"][0] == "Plate Carree":
        proj = ccrs.PlateCarree(central_longitude = clon)
    elif proj_dict["projection"]["selection"][0] == "Robinson":
        proj = ccrs.Robinson(central_longitude = clon)
    elif proj_dict["projection"]["selection"][0] == "Geostationary":
        proj = ccrs.Geostationary(central_longitude = clon, satellite_height = sath)
    elif proj_dict["projection"]["selection"][0] == "Nearside Perspective":
        proj = ccrs.NearsidePerspective(central_latitude = clat, central_longitude = clon, satellite_height = sath)
    elif proj_dict["projection"]["selection"][0] == "None":
        proj = None

    return proj

def keytest(key):
    unpkl = pkl.load(key)

    knum = unpkl.k
    a = knum[4:-4]
    b = knum[-4:]
    c = knum[:4]
    aadd = np.sum([int(x) for x in a])

    if int(b) == int(c)*int(aadd):
        return unpkl
    else:
        return None

class amgpkey(object):
    def __init__(self, keynum : str, name : str):
        self.k = keynum
        self.username = name

def ThrowError(moduleName : str, process : str, type : int, text : str, runtime : datetime, log : bool = True, exit : bool = False, echo : bool = False):
    """
    AMGP's custom error handler, predominantly for the purpose of
    handling the creation of log files and console printouts.

    Parameters
    ----------
    moduleName : string
        The module name, as recognized elsewhere within the program (AMGP_*), in string form.

    process : string
        The process name which the error was produced in.
    
    type : int
        Error call type, stored as an integer. Purely cosmetic at the current time.

        0. Standard error
        1. Warning
        2. Alert

        Values outside of the ones listed above return with type "null", indicating that they
        are not truly errors, but simply informational. The standard for this is "-1".

    text : string
        The custom error message for the given thrown error. Can be any string.
    
    runtime : datetime.datetime
        The time AMGP was initialized.

    log : bool, optional, defaults to True
        Whether or not the error should be saved to the log file for the session.

    exit : bool, optional, defaults to False
        Whether or not the error should close the program upon being thrown.

    echo : bool, optional, defaults to False
        Whether or not the error should be printed to the console upon being thrown.
    """

    if type == 0:
        Type = "Error"
    elif type == 1:
        Type = "Warning"
    elif type == 2:
        Type = "Alert"
    else:
        Type = "Other"
    
    if echo:
        print(f"(AMGP_UTIL) <ThrowError()> {Type}: {moduleName} <{process}> threw '{text}'")
        
    if log:
        dr = os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Logs")
        if not os.path.exists(dr):
            os.mkdir(dr)
        if not os.path.exists(f"{dr}{PathSep()}ErrorLogs"):
            os.mkdir(f"{dr}{PathSep()}ErrorLogs")
        with open(f"{dr}{PathSep()}ErrorLogs{PathSep()}{runtime.replace(microsecond=0)}.log", "a+") as logfile:
            logfile.write(f"{moduleName} produced code {type} at {datetime.now(timezone.utc)}: " + text + "\n")
            logfile.close()

    if exit:
        sys.exit()