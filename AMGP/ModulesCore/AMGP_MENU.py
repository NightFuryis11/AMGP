###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #
#           Distributed under the GPL-3.0 License             #
#                  Created on Mar 09, 2022                    #
#                                                             #
#                  Core Module: AMGP_MENU.py                  #
#                     Author: Sam Bailey                      #
#                 Last Revised: Apr 14, 2025                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################

import tkinter as tk
from tkinter import ttk

import os
import sys

import glob

import webbrowser

from ast import literal_eval

#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_UTIL as amgp
from ModulesCore import AMGP_MAP as amgpmap
#-----------------  Definitions -------------------#

preset_prefix = f'{os.path.dirname(os.path.realpath(__file__).replace("ModulesCore", "Styles"))}'

def Info():
    return {
        "name":"AMGP_MENU",
        "uid":"00220100"
    }

def InitWithInterface(packed_data):
    global version
    global util_modules
    global data_modules
    global menu_modules
    global module_names
    global styles
    global runtime
    global comp_data
    comp_data = packed_data
    version = packed_data["version"]
    util_modules = packed_data["util_modules"]
    data_modules = packed_data["data_modules"]
    menu_modules = packed_data["menu_modules"]
    module_names = packed_data["module_names"]
    styles = packed_data["styles"]
    runtime = packed_data["runtime"]
    

    amgp.GetPing(data_modules)
    Start()

def InitWithoutInterface(packed_data, preset_dict):
    RunWithoutInterface(packed_data, preset_dict["plotables"], preset_dict["map_settings"], preset_dict["projections"], preset_dict["style"], preset_dict["save"])


def Version():
    global version
    return version

def RunFromInterface(selected_plotables, selected_map, selected_projections, selected_style, save_loc):
    global StatusBox
    global window
    #print(literal_eval(selected_plotables.get()))
    #print(literal_eval(selected_map.get()))
    UpdateStatusBox("Running...")
    if (literal_eval(selected_plotables.get()) != []) and (literal_eval(selected_map.get()) != {}):
        amgp.SavePreset("Previous", "AMGP_MENU", literal_eval(selected_plotables.get()), literal_eval(selected_map.get()), literal_eval(selected_projections.get()), literal_eval(selected_style.get()), save_loc.get())
        image = amgp.TKIMG(amgpmap.Run(comp_data, literal_eval(selected_plotables.get()), literal_eval(selected_map.get()), literal_eval(selected_projections.get()), literal_eval(selected_style.get()), save_loc.get(), True), (900, 638))
        for im in glob.glob(f'{os.path.dirname(os.path.realpath(__file__).replace("ModulesCore", "Maps"))}{amgp.PathSep()}Temp{amgp.PathSep()}*'):
            os.remove(im) # Clean out the temp folder after running, since we've already produced a TKIMG and no longer need to keep the original in the temp folder
        UpdateStatusBox("Running complete!")
        UpdatePreviewImage(image)
        
    else:
        UpdateStatusBox("Select a style, factors, and map settings before running.")
        
def RunWithoutInterface(packed_data, selected_plotables, selected_map, selected_projections, selected_style, save_loc):
    amgpmap.Run(packed_data, selected_plotables, selected_map, selected_projections, selected_style, save_loc)
    for im in glob.glob(f'{os.path.dirname(os.path.realpath(__file__).replace("ModulesCore", "Maps"))}{amgp.PathSep()}Temp{amgp.PathSep()}*'):
        os.remove(im)

def InitPreset(preset_name):
    global selected_plotables
    global selected_map

    preset_dict = amgp.LoadPreset(preset_name, "AMGP_MENU")

    selected_plotables.set(str(preset_dict["plotables"]))
    selected_map.set(str(preset_dict["map_settings"]))
    selected_projections.set(str(preset_dict["projections"]))
    selected_style.set(str(preset_dict["style"]))
    save_loc.set(preset_dict["save"])

    if preset_dict["style"]["preview"] != None:
        UpdatePreviewImage(amgp.TKIMG(f'{preset_prefix}{amgp.PathSep()}{preset_dict["style"]["preview"]}', (900, 638)))

def InitStyle(style_name):
    global selected_style

    selected_style.set(str(styles[style_name].StyleInfo()))
    if styles[style_name].StyleInfo()["preview"] != None:
        UpdatePreviewImage(amgp.TKIMG(f'{preset_prefix}{amgp.PathSep()}{styles[style_name].StyleInfo()["preview"]}', (900, 638)))

def InitPresetSave(PresetEntryboxVar, selected_plotables, selected_projections, selected_map, selected_style):

    if (literal_eval(selected_plotables.get()) != []) and (literal_eval(selected_map.get()) != {}):
        amgp.SavePreset(PresetEntryboxVar.get(), "AMGP_MENU", literal_eval(selected_plotables.get()), literal_eval(selected_map.get()), literal_eval(selected_projections.get()), literal_eval(selected_style.get()), save_loc.get())

        PresetEntryboxVar.set("")
        UpdatePresetListbox()

