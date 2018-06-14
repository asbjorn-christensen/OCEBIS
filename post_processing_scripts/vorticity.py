#!/usr/bin/env python
###################################################################################################
#
#   Postprocess CMEMS surface current time frames into vorticity (curl of current vectors) using GridWetData
#   
#   input  in CMEMS netcdf format (either TMB 3 layer format OR full layer resolution)  
#   output in COARDS netcdf format
#
#   usage: vorticity.py  <current-data>   < vorticity-data > 
#
#   
###################################################################################################


from GridWetData.CMEMS.NWS.NWS_grid_data  import *
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys

gv  = NWS_HorizontalCurrents_3DwithTime(sys.argv[1])
nt  = gv.get_number_of_frames()
nx  = gv.grid.nx
ny  = gv.grid.ny
nz  = gv.grid.nz
#
ncf  = netcdf.Dataset(sys.argv[2], "w")
info = {'variable_name':"vorticity",
                 'units':'1/sec',
                 'time' : gv.ncfdata.ncf.variables["time"][:],
                 'long_name':'Surface vorticity (curl of surface current vector field)'}
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    g3v = gv.load_frame(it)
    gsv  = g3v.get_surface_layer(setwetmask=True)
    curl = gsv.curl()
    #
    plt.contourf(transpose(curl.data))
    plt.colorbar()
    plt.show()
    # --- dump data ---
    curl.grid.write_data_as_COARDS(ncf,  curl.data,  info, time_frame_number=it)
#
ncf.variables["time"].units = gv.ncfdata.ncf.variables["time"].units   # pass through
ncf.close()
# 
