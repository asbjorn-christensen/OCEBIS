#!/usr/bin/env python
###################################################################################################
#
#   Postprocess CMEMS temperature/salinity time frames into depth+strength of pycnocline using GridWetData
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   usage: density_strat.py  < temperature-data>  < salinity-data >   < pycnocline-depth >  < pycnocline-strength >
#
#   
###################################################################################################
from GridWetData.CMEMS.NWS.NWS_grid_data  import *
from GridWetData.oceanography.water_column  import find_highest_gradient, evaluate_water_density
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys


# =================================================
# (1) stratification indices
# =================================================


# --------------------------------------------------------------------------
# 1b) Density dependent indices of stratification:
#     Depth of lowest density-slope (i.e. that most toward negative value)
#     Value of lowest density-slope (i.e. that most toward negative value)
#     gradient; Considered as stratified in case of
#     vertical density gradient >0.02 kg /m*   ???
# --------------------------------------------------------------------------

grad_threshold  = 0.002  # kg/m4  (stratification threshold) ??
depth_threshold = 100    # m      (max accepted depth of stratification)

temp   = NWS_GridData_3DwithTime(sys.argv[1])
salt   = NWS_GridData_3DwithTime(sys.argv[2]) # in sync with temp
nt     = temp.get_number_of_frames()
nx     = temp.grid.nx
ny     = temp.grid.ny
nz     = temp.grid.nz
#
ncf_depth = netcdf.Dataset(sys.argv[3], "w")
info_depth = {'variable_name':"strat_depth",
              'units':'m',
              'time' : temp.ncfdata.ncf.variables["time"][:],
              'long_name':'Depth of pycnocline'}
#
ncf_grad  = netcdf.Dataset(sys.argv[4],  "w")
info_grad = {'variable_name':"strat_grad",
              'units':'kg/m4',
              'time' : temp.ncfdata.ncf.variables["time"][:],
              'long_name':'max denity gradient'}
#
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    temp_frame  = temp.load_frame(it)
    salt_frame  = salt.load_frame(it)
    # --- loop over water columns ---
    zmin     = zeros((nx,ny), float)
    gradmin  = zeros((nx,ny), float)
    for ix in range(nx):
        for iy in range(ny):
            ib = temp_frame.grid.bottom_layer[ix,iy]    # short hand, assume temp+salt in sync
            if ib<0:                                    # skip land points
                continue
            z  = temp_frame.grid.ccdepth[ix,iy,:(ib+1)] # short hand
            t  = temp_frame.data[ix,iy,:(ib+1)]         # short hand
            s  = salt_frame.data[ix,iy,:(ib+1)]         # short hand  
            rhow  = evaluate_water_density(z, s, t)     # shape (nz,)
            zmin[ix,iy], gradmin[ix,iy] = find_highest_gradient(z, rhow, ib)  # NB: density increases with depth
    #        
    # --- whole array checks  ---
    #
    accept = (zmin < depth_threshold) & (gradmin > grad_threshold) # NB: density increases with depth 
    zmin    = where(accept, zmin,    0.0)
    gradmin = where(accept, gradmin, 0.0)
    #
    #plt.contourf(transpose(reshape(zmin, (nx,ny))))
    #plt.contourf(transpose(reshape(gradmin, (nx,ny))))
    #plt.colorbar()
    #plt.show()
    g2d = temp_frame.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf_depth, zmin,   info_depth, time_frame_number=it)
    g2d.write_data_as_COARDS(ncf_grad,  gradmin, info_grad,  time_frame_number=it)
    #if it==2: break
#
ncf_depth.variables["time"].units = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_depth.close()
ncf_grad.variables["time"].units  = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_grad.close()
# 