def ConfigurePlotables(master_window, selected_plotables, selected_style):
    rows = 4

    global previously_selected_plotables
    global old_plotable_selection

    previously_selected_plotables = {}
    old_plotable_selection = tk.StringVar()
    if literal_eval(selected_plotables.get()) != {}:
        for fig_num, fig_list in literal_eval(selected_plotables.get()).items():
            previously_selected_plotables[fig_num] = [amgp.Factor().AsObject(x) for x in fig_list]
        
    if len([k for (k, _) in previously_selected_plotables.items()]) < literal_eval(selected_style.get())["axes"]:
        for i in range(len([k for (k, _) in previously_selected_plotables.items()]), literal_eval(selected_style.get())["axes"]):
            previously_selected_plotables[i] = [amgp.Factor().AsObject({"source_module":None,"name":None,"description":None,"options":{None:None},"time_format":None,"is_fill":None})]
    
    old_plotable_selection.set(str({k:[F.AsDict() for F in v] for (k, v) in previously_selected_plotables.items()}))

    selectables = [x.AsDict() for x in amgp.GetFactors(data_modules)]

    def save_current_plotables(axis_index):
        global previously_selected_plotables
        global config_result
        config_result = []
        for factor_index in range(0, len(selectables)):
            factor_dictionary = selectables[factor_index]

            if globals()[f"PlotCheckbox{factor_index}"].instate(["selected"]):

                if factor_dictionary["options"] == {None:None}:
                    config_result.append(amgp.Factor().AsObject({"source_module":factor_dictionary["source_module"],"name":factor_dictionary["name"],"description":factor_dictionary["description"],"options":{None:None},"time_format":factor_dictionary["time_format"],"is_fill":factor_dictionary["is_fill"]}))
                else:
                    option_dict = {}
                    option_num = 1
                    for option, options in factor_dictionary["options"].items():
                        if options == [None]:
                            option_dict[f"{option}"] = globals()[f"PlotEntrybox{factor_index}-{option_num}"].get()
                        elif options == ["Bool"]:
                            if globals()[f"PlotCheckbox{factor_index}-{option_num}"].instate(["selected"]):
                                option_dict[f"{option}"] = True
                        else:
                            option_dict[f'{option}'] = [globals()[f"PlotChecklist{factor_index}-{option_num}"].get(x) for x in globals()[f"PlotChecklist{factor_index}-{option_num}"].curselection()]
                        option_num += 1
                    config_result.append(amgp.Factor().AsObject({"source_module":factor_dictionary["source_module"],"name":factor_dictionary["name"],"description":factor_dictionary["description"],"options":option_dict,"time_format":factor_dictionary["time_format"],"is_fill":factor_dictionary["is_fill"]}))
            
            previously_selected_plotables[axis_index] = config_result
    
    def refresh_mapwin(master_window, selected_style, new_axis, old_axis, startup = False):
        global config_window
        if not startup:
            save_current_plotables(old_axis)
            config_window.destroy()
        
        config_window = tk.Toplevel()
        config_window.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
        config_window.title(f"AMGP v{version} - Plotable Config Window")
        config_window.geometry("600x600")

        config_window_frame = tk.Frame(config_window)
        config_window_frame.pack(fill = tk.BOTH, expand = 1)

        global config_window_canvas
        config_window_canvas = tk.Canvas(config_window_frame)

        config_window_scrollbar = tk.Scrollbar(config_window_frame, orient = tk.VERTICAL, command = config_window_canvas.yview)
        config_window_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        config_window_scrollbar2 = tk.Scrollbar(config_window_frame, orient = tk.HORIZONTAL, command = config_window_canvas.xview)
        config_window_scrollbar2.pack(side = tk.BOTTOM, fill = tk.X)

        config_window_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        config_window_canvas.configure(yscrollcommand = config_window_scrollbar.set)
        config_window_canvas.configure(xscrollcommand = config_window_scrollbar2.set)
        config_window_canvas.bind('<Configure>', lambda e: config_window_canvas.configure(scrollregion = config_window_canvas.bbox("all")))

        global config_window_frame2
        config_window_frame2 = tk.Frame(config_window_canvas, width = 600, height = 500)

        globals()[f"PlotStylebox"] = tk.Listbox(config_window_frame2, selectmode = tk.SINGLE, exportselection = False, height = 4)
        for style_index in range(0, literal_eval(selected_style.get())["axes"]):
            globals()[f"PlotStylebox"].insert(style_index, style_index)
        globals()[f"PlotStylebox"].select_set(new_axis)
        globals()[f"PlotStylebox"].grid(row = 0, column = 0)

        globals()[f"PlotStylebutton"] = ttk.Button(config_window_frame2, text = "Change Axis", command = lambda : refresh_mapwin(master_window, selected_style, globals()[f"PlotStylebox"].get(globals()[f"PlotStylebox"].curselection()), new_axis))
        globals()[f"PlotStylebutton"].grid(row = 0, column = 1)

        for factor_index in range(0, len(selectables)):
            factor_dictionary = selectables[factor_index]

            globals()[f"PlotCheckbox{factor_index}"] = ttk.Checkbutton(config_window_frame2, text = f"{factor_dictionary['name']}")
            if (f"{factor_dictionary['name']}" in [F.name for F in previously_selected_plotables[new_axis]]) and (previously_selected_plotables[new_axis][0].name != None):
                globals()[f"PlotCheckbox{factor_index}"].state(["!alternate", "selected"])
            else:
                globals()[f"PlotCheckbox{factor_index}"].state(["!alternate", "!selected"])
            globals()[f"PlotCheckbox{factor_index}"].grid(row=(rows*factor_index) + 1, column=0, padx=5, pady=5)

            globals()[f"PlotLabel{factor_index}"] = ttk.Label(config_window_frame2, text = f"{factor_dictionary['description']}", wraplength=300)
            globals()[f"PlotLabel{factor_index}"].grid(row=(rows*factor_index) + 1, column=2, padx=5, pady=5)

            globals()[f"PlotLabel{factor_index}2"] = ttk.Label(config_window_frame2, text = f"{amgp.ModuleFromUID(factor_dictionary['source_module'], data_modules).Info()['name']}", wraplength=300)
            globals()[f"PlotLabel{factor_index}2"].grid(row=(rows*factor_index) + 1, column=1, padx=5, pady=5)

            if factor_dictionary["options"] == {None:None}: # Any factor with no options should have this under their options
                globals()[f"PlotLabel{factor_index}-0"] = ttk.Label(config_window_frame2, text = "This factor has no options.", wraplength=300)
                globals()[f"PlotLabel{factor_index}-0"].grid(row=(rows*factor_index) + 2, column=0, padx=5, pady=5)
            else:
                option_num = 1
                for option, options in factor_dictionary["options"].items():
                    if options == [None]:
                        globals()[f"PlotEntryboxResult{factor_index}-{option_num}"] = tk.StringVar()
                        globals()[f"PlotEntrybox{factor_index}-{option_num}"] = ttk.Entry(config_window_frame2, textvariable = globals()[f"PlotEntryboxResult{factor_index}-{option_num}"], width=50)
                        if (option in [i for l in [list(F.options.keys()) for F in previously_selected_plotables[new_axis] if F.name == factor_dictionary["name"]] for i in l]) and (previously_selected_plotables[new_axis][0].name != None):
                            globals()[f"PlotEntryboxResult{factor_index}-{option_num}"].set([F for F in previously_selected_plotables[new_axis] if F.name == factor_dictionary["name"]][0].options[option])
                        else:
                            globals()[f"PlotEntryboxResult{factor_index}-{option_num}"].set("")
                        globals()[f"PlotLabel{factor_index}-{option_num}"] = ttk.Label(config_window_frame2, text = f"{option}", wraplength=300)
                        globals()[f"PlotLabel{factor_index}-{option_num}"].grid(row=(rows*factor_index) + 2, column=option_num, padx=5, pady=5)
                        globals()[f"PlotEntrybox{factor_index}-{option_num}"].grid(row=(rows*factor_index) + 3, column=option_num, padx=5, pady=5)
                    elif options == ["Bool"]:
                        globals()[f"PlotCheckbox{factor_index}-{option_num}"] = ttk.Checkbutton(config_window_frame2, text = f"{option}")
                        if (option in [i for l in [list(F.options.keys()) for F in previously_selected_plotables[new_axis] if F.name == factor_dictionary["name"]] for i in l]) and (previously_selected_plotables[new_axis][0].name != None):
                            globals()[f"PlotCheckbox{factor_index}-{option_num}"].state(["!alternate", "selected"])
                        else:
                            globals()[f"PlotCheckbox{factor_index}-{option_num}"].state(["!alternate", "!selected"])
                        globals()[f"PlotCheckbox{factor_index}-{option_num}"].grid(row=(rows*factor_index) + 2, column=option_num, padx=5, pady=5)
                    else:
                        globals()[f"PlotLabel{factor_index}-{option_num}"] = ttk.Label(config_window_frame2, text = f"{option}", wraplength=300)
                        globals()[f"PlotLabel{factor_index}-{option_num}"].grid(row=(rows*factor_index) + 2, column=option_num, padx=5, pady=5)

                        globals()[f"PlotChecklist{factor_index}-{option_num}"] = tk.Listbox(config_window_frame2, selectmode = tk.MULTIPLE, exportselection = False, height = 4)
                        for item_index in range(0, len(options)):
                            globals()[f"PlotChecklist{factor_index}-{option_num}"].insert(item_index, options[item_index]) # item_index + 2 was here, potentially mistakenly?
                            if (options[item_index] in [i for l in [F.options[f"{option}"] for F in previously_selected_plotables[new_axis] if F.name == factor_dictionary["name"]] for i in l]) and (previously_selected_plotables[new_axis][0].name != None):
                                globals()[f"PlotChecklist{factor_index}-{option_num}"].select_set(item_index)
                        globals()[f"PlotChecklist{factor_index}-{option_num}"].grid(row=(rows*factor_index) + 3, column=option_num, padx=5, pady=5)
                    option_num += 1
                
            ConfirmButton = ttk.Button(config_window_frame2, text = "Submit", command = lambda : confirm())
            ConfirmButton.grid(row=(rows*len(selectables))+5, column=0, padx=5, pady=5)

            CancelButton = ttk.Button(config_window_frame2, text = "Cancel", command = lambda : cancel())
            CancelButton.grid(row=(rows*len(selectables))+6, column=0, padx=5, pady=5)

            config_window_frame2.pack()

        config_window_canvas.create_window((0, 0), window = config_window_frame2, anchor = "nw")
        
        def confirm():
            save_current_plotables(globals()[f"PlotStylebox"].get(globals()[f"PlotStylebox"].curselection()))
            config_window.destroy()

        def cancel():
            global previously_selected_plotables
            global old_plotable_selection
            previously_selected_plotables = {k:[amgp.Factor().AsObject(F) for F in v] for (k, v) in literal_eval(old_plotable_selection.get()).items()}
            config_window.destroy()
            
        master_window.wait_window(config_window)

        return {k:[F.AsDict() for F in v] for (k, v) in previously_selected_plotables.items()}

    if literal_eval(selected_style.get()) != {}:
        selected_plotables.set(str(refresh_mapwin(master_window, selected_style, 0, 0, True)))
        #print(selected_plotables.get())
    else:
        UpdateStatusBox("Select a style before altering factors!")

