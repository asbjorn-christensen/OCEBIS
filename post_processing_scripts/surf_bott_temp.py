#!/usr/bin/env python
###################################################################################################
#
#   Postprocess CMEMS temperature time frames into surface-bottom stratification
#   and the mixing front (gradient of surface-bottom stratification) using GridWetData
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   usage: surf_bott_temp.py  <temperature-data>   <surf-temperature>   <surf_bott_stratification>  <grad_surf_bott_stratification>
#
#   
###################################################################################################


from GridWetData.CMEMS.NWS.NWS_grid_data  import *
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys



# =================================================
# (1) surface-bottom stratification
# =================================================
# 

temp   = NWS_GridData_3DwithTime(sys.argv[1])
nt     = temp.get_number_of_frames()
nx     = temp.grid.nx
ny     = temp.grid.ny
nz     = temp.grid.nz
#
ncf_surftemp  = netcdf.Dataset(sys.argv[2], "w")
info_surftemp = {'variable_name':"surf_temp",
                 'units':'deg',
                 'time' : temp.ncfdata.ncf.variables["time"][:],
                 'long_name':'surface temperature'}
#
ncf_sbstrat  = netcdf.Dataset(sys.argv[3], "w")
info_sbstrat = {'variable_name':"sb_strat",
                 'units':'deg',
                 'time' : temp.ncfdata.ncf.variables["time"][:],
                 'long_name':'surface-bottom stratification'}
#
ncf_mixing  = netcdf.Dataset(sys.argv[4],  "w")
info_mixing = {'variable_name':"mixing_front",
              'units':'deg/m',
              'time' : temp.ncfdata.ncf.variables["time"][:],
              'long_name':'mixing front (evaluated as magnitude of gradient of surface-bottom stratification)'}
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    gd3d  = temp.load_frame(it)
    gsu      = gd3d.get_surface_layer()
    g2d      = gsu.grid.export_horizontal_grid()
    # --- export surface temp before processing ---
    g2d.write_data_as_COARDS(ncf_surftemp, gsu.data,  info_sbstrat, time_frame_number=it)
    # --- generate surf-bott stratification ---
    gbo      = gd3d.get_bottom_layer()
    gsu.data = gsu.data - gbo.data
    gsu.data = where(gd3d.grid.wetmask[:,:,0] == 0, 0, gsu.data)
    # --- generate front ---
    dgsu      = gsu.gradient()
    dgsu.data = sqrt(1e-20 + dgsu.data[0]**2 + dgsu.data[1]**2)
    dgsu.data = where(gd3d.grid.wetmask[:,:,0] == 0, 0, dgsu.data)
    #
    #plt.contourf(transpose(dgsu.data))
    #plt.colorbar()
    #plt.show()
    # --- dump data ---
    g2d.write_data_as_COARDS(ncf_sbstrat, gsu.data,  info_sbstrat, time_frame_number=it)
    g2d.write_data_as_COARDS(ncf_mixing,  dgsu.data, info_mixing,  time_frame_number=it)

#
ncf_surftemp.variables["time"].units = temp.ncfdata.ncf.variables["time"].units  # pass through
ncf_surftemp.close()
ncf_sbstrat.variables["time"].units = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_sbstrat.close()
ncf_mixing.variables["time"].units  = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_mixing.close()
# 
