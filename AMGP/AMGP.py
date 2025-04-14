###############################################################
#                                                             #
#        The Automated Map Generation Program ( AMGP )        #
#              © 2022-2025 Samuel Nelson Bailey               #
#           Distributed under the GPL-3.0 License             #
#                  Created on Mar 09, 2022                    #
#                                                             #
#                           AMGP.py                           #
#                     Author: Sam Bailey                      #
#                 Last Revised: Apr 14, 2025                  #
#                        Version: 1.0.0                       #
#                                                             #
###############################################################
#                                                             #
version = "1.0.0" #       AMGP Version                        #
#                                                             #
###############################################################
#                                                             #
#   Required Python packages for Core and Official Modules:   #
#   sys                                                       #
#   os                                                        #
#   importlib                                                 #
#   datetime                                                  #
#   tkinter                                                   #
#   ast                                                       #
#   glob                                                      #
#   webbrowser                                                #
#   math                                                      #
#   json                                                      #
#   cartopy                                                   #
#   pillow                                                    #
#   pickle                                                    #
#   numpy                                                     #
#   urllib                                                    #
#   metpy                                                     #
#   siphon                                                    #
#   pandas                                                    #
#   io                                                        #
#   xarray                                                    #
#   matplotlib                                                #
#                                                             #
###############################################################

from importlib import import_module

import os
import sys

from datetime import datetime, timezone

#import warnings
#warnings.filterwarnings('ignore', category=FutureWarning)
#warnings.filterwarnings('ignore', category=RuntimeWarning)
#warnings.filterwarnings('ignore', category=UserWarning)

#-----------------   <startup>  -------------------#

global runtime
runtime = datetime.now(timezone.utc)
#----------------- AMGP IMPORTS -------------------#
from ModulesCore import AMGP_UTIL as amgp
try:
    from ModulesCore import AMGP_UTIL as amgp
    if len(sys.argv) == 1:
        print("(AMGP) <startup> AMGP_UTIL.py imported as amgp")
except:
    sys.exit("(AMGP) <startup> ERROR: AMGP cannot function without the Utilities module. Please visit the AMGP GitHub for a replacement.")

try:
    from ModulesCore import AMGP_MAP as amgpmap
    if len(sys.argv) == 1:
        print("(AMGP) <startup> AMGP_MAP.py imported as amgpmap")
except:
    amgp.ThrowError("AMGP", "startup", 0, "AMGP cannot function without the Mapping module. Please visit the AMGP GitHub for a replacement.", runtime, False, True, True)

try:
    from ModulesCore import AMGP_MENU as amgpmenu
    if len(sys.argv) == 1:
        print("(AMGP) <startup> AMGP_MENU.py imported as amgpmenu")
except:
    amgp.ThrowError("AMGP", "startup", 0, "AMGP cannot function without the Menu module. Please visit the AMGP GitHub for a replacement.", runtime, False, True, True)

# Initialize the dictionaries of module objects and the priority:name dictionary
util_modules = {100:import_module("ModulesCore.AMGP_MAP"), 200:import_module("ModulesCore.AMGP_UTIL")}
data_modules = {}
menu_modules = {0:import_module("ModulesCore.AMGP_MENU")}
module_names = {0:"AMGP_MENU",100:"AMGP_MAP",200:"AMGP_UTIL"}
styles = {}

# Search the Official Modules directory for modules to import
for module in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}ModulesOfficial"):
    if module.startswith("AMGP_") and module.replace(".py", "") not in module_names.values():
        strp = module.replace(".py", "")
        var_name = strp.replace("_", "").lower()
        globals()[f"{var_name}"] = import_module(f"ModulesOfficial.{strp}")
        if len(sys.argv) == 1:
            print(f"(AMGP) <startup> {strp} imported as {var_name}")
        module_id = globals()[f"{var_name}"].Info()["uid"]
        if int(module_id[3:-4]) == 0:
            util_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            util_modules = dict(sorted(util_modules.items()))
        if int(module_id[3:-4]) == 1:
            data_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            data_modules = dict(sorted(data_modules.items()))
        if int(module_id[3:-4]) == 2:
            menu_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            menu_modules = dict(sorted(menu_modules.items()))
        # If combo modules are ever implemented again, this will handle their import
        #if int(module_id[3:-4]) == 3:
        #    combo_modules[int(module_id[4:])] = globals()[f"{var_name}"]
        #    combo_modules = dict(sorted(combo_modules.items()))