def ConfigureMap(master_window, selected_map, selected_style):
    rows = 4

    if comp_data["key"] != None:
        uname = comp_data["key"].username
    else:
        uname = "An AMGP User"

    map_config = {
        "time": {
            "options": None,
            "description": "The base time(s) for which the map(s) should be made. Format should be 'YYYYmmdd-HH:MM:SS'. The keyword 'to' indicates the date before/after the keyword is the start/end of a range of dates (inclusive) and requires the keyword 'interval' followed by HH:MM:SS defining the interval of runs. The keyword 'recent' may be used in place of an individual or end date. String is delimited by whitespace.",
            "default": "recent",
            "selection": None
        },
        "time mode": {
            "options": ["sync", "async", "nearest", "raw"],
            "description": "The time mode utilized for plotting. Sync uses the most recent time that contains all of the requested data, async uses the most recent data as of the requested plot date, nearest uses the time of the most recent data requested, raw pulls data for exactly the time queried.",
            "default": ["async"],
            "multiselect": False,
            "selection": None
        },
        "layers": {
            "options": ["states", "coastlines", "lakes", "oceans", "country borders", "rivers"],
            "description": "The physical and geopolitical divions to display on any maps of Earth.",
            "default": ["states", "coastlines", "country borders"],
            "multiselect": True,
            "selection": None
        },
        #"scale": {
        #    "options": None,
        #    "description": "The relative scale of ploted objects.",
        #    "default": "1.3",
        #    "selection": None
        #},
        "image dpi": {
            "options": ["150", "250", "350"],
            "description": "The DPI of the resultant map.",
            "default": ["150"],
            "multiselect": False,
            "selection": None
        },
        "figure title": {
            "options": None,
            "description": "The central title of the figure; should be something descriptive, but brief.",
            "default": "A Figure",
            "selection": None
        },
        "append date to title": {
            "options": ["Yes", "No"],
            "description": "Yes tells AMGP to append the date of the figure to the left side of the central title above.",
            "default": ["Yes"],
            "multiselect": False,
            "selection": None
        },
        "username": {
            "options": None,
            "description": "The username of the current user, shown as the right title of the figure.",
            "default": uname,
            "selection": None
        }
    }

    global previously_selected_map
    global old_map_selection
    previously_selected_map = tk.StringVar()
    previously_selected_map.set(str({}))

    if literal_eval(selected_map.get()) != {}:
        previously_selected_map.set(selected_map.get())

    if len([k for (k, _) in literal_eval(previously_selected_map.get()).items()]) < literal_eval(selected_style.get())["axes"]:
        for i in range(len([k for (k, _) in literal_eval(previously_selected_map.get()).items()]), literal_eval(selected_style.get())["axes"]):
            tmp_prev_map = literal_eval(previously_selected_map.get())
            tmp_prev_map[i] = map_config
            previously_selected_map.set(str(tmp_prev_map))

    old_map_selection = tk.StringVar()
    old_map_selection.set(previously_selected_map.get())

    def save_current_selection(axis_index):
            map_config_result = map_config
            parameter_num = 0
            for param, attr in map_config_result.items():
                if attr["options"] == None:
                    map_config_result[f"{param}"]["selection"] = globals()[f"MapEntrybox{parameter_num}"].get()
                else:
                    map_config_result[f"{param}"]["selection"] = [globals()[f"MapChecklist{parameter_num}"].get(x) for x in globals()[f"MapChecklist{parameter_num}"].curselection()]

                parameter_num += 1
            
            tmp_prev_map = literal_eval(previously_selected_map.get())
            tmp_prev_map[axis_index] = map_config_result
            previously_selected_map.set(str(tmp_prev_map))

    def refresh_mapwin(master_window, selected_style, new_axis, old_axis, startup = False):
        global map_config_window
        if not startup:
            save_current_selection(old_axis)
            map_config_window.destroy()

        map_config_window = tk.Toplevel()
        map_config_window.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
        map_config_window.title(f"AMGP v{version} - Map Data Config Window")
        map_config_window.geometry("600x600")

        map_config_window_frame = tk.Frame(map_config_window)
        map_config_window_frame.pack(fill = tk.BOTH, expand = 1)

        global map_config_window_canvas
        map_config_window_canvas = tk.Canvas(map_config_window_frame)

        global map_config_window_frame2
        map_config_window_frame2 = tk.Frame(map_config_window_canvas, width = 600, height = 500)

        globals()[f"MapAxisDropbox"] = tk.Listbox(map_config_window_frame2, selectmode = tk.SINGLE, exportselection = False, height = 4)
        for style_index in range(0, literal_eval(selected_style.get())["axes"]):
            globals()[f"MapAxisDropbox"].insert(style_index, style_index)
        globals()[f"MapAxisDropbox"].select_set(new_axis)
        globals()[f"MapAxisDropbox"].grid(row = 0, column = 0)

        globals()[f"MapAxisDropboxButton"] = ttk.Button(map_config_window_frame2, text = "Change Axis", command = lambda : refresh_mapwin(master_window, selected_style, globals()[f"MapAxisDropbox"].get(globals()[f"MapAxisDropbox"].curselection()), new_axis))
        globals()[f"MapAxisDropboxButton"].grid(row = 0, column = 1)

        parameter_num = 0
        for param, attr in map_config.items():
            globals()[f"MapLabel{parameter_num}"] = ttk.Label(map_config_window_frame2, text = f"{param}", wraplength=300)
            globals()[f"MapLabel{parameter_num}"].grid(row=(rows*parameter_num)+1, column=0, padx=5, pady=5)
            globals()[f"MapLabel{parameter_num}2"] = ttk.Label(map_config_window_frame2, text = f"{attr['description']}", wraplength=300)
            globals()[f"MapLabel{parameter_num}2"].grid(row=(rows*parameter_num)+1, column=1, padx=5, pady=5)

            if attr["options"] == None:
                globals()[f"MapEntryboxResult{parameter_num}"] = tk.StringVar()
                if (param in ["time", "projection", "figure title", "username"]):
                    globals()[f"MapEntrybox{parameter_num}"] = ttk.Entry(map_config_window_frame2, textvariable = globals()[f"MapEntryboxResult{parameter_num}"], width=50)
                else:
                    globals()[f"MapEntrybox{parameter_num}"] = ttk.Entry(map_config_window_frame2, textvariable = globals()[f"MapEntryboxResult{parameter_num}"], width=10)
                if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"] == None:
                    if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"] != None:
                        # REPLICATE FOR PARAMETER ENTRYBOX
                        globals()[f"MapEntryboxResult{parameter_num}"].set(literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"])
                else:
                    globals()[f"MapEntryboxResult{parameter_num}"].set(literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"])
                globals()[f"MapEntrybox{parameter_num}"].grid(row=(rows*parameter_num)+2, column=1, padx=5, pady=5)
            else:
                if attr["multiselect"]:
                    globals()[f"MapChecklist{parameter_num}"] = tk.Listbox(map_config_window_frame2, selectmode = tk.MULTIPLE, exportselection = False, height = 4)
                    for item_index in range(0, len(attr["options"])):
                        globals()[f"MapChecklist{parameter_num}"].insert(item_index + 1, attr["options"][item_index])
                        if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"] == None:
                            if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"] != None:
                                if attr["options"][item_index] in literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"]:
                                    globals()[f"MapChecklist{parameter_num}"].select_set(item_index)
                        else:
                            if attr["options"][item_index] in literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"]:
                                globals()[f"MapChecklist{parameter_num}"].select_set(item_index)
                        globals()[f"MapChecklist{parameter_num}"].grid(row=(rows*parameter_num)+2, column=1, padx=5, pady=5)
                    globals()[f"MapChecklist{parameter_num}"].grid(row=(rows*parameter_num) + 2, column=1, padx=5, pady=5)
                else:
                    globals()[f"MapChecklist{parameter_num}"] = tk.Listbox(map_config_window_frame2, selectmode = tk.SINGLE, exportselection = False, height = 4)
                    for item_index in range(0, len(attr["options"])):
                        globals()[f"MapChecklist{parameter_num}"].insert(item_index + 1, attr["options"][item_index])
                        if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"] == None:
                            if literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"] != None:
                                if attr["options"][item_index] in literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["default"]:
                                    globals()[f"MapChecklist{parameter_num}"].select_set(item_index)
                        else:
                            if attr["options"][item_index] in literal_eval(previously_selected_map.get())[new_axis][f"{param}"]["selection"]:
                                globals()[f"MapChecklist{parameter_num}"].select_set(item_index)
                    globals()[f"MapChecklist{parameter_num}"].grid(row=(rows*parameter_num) + 2, column=1, padx=5, pady=5)
                
            parameter_num += 1

        ConfirmButton = ttk.Button(map_config_window_frame2, text = "Submit", command = lambda : confirm())
        ConfirmButton.grid(row=(rows*len([k for (k, _) in map_config.items()]))+4, column=0, padx=5, pady=5)

        CancelButton = ttk.Button(map_config_window_frame2, text = "Cancel", command = lambda : cancel())
        CancelButton.grid(row=(rows*len([k for (k, _) in map_config.items()]))+5, column=0, padx=5, pady=5)
        map_config_window_frame2.pack()

        map_config_window_scrollbar = tk.Scrollbar(map_config_window_frame, orient = tk.VERTICAL, command = map_config_window_canvas.yview)
        map_config_window_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        map_config_window_scrollbar2 = tk.Scrollbar(map_config_window_frame, orient = tk.HORIZONTAL, command = map_config_window_canvas.xview)
        map_config_window_scrollbar2.pack(side = tk.BOTTOM, fill = tk.X)

        map_config_window_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        map_config_window_canvas.configure(yscrollcommand = map_config_window_scrollbar.set)
        map_config_window_canvas.configure(xscrollcommand = map_config_window_scrollbar2.set)
        map_config_window_canvas.bind('<Configure>', lambda e: map_config_window_canvas.configure(scrollregion = map_config_window_canvas.bbox("all")))

        map_config_window_canvas.create_window((0, 0), window = map_config_window_frame2, anchor = "nw")

        def confirm():
            save_current_selection(globals()[f"MapAxisDropbox"].get(globals()[f"MapAxisDropbox"].curselection()))
            map_config_window.destroy()

        def cancel():
            global previously_selected_map
            global old_map_selection
            previously_selected_map.set(old_map_selection.get())
            map_config_window.destroy()
        
        master_window.wait_window(map_config_window)
        
        return literal_eval(previously_selected_map.get())
    
    if literal_eval(selected_style.get()) != {}:
        selected_map.set(str(refresh_mapwin(master_window, selected_style, 0, 0, True)))
    else:
        UpdateStatusBox("Select a style before altering map parameters!")

def ConfigureProjections(master_window, selected_projections, selected_style):
    rows = 4

    global previously_selected_projections
    global old_projection_selection
    previously_selected_projections = tk.StringVar()
    previously_selected_projections.set({})

    proj_options = {
        "projection": {
            "options": ["Lambert Conformal", "Plate Carree", "Robinson", "Geostationary", "Nearside Perspective", "None"],
            "description": "The base projection style, as defined within Cartopy.",
            "default": ["Lambert Conformal"],
            "selection": None,
            "multiselect": False
        },
        "central_longitude": {
            "options": None,
            "description": "The longitude where the projection is focused, in degrees [-180, 180].",
            "default": "-80",
            "selection": None
        },
        "central_latitude": {
            "options": None,
            "description": "The latitude where the projection is focused, in degrees [-90, 90].",
            "default": "45",
            "selection": None
        },
        "standard_parallel_1": {
            "options": None,
            "description": "The lines of latitude where the projection is the most accurate [-90, 90].",
            "default": "40",
            "selection": None
        },
        "standard_parallel_2": {
            "options": None,
            "description": "The lines of latitude where the projection is the most accurate [-90, 90].",
            "default": "50",
            "selection": None
        },
        "satellite_height": {
            "options": None,
            "description": "The height of the virtual satellite from which the projection is viewed.",
            "default": "35785831",
            "selection": None
        },
        "area": {
            "options": None,
            "description": "The geograpical area to center on; affects the display region, not the projection itself. Accepts the postal codes accepted by MetPy, as well as any custom-defined ones.",
            "default": "US",
            "selection": None
        }
    }

    if literal_eval(selected_projections.get()) != {}:
        previously_selected_projections.set(selected_projections.get())
    
    if len([k for (k, _) in literal_eval(previously_selected_projections.get()).items()]) < literal_eval(selected_style.get())["axes"]:
        tmp_prev_projs = literal_eval(previously_selected_projections.get())
        for i in range(len([k for (k, _) in literal_eval(previously_selected_projections.get()).items()]), literal_eval(selected_style.get())["axes"]):
            tmp_prev_projs[i] = proj_options
        previously_selected_projections.set(str(tmp_prev_projs))
    
    old_projection_selection = tk.StringVar()
    old_projection_selection.set(str(literal_eval(previously_selected_projections.get())))

    def save_current_selection(axis_index):
        global previously_selected_projections
        global proj_config_result
        proj_config_result = proj_options
        parameter_num = 0
        for param, attr in proj_config_result.items():
            if attr["options"] == None:
                proj_config_result[f"{param}"]["selection"] = globals()[f"ProjEntrybox{parameter_num}"].get()
            else:
                proj_config_result[f"{param}"]["selection"] = [globals()[f"ProjChecklist{parameter_num}"].get(x) for x in globals()[f"ProjChecklist{parameter_num}"].curselection()]
        
            parameter_num += 1
        
        tmp_prev_proj = literal_eval(previously_selected_projections.get())
        tmp_prev_proj[axis_index] = proj_config_result
        previously_selected_projections.set(str(tmp_prev_proj))
    
    def current_selection_dict():
        proj_config_test_output = proj_options
        parameter_num = 0
        for param, attr in proj_config_test_output.items():
            if attr["options"] == None:
                proj_config_test_output[f"{param}"]["selection"] = globals()[f"ProjEntrybox{parameter_num}"].get()
            else:
                proj_config_test_output[f"{param}"]["selection"] = [globals()[f"ProjChecklist{parameter_num}"].get(x) for x in globals()[f"ProjChecklist{parameter_num}"].curselection()]
        
            parameter_num += 1
        
        return proj_config_test_output

    def refresh_projwin(master_window, selected_style, new_axis, old_axis, startup = False):
        global proj_config_window
        if not startup:
            save_current_selection(old_axis)
            proj_config_window.destroy()
        
        proj_config_window = tk.Toplevel()
        proj_config_window.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
        proj_config_window.title(f"AMGP v{version} - Projection Config Window")
        proj_config_window.geometry("600x600")

        proj_config_window_frame = tk.Frame(proj_config_window)
        proj_config_window_frame.pack(fill = tk.BOTH, expand = 1)

        global proj_config_window_canvas
        proj_config_window_canvas = tk.Canvas(proj_config_window_frame)

        global proj_config_window_frame2
        proj_config_window_frame2 = tk.Frame(proj_config_window_canvas, width = 600, height = 600)

        globals()[f"ProjAxisDropbox"] = tk.Listbox(proj_config_window_frame2, selectmode = tk.SINGLE, exportselection = False, height = 4)
        for style_index in range(0, literal_eval(selected_style.get())["axes"]):
            globals()[f"ProjAxisDropbox"].insert(style_index, style_index)
        globals()[f"ProjAxisDropbox"].select_set(new_axis)
        globals()[f"ProjAxisDropbox"].grid(row = 0, column = 0)

        globals()[f"ProjAxisDropboxButton"] = ttk.Button(proj_config_window_frame2, text = "Change Axis", command = lambda : refresh_projwin(master_window, selected_style, globals()[f"ProjAxisDropbox"].get(globals()[f"MapAxisDropbox"].curselection(), new_axis)))
        globals()[f"ProjAxisDropboxButton"].grid(row = 0, column = 1)

        parameter_num = 0
        for param, attr in proj_options.items():
            globals()[f"ProjLabel{parameter_num}"] = ttk.Label(proj_config_window_frame2, text = f"{param}", wraplength = 300)
            globals()[f"ProjLabel{parameter_num}"].grid(row = (rows*parameter_num) + 1, column = 0, padx = 5, pady = 5)
            globals()[f"ProjLabel{parameter_num}2"] = ttk.Label(proj_config_window_frame2, text = f"{attr['description']}", wraplength = 300)
            globals()[f"ProjLabel{parameter_num}2"].grid(row = (rows*parameter_num) + 1, column = 1, padx = 5, pady = 5)

            if attr["options"] == None:
                globals()[f"ProjEntryboxResult{parameter_num}"] = tk.StringVar()
                globals()[f"ProjEntrybox{parameter_num}"] = ttk.Entry(proj_config_window_frame2, textvariable = globals()[f"ProjEntryboxResult{parameter_num}"], width = 25)
                if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"] == None:
                    if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"] != None:
                        globals()[f"ProjEntryboxResult{parameter_num}"].set(literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"])
                else:
                    globals()[f"ProjEntryboxResult{parameter_num}"].set(literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"])
                globals()[f"ProjEntrybox{parameter_num}"].grid(row = (rows*parameter_num) + 2, column = 1, padx = 5, pady = 5)
            else:
                if attr["multiselect"]:
                    globals()[f"ProjChecklist{parameter_num}"] = tk.Listbox(proj_config_window_frame2, selectmode = tk.MULTIPLE, exportselection = False, height = 4)
                    for item_index in range(0, len(attr["optins"])):
                        globals()[f"ProjChecklist{parameter_num}"].insert(item_index + 1, attr["options"][item_index])
                        if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"] == None:
                            if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"] != None:
                                if attr["options"][item_index] in literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"]:
                                    globals()[f"ProjChecklist{parameter_num}"].select_set(item_index)
                        else:
                            if attr["options"][item_index] in literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"]:
                                globals()[f"ProjChecklist{parameter_num}"].select_set(item_index)
                        globals()[f"ProjChecklist{parameter_num}"].grid(row=(rows*parameter_num)+2, column=1, padx=5, pady=5)
                    globals()[f"ProjChecklist{parameter_num}"].grid(row=(rows*parameter_num) + 2, column=1, padx=5, pady=5)
                else:
                    globals()[f"ProjChecklist{parameter_num}"] = tk.Listbox(proj_config_window_frame2, selectmode = tk.SINGLE, exportselection = False, height = 4)
                    for item_index in range(0, len(attr["options"])):
                        globals()[f"ProjChecklist{parameter_num}"].insert(item_index + 1, attr["options"][item_index])
                        if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"] == None:
                            if literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"] != None:
                                if attr["options"][item_index] in literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["default"]:
                                    globals()[f"ProjChecklist{parameter_num}"].select_set(item_index)
                        else:
                            if attr["options"][item_index] in literal_eval(previously_selected_projections.get())[new_axis][f"{param}"]["selection"]:
                                globals()[f"ProjChecklist{parameter_num}"].select_set(item_index)
                    globals()[f"ProjChecklist{parameter_num}"].grid(row=(rows*parameter_num) + 2, column=1, padx=5, pady=5)
            
            parameter_num += 1

        TestButton = ttk.Button(proj_config_window_frame2, text = "Test Projection", command = lambda : proj_win_image(amgp.TKIMG(amgpmap.Run(comp_data, [[]], {new_axis : {
        "time": {
            "options": None,
            "description": "The base time(s) for which the map(s) should be made. Format should be 'YYYYmmdd-HH:MM:SS'. The keyword 'to' indicates the date before/after the keyword is the start/end of a range of dates (inclusive) and requires the keyword 'interval' followed by HH:MM:SS defining the interval of runs. The keyword 'recent' may be used in place of an individual or end date. String is delimited by whitespace.",
            "default": "recent",
            "selection": "recent"
        },
        "time mode": {
            "options": ["sync", "async", "nearest", "raw"],
            "description": "The time mode utilized for plotting. Sync uses the most recent time that contains all of the requested data, async uses the most recent data as of the requested plot date, nearest uses the time of the most recent data requested, raw pulls data for exactly the time queried.",
            "default": ["async"],
            "multiselect": False,
            "selection": ["async"]
        },
        "layers": {
            "options": ["states", "coastlines", "lakes", "oceans", "country borders", "rivers"],
            "description": "The physical and geopolitical divions to display on any maps of Earth.",
            "default": ["states", "coastlines", "country borders"],
            "multiselect": True,
            "selection": ["states", "coastlines", "country borders"]
        },
        "scale": {
            "options": None,
            "description": "The relative scale of ploted objects.",
            "default": "1.3",
            "selection": "1.3"
        },
        "image dpi": {
            "options": ["150", "250", "350"],
            "description": "The DPI of the resultant map.",
            "default": ["150"],
            "multiselect": False,
            "selection": ["150"]
        },
        "figure title": {
            "options": None,
            "description": "The central title of the figure; should be something descriptive, but brief.",
            "default": "A Figure",
            "selection": "Projection Test"
        },
        "append date to title": {
            "options": ["Yes", "No"],
            "description": "Yes tells AMGP to append the date of the figure to the left side of the central title above.",
            "default": ["Yes"],
            "multiselect": False,
            "selection": ["No"]
        },
        "username": {
            "options": None,
            "description": "The username of the current user, shown as the right title of the figure.",
            "default": "",
            "selection": ""
        }
    }}, {new_axis:current_selection_dict()}, literal_eval(selected_style.get()), "./Temp/", True), (800, 600))))
        TestButton.grid(row = (rows*len([k for (k, _) in proj_options.items()])) + 4, column = 0, padx = 5, pady = 5)

        ConfirmButton = ttk.Button(proj_config_window_frame2, text = "Submit", command = lambda : confirm())
        ConfirmButton.grid(row = (rows*len([k for (k, _) in proj_options.items()])) + 5, column = 0, padx = 5, pady = 5)

        CancelButton = ttk.Button(proj_config_window_frame2, text = "Cancel", command = lambda : cancel())
        CancelButton.grid(row = (rows*len([k for (k, _) in proj_options.items()])) + 6, column = 0, padx = 5, pady = 5)
        proj_config_window_frame2.pack()

        proj_config_window_scrollbar = tk.Scrollbar(proj_config_window_frame, orient = tk.VERTICAL, command = proj_config_window_canvas.yview)
        proj_config_window_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        proj_config_window_scrollbar2 = tk.Scrollbar(proj_config_window_frame, orient = tk.HORIZONTAL, command = proj_config_window_canvas.xview)
        proj_config_window_scrollbar2.pack(side = tk.BOTTOM, fill = tk.X)

        proj_config_window_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        proj_config_window_canvas.configure(yscrollcommand = proj_config_window_scrollbar.set)
        proj_config_window_canvas.configure(xscrollcommand = proj_config_window_scrollbar2.set)
        proj_config_window_canvas.bind('<Configure>', lambda e: proj_config_window_canvas.configure(scrollregion = proj_config_window_canvas.bbox("all")))

        proj_config_window_canvas.create_window((0, 0), window = proj_config_window_frame2, anchor = "nw")
    
        def proj_win_image(image):
            proj_image = tk.Toplevel(proj_config_window)
            proj_image.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
            proj_image.title(f"AMGP v{version} - Projection Preview Window")
            proj_image.geometry("800x600")

            proj_image_frame = tk.Frame(proj_image, width = 800, height = 600)
            proj_image_frame.pack(fill = tk.BOTH, expand = 1)

            image_container = tk.Label(proj_image_frame, image = image, anchor = tk.CENTER)
            image_container.image = image
            image_container.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER)

            for im in glob.glob(f'{os.path.dirname(os.path.realpath(__file__).replace("ModulesCore", "Maps"))}{amgp.PathSep()}Temp{amgp.PathSep()}*'):
                os.remove(im) # Clean out the temp folder after running, since we've already produced a TKIMG and no longer need to keep the original in the temp folder
    
        def confirm():
            save_current_selection(globals()[f"ProjAxisDropbox"].get(globals()[f"ProjAxisDropbox"].curselection()))
            proj_config_window.destroy()
        
        def cancel():
            previously_selected_projections.set(old_projection_selection.get())
            proj_config_window.destroy()
    
        master_window.wait_window(proj_config_window)

        return literal_eval(previously_selected_projections.get())
    if literal_eval(selected_style.get()) != {}:
        selected_projections.set(str(refresh_projwin(master_window, selected_style, 0, 0, True)))
    else:
        UpdateStatusBox("Select a style before altering figure projections!")

def ConfigureSave(master_window, save_loc):
    def save_window(master_window):
        global save_window
        global save_loc
        save_window = tk.Toplevel()
        save_window.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
        save_window.title(f"AMGP v{version} - Plotable Config Window")
        save_window.geometry("600x600")

        global previous_save_loc
        previous_save_loc = tk.StringVar()
        previous_save_loc.set(save_loc.get())

        save_window_frame = tk.Frame(save_window)
        save_window_frame.pack(fill = tk.BOTH, expand = 1)

        global save_window_canvas
        save_window_canvas = tk.Canvas(save_window_frame)

        global save_window_frame2
        save_window_frame2 = tk.Frame(save_window_canvas, width = 600, height = 500)

        desc = tk.Label(save_window_frame2, text = "Leave the below blank if you'd like to use AMGP's default internal filesystem save locations within ./AMGP/Maps/\nIf you'd like custom save locations, there are a few custom wildcards that you can use in conjunction with an absolute path, or you can specify a relative path to create a new directory within the AMGP maps folder to construct a project directory.\nThe wildcards are as follows:\n'$Y' - 4-digit year\n'$m' - 0-padded month\n'$d' - 0-padded day of the month\n'$D' - The full date as in '$Y-$m-$d'\n'$t' - UTC time of data contained within the figure\n'$r' - AMGP instance runtime\n'$i' - Figure number, starting with 0\n'$n' - Figure number, starting with 1\nThe path './Temp/' will create the figures in a temp directory that will not be saved, but only displayed in the AMGP main window.", wraplength = 600)
        desc.grid(row = 0, column = 0, padx = 5, pady = 5)

        globals()["SaveLocEntryResult"] = tk.StringVar()
        globals()["SaveLocEntryResult"].set(previous_save_loc.get())
        globals()["SaveLocEntry"] = ttk.Entry(save_window_frame2, textvariable = globals()["SaveLocEntryResult"], width = 100)
        globals()["SaveLocEntry"].grid(row = 1, column = 0, padx = 5, pady = 5)

        conf_button = ttk.Button(save_window_frame2, text = "Confirm", command = lambda : confirm())
        conf_button.grid(row = 2, column = 0, padx = 5, pady = 5)

        quit_button = ttk.Button(save_window_frame2, text = "Cancel", command = lambda : cancel())
        quit_button.grid(row = 3, column = 0, padx = 5, pady = 5)

        save_window_frame2.pack()

        save_window_scrollbar = tk.Scrollbar(save_window_frame, orient = tk.VERTICAL, command = save_window_canvas.yview)
        save_window_scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

        save_window_scrollbar2 = tk.Scrollbar(save_window_frame, orient = tk.HORIZONTAL, command = save_window_canvas.xview)
        save_window_scrollbar2.pack(side = tk.BOTTOM, fill = tk.X)

        save_window_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

        save_window_canvas.configure(yscrollcommand = save_window_scrollbar.set)
        save_window_canvas.configure(xscrollcommand = save_window_scrollbar2.set)
        save_window_canvas.bind('<Configure>', lambda e: save_window_canvas.configure(scrollregion = save_window_canvas.bbox("all")))

        save_window_canvas.create_window((0, 0), window = save_window_frame2, anchor = "nw")

        def confirm():
            previous_save_loc.set(globals()["SaveLocEntry"].get())
            save_window.destroy()
        
        def cancel():
            save_window.destroy()
        
        master_window.wait_window(save_window)
        return previous_save_loc.get()
    
    save_loc.set(save_window(master_window))

def UpdatePresetListbox():
    global window
    global PresetListbox
    PresetListbox = tk.Listbox(window, selectmode = tk.SINGLE, exportselection = False, height = 4)
    preset_index = 0
    for preset in amgp.ListPresets("AMGP_MENU"):
        PresetListbox.insert(preset_index, preset)
        preset_index += 1
    PresetListbox.grid(row=12, column=1)

def UpdateStatusBox(message):
    global window
    global StatusBox
    StatusBox.destroy()
    StatusBox = tk.Label(window, text = message, wraplength = 180, justify = tk.CENTER)
    StatusBox.grid(row = 1, rowspan = 2, column = 1)

def UpdatePreviewImage(image):
    global internal_frame
    global PreviewImageContainer
    
    PreviewImageContainer.destroy()
    PreviewImageContainer = tk.Label(internal_frame, image = image, anchor = tk.CENTER)
    PreviewImageContainer.image = image
    PreviewImageContainer.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

def quit_program():
    global window
    window.destroy()
    sys.exit()

def Start():


    #----------------- <initialize> -------------------#

    #----------------- TK interface -------------------#

    global window
    window = tk.Tk()
    window.iconphoto(False, amgp.TKIMG(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}..{amgp.PathSep()}Resources{amgp.PathSep()}logo.png", (100, 100)))
    window.geometry("1080x720")
    window.title(f"Automated Map Generation Program v{version}")

    global selected_plotables
    selected_plotables = tk.StringVar()
    selected_plotables.set("{}")

    global selected_map
    selected_map = tk.StringVar()
    selected_map.set("{}")

    global selected_style
    selected_style = tk.StringVar()
    selected_style.set("{}")

    global selected_projections
    selected_projections = tk.StringVar()
    selected_projections.set("{}")

    global save_loc
    save_loc = tk.StringVar()
    save_loc.set("")

    #clock_label = ttk.Label(window, text='', font=("Arial", 32))
    #clock_label.grid(row=0, column=0)

    canvas_frame = tk.Frame(window, width = 900, height = 720)
    canvas_frame.grid(row=3, column=0, rowspan=18, sticky = "nsew")

    canvas = tk.Canvas(canvas_frame)

    #scrollbar = tk.Scrollbar(canvas_frame, orient = tk.VERTICAL, command = canvas.yview)
    #scrollbar.pack(side = tk.RIGHT, fill = tk.Y)

    #scrollbar2 = tk.Scrollbar(canvas_frame, orient = tk.HORIZONTAL, command = canvas.xview)
    #scrollbar2.pack(side = tk.BOTTOM, fill = tk.X)

    canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)

    #canvas.configure(yscrollcommand = scrollbar.set)
    #canvas.configure(xscrollcommand = scrollbar2.set)
    #canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    global internal_frame
    internal_frame = tk.Frame(canvas, width = 900, height = 638)

    global PreviewImageContainer
    preview_image = amgp.TKIMG(f'{os.path.dirname(os.path.realpath(__file__)).replace("ModulesCore", "Resources")}{amgp.PathSep()}logo.png', (900, 638))
    PreviewImageContainer = tk.Label(internal_frame, image = preview_image, anchor = tk.CENTER)
    PreviewImageContainer.image = preview_image
    PreviewImageContainer.place(relx=0.5,rely=0.5,anchor=tk.CENTER)

    canvas.create_window((0, 0), window = internal_frame, anchor = "nw")

    WelcomeMessage = ttk.Label(window, text = f"Automated Map Generation Program (AMGP) version {version}, copyright (c) 2022-2025, Samuel Nelson Bailey")
    WelcomeMessage.grid(row=1, column = 0)

    InfoMessage = ttk.Label(window, text = "For more information and guides on how to use and build your own modules, please visit https://github.com/sbailey04/AMGP, or click here!", foreground = "blue")
    InfoMessage.grid(row = 2, column = 0)
    InfoMessage.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/sbailey04/AMGP"))

    global StatusBox
    StatusBox = ttk.Label(window, text = "", wraplength = 180, justify = tk.CENTER)
    StatusBox.grid(row = 1, rowspan = 2, column = 1)

    global StyleListbox
    StyleListbox = tk.Listbox(window, selectmode = tk.SINGLE, exportselection = False, height = 4)
    style_index = 0
    for style in amgp.ListStyles():
        StyleListbox.insert(style_index, style)
        style_index += 1
    StyleListbox.grid(row=3, column=1)

    StyLoadButton = ttk.Button(window, text = "Load Above Style", command = lambda : InitStyle([StyleListbox.get(x) for x in StyleListbox.curselection()][0]))
    StyLoadButton.grid(row=4, column=1)

    ConfigButton = ttk.Button(window, text = "Configure Plotables", command = lambda : ConfigurePlotables(window, selected_plotables, selected_style))
    ConfigButton.grid(row=6, column=1)

    ProjButton = ttk.Button(window, text = "Configure Map Projections", command = lambda : ConfigureProjections(window, selected_projections, selected_style))
    ProjButton.grid(row=7, column=1)

    TimeButton = ttk.Button(window, text = "Configure Map Settings", command = lambda : ConfigureMap(window, selected_map, selected_style))
    TimeButton.grid(row=8, column=1)

    SaveLocButton = ttk.Button(window, text = "Configure Save Location", command = lambda : ConfigureSave(window, save_loc))
    SaveLocButton.grid(row=9, column=1)

    global PresetListbox
    PresetListbox = tk.Listbox(window, selectmode = tk.SINGLE, exportselection = False, height = 4)
    preset_index = 0
    for preset in amgp.ListPresets("AMGP_MENU"):
        PresetListbox.insert(preset_index, preset)
        preset_index += 1
    PresetListbox.grid(row=12, column=1)

    PSLoadButton = ttk.Button(window, text = "Load Above Preset", command = lambda : InitPreset([PresetListbox.get(x) for x in PresetListbox.curselection()][0]))
    PSLoadButton.grid(row=13, column=1)

    global PresetEntryboxVar
    PresetEntryboxVar = tk.StringVar()
    PresetEntrybox = ttk.Entry(window, textvariable = PresetEntryboxVar)
    PresetEntrybox.grid(row=15, column=1)

    PSSaveButton = ttk.Button(window, text = "Save Preset as Above", command = lambda : InitPresetSave(PresetEntryboxVar, selected_plotables, selected_projections, selected_map, selected_style))
    PSSaveButton.grid(row=16, column=1)

    StartButton = ttk.Button(window, text = "Run", command = lambda : RunFromInterface(selected_plotables, selected_map, selected_projections, selected_style, save_loc))
    StartButton.grid(row=18, column=1)

    window.grid_rowconfigure([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], minsize = 36)
    window.grid_columnconfigure(0, minsize = 900)
    window.grid_columnconfigure(1, minsize = 180)

    window.protocol("WM_DELETE_WINDOW", quit_program)

    #-----------------   TK loop    -------------------#
    #CurrentTime(window, clock_label)
    window.mainloop()
    