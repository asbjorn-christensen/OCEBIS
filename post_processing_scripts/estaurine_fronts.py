#!/usr/bin/env python
###################################################################################################
#
#   Postprocess CMEMS salinity time frames into estaurine front mask using GridWetData
#   Estaurine front zone is areas where
#                    PSU_min < PSU < PSU_max   eq.1
#
#   The map is assigned 1, where eq.1 is fulfilled, zero elsewhere
#   
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   usage: estaurine_fronts.py  <salinity-data>   < estaurine-front > 
#
#   
###################################################################################################


from GridWetData.CMEMS.NWS.NWS_grid_data  import *
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys

PSU_min = 32
PSU_max = 33.5

salt   = NWS_GridData_3DwithTime(sys.argv[1])
nt     = salt.get_number_of_frames()
nx     = salt.grid.nx
ny     = salt.grid.ny
nz     = salt.grid.nz
#
ncf  = netcdf.Dataset(sys.argv[2], "w")
info = {'variable_name':"estaurine_front",
                 'units':'1',
                 'time' : salt.ncfdata.ncf.variables["time"][:],
                 'long_name':'Surface estaurine front, characterized by %f PSU < salinity %f PSU' % (PSU_min, PSU_max)}
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    gd3d  = salt.load_frame(it)
    # --- generate surf-bott stratification ---
    surfsalt      = gd3d.get_surface_layer()
    is_estfront   = (PSU_min < surfsalt.data) & (surfsalt.data < PSU_max)
    surfsalt.data = where(is_estfront, 1.0, 0.0)
    #
    #plt.contourf(transpose(surfsalt.data))
    #plt.colorbar()
    #plt.show()
    # --- dump data ---
    g2d = surfsalt.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf,  surfsalt.data,  info, time_frame_number=it)
#
ncf.variables["time"].units = salt.ncfdata.ncf.variables["time"].units   # pass through
ncf.close()
# 