# The same as above for the User Modules folder
for module in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}ModulesUser"):
    if module.startswith("AMGP_") and module.replace(".py", "") not in module_names.values():
        strp = module.replace(".py", "")
        var_name = strp.replace("_", "").lower()
        globals()[f"{var_name}"] = import_module(f"ModulesUser.{strp}")
        if len(sys.argv) == 1:
            print(f"(AMGP_Main) <startup> {strp} imported as {var_name}")
        module_id = globals()[f"{var_name}"].Info()["uid"]
        if int(module_id[3:-4]) == 0:
            util_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            util_modules = dict(sorted(util_modules.items()))
        if int(module_id[3:-4]) == 1:
            data_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            data_modules = dict(sorted(data_modules.items()))
        if int(module_id[3:-4]) == 2:
            menu_modules[int(module_id[4:])] = globals()[f"{var_name}"]
            menu_modules = dict(sorted(menu_modules.items()))

# Due to the ordering of these calls, User Modules by design CAN override Official Modules,
# but this is not recommended unless you really know what you're doing.

for style_module in os.listdir(f"{os.path.dirname(os.path.realpath(__file__))}{amgp.PathSep()}Styles"):
    if style_module.endswith(".py"):
        strp = style_module.replace(".py", "")
        globals()[f"{strp}"] = import_module(f"Styles.{strp}")
        styles[strp] = globals()[f"{strp}"]

try:
    with open(f'.{amgp.PathSep()}Resources{amgp.PathSep()}{[f for f in os.listdir(f".{amgp.PathSep()}Resources") if f.endswith(".amgp")][0]}', "rb") as K:
        key = amgp.keytest(K)
        K.close()
except:
    key = None

if len(sys.argv) == 1:
    amgpmenu.InitWithInterface({
        "version":version,
        "util_modules":util_modules, # Type 0
        "data_modules":data_modules, # Type 1
        "menu_modules":menu_modules, # Type 2
        "module_names":module_names,
        "styles":styles,
        "runtime":runtime,
        "key":key
    })
else:
    if sys.argv[1].endswith(".json"):
        amgpmenu.InitWithoutInterface({
            "version":version,
            "util_modules":util_modules, # Type 0
            "data_modules":data_modules, # Type 1
            "menu_modules":menu_modules, # Type 2
            "module_names":module_names,
            "styles":styles,
            "runtime":runtime,
            "key":key
        },
        amgp.LoadPreset(sys.argv[1], None))
    elif sys.argv[1].endswith(".txt"):
        with open(sys.argv[1]) as f:
            for line in f.readlines():
                amgpmenu.InitWithoutInterface({
                    "version":version,
                    "util_modules":util_modules, # Type 0
                    "data_modules":data_modules, # Type 1
                    "menu_modules":menu_modules, # Type 2
                    "module_names":module_names,
                    "styles":styles,
                    "runtime":runtime,
                    "key":key
                },
                amgp.LoadPreset(line, None))
            f.close()
    elif sys.argv[1] == "--no-ui":
        flag = True
        print(f"AMGP v{version} Copyright (C) 2022-2025 Samuel Nelson Bailey\nThis program comes with ABSOLUTELY NO WARRANTY; for details see 'LICENSE.txt'.\nThis is free software, and you are welcome to redistribute it\nunder certain conditions; for details see 'LICENSE.txt'.")
        while flag:
            user_input = input("(AMGP) <run_w/o_interface> Type the absolute path to a preset.json file you'd like to run, or type 'exit' to quit: ")
            if user_input.lower().strip() == "exit":
                sys.exit()
            else:
                amgpmenu.InitWithoutInterface({
                    "version":version,
                    "util_modules":util_modules, # Type 0
                    "data_modules":data_modules, # Type 1
                    "menu_modules":menu_modules, # Type 2
                    "module_names":module_names,
                    "styles":styles,
                    "runtime":runtime,
                    "key":key
                },
                amgp.LoadPreset(user_input, None))