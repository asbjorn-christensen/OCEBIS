#!/usr/bin/env python
###################################################################################################
#
#   Pass through layers directly from CMEMS (mixed-layer depth)
#   
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   usage: pass_through_MLD.py  <MLD-data>  <MLD-data-out>  
#
#   
###################################################################################################


from GridWetData.CMEMS.NWS.NWS_grid_data  import *
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys


data   = NWS_GridData_2DwithTime(sys.argv[1], get_wetmask=True)
nt     = data.get_number_of_frames()
nx     = data.grid.nx
ny     = data.grid.ny
#
ncf  = netcdf.Dataset(sys.argv[2], "w")
info = {'variable_name':"mld",
                 'units':'m',
                 'time' : data.ncfdata.ncf.variables["time"][:],
                 'long_name':'Mixed layer depth'}
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    gd2d  = data.load_frame(it)
    gd2d.data = where(gd2d.grid.wetmask == 1,  gd2d.data,  0)
    #
    #plt.contourf(transpose(gd2d.data))
    #plt.colorbar()
    #plt.show()
    #
    gd2d.grid.write_data_as_COARDS(ncf,  gd2d.data,  info, time_frame_number=it)
#
ncf.variables["time"].units = data.ncfdata.ncf.variables["time"].units   # pass through
ncf.close()
# 
