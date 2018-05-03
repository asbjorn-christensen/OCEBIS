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
depth_data = zeros((nt, nx, ny), float)
grad_data  = zeros((nt, nx, ny), float)
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
    z     = reshape(temp_frame.grid.ccdepth, (nx*ny, nz))
    t     = reshape(temp_frame.data,         (nx*ny, nz))
    s     = reshape(salt_frame.data,         (nx*ny, nz))  # assume in sync with temp
    blay  = reshape(temp_frame.grid.bottom_layer, nx*ny)   # assume in sync with salt
    rhow  = evaluate_water_density(z, s, t)   # shape (nx*ny, nz)
    # ------ plot surface density
    #rhowxyz = reshape(rhow, (nx, ny, nz))
    #plt.contourf(transpose(rhowxyz[:,:,0]))
    #plt.colorbar()
    #plt.show()
    #
    zmin, gradmin    = find_highest_gradient(z, rhow, blay)        # NB: density increases with depth
    accept = (zmin < depth_threshold) & (gradmin > grad_threshold) # NB: density increases with depth 
    zmin    = where(accept, zmin,    0.0)
    gradmin = where(accept, gradmin, 0.0)
    #
    #plt.contourf(transpose(reshape(zmin, (nx,ny))))
    #plt.contourf(transpose(reshape(gradmin, (nx,ny))))
    #plt.colorbar()
    #plt.show()
    g2d = temp_frame.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf_depth, reshape(zmin, (nx,ny)),   info_depth, time_frame_number=it)
    g2d.write_data_as_COARDS(ncf_grad, reshape(gradmin, (nx,ny)), info_grad,  time_frame_number=it)
#
ncf_depth.variables["time"].units = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_depth.close()
ncf_grad.variables["time"].units  = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_grad.close()
# 
