import xarray as xr
import metpy
from datetime import datetime

ds = xr.open_dataset(f'https://thredds.ucar.edu/thredds/dodsC/grib/NCEP/GFS/Global_onedeg/GFS_Global_onedeg_20231030_0000.grib2').metpy.parse_cf()

print(ds["Temperature_height_above_ground"])