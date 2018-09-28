#!/usr/bin/env python
###################################################################################################
#
#   Postprocess CMEMS temperature time frames into stratification depth+strength using GridWetData
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   usage: temp_strat.py  < temperature-data>   < stratification-depth >  < stratification-strength >
#
#   
###################################################################################################


from GridWetData.CMEMS.NWS.NWS_grid_data  import *
from GridWetData.oceanography.water_column  import find_lowest_gradient
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys



# =================================================
# (1) stratification indices
# =================================================
# --------------------------------------------------------------------------
# 1a) Temperature dependent indices of stratification:
#     Depth of lowest temperature slope (i.e. that most toward negative value)
#     Value of lowest temperature slope (i.e. that most toward negative value)
# --------------------------------------------------------------------------

grad_threshold = 0.1   # deg/m  (stratification threshold)
depth_threshold = 1000 # m      (max accepted depth of stratification)

temp   = NWS_GridData_3DwithTime(sys.argv[1])
nt     = temp.get_number_of_frames()
nx     = temp.grid.nx
ny     = temp.grid.ny
nz     = temp.grid.nz
#
ncf_depth = netcdf.Dataset(sys.argv[2], "w")
info_depth = {'variable_name':"strat_depth",
              'units':'m',
              'time' : temp.ncfdata.ncf.variables["time"][:],
              'long_name':'Depth of max temperature gradient'}
#
ncf_grad  = netcdf.Dataset(sys.argv[3],  "w")
info_grad = {'variable_name':"strat_grad",
              'units':'deg/m',
              'time' : temp.ncfdata.ncf.variables["time"][:],
              'long_name':'max temperature gradient'}
#
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    gd3d  = temp.load_frame(it)

    zmin     = zeros((nx,ny), float)
    gradmin  = zeros((nx,ny), float)
    for ix in range(nx):
        for iy in range(ny):
            ib = gd3d.grid.bottom_layer[ix,iy]    # short hand, assume temp+salt in sync
            if ib<0:                                    # skip land points
                continue
            z  = gd3d.grid.ccdepth[ix,iy,:(ib+1)] # short hand
            y  = gd3d.data[ix,iy,:(ib+1)]         # short hand
            zmin[ix,iy], gradmin[ix,iy] = find_lowest_gradient(z, y, ib)
    #        
    # --- whole array checks  ---
    #
    accept = (zmin < depth_threshold) & (gradmin < -grad_threshold)
    zmin    = where(accept, zmin,    0.0)
    gradmin = where(accept, gradmin, 0.0)
    #plt.hist(zmin)
    #plt.show()
    #plt.contourf(transpose(reshape(zmin, (nx,ny))))
    #plt.contourf(transpose(reshape(-gradmin, (nx,ny))))
    #plt.colorbar()
    #plt.show()
    g2d = gd3d.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf_depth, reshape(zmin, (nx,ny)),   info_depth, time_frame_number=it)
    g2d.write_data_as_COARDS(ncf_grad, reshape(gradmin, (nx,ny)), info_grad,  time_frame_number=it)
    #if it==3: break
#
ncf_depth.variables["time"].units = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_depth.close()
ncf_grad.variables["time"].units  = temp.ncfdata.ncf.variables["time"].units   # pass through
ncf_grad.close()
# 
