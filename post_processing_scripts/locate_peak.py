#!/usr/bin/env python
###################################################################################################
#
#   Locate max value and depth-at-max in data time frames using GridWetData
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#
#   inherit variable name from input file
#   TODO transfer unit from input
#   
#   usage: locate_peak.py  < data >   < max_value >   < depth_at_max >
#
#   
###################################################################################################
from GridWetData.CMEMS.NWS.NWS_grid_data  import *
from GridWetData.oceanography.water_column  import find_maximum_value
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys


#


grad_threshold  = 0.002  # kg/m4  (stratification threshold) ??
depth_threshold = 100    # m      (max accepted depth of stratification)

data = NWS_GridData_3DwithTime(sys.argv[1])   # assumes prop attribute gets set
nt   = data.get_number_of_frames()
nx   = data.grid.nx
ny   = data.grid.ny
nz   = data.grid.nz
depth_data  = zeros((nt, nx, ny), float)
maxval_data = zeros((nt, nx, ny), float)
#
ncf_depth = netcdf.Dataset(sys.argv[2], "w")
info_depth = {'variable_name':"%s_depth" % data.prop,
              'units':'NA',    # hack
              'time' : data.ncfdata.ncf.variables["time"][:],
              'long_name':'Depth of vertical maximum of %s' % data.prop}
#
ncf_valmax  = netcdf.Dataset(sys.argv[3],  "w")
info_valmax = {'variable_name':"%s_max" % data.prop,
              'units':'NA',    # hack
              'time' : data.ncfdata.ncf.variables["time"][:],
              'long_name':'vertical maximum of %s' % data.prop}
#
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    data_frame  = data.load_frame(it)
    z     = reshape(data_frame.grid.ccdepth, (nx*ny, nz))
    y     = reshape(data_frame.data,         (nx*ny, nz))
    blay  = reshape(data_frame.grid.bottom_layer, nx*ny)   # assume in sync with salt
    #
    zmax, maxval    = find_maximum_value(z, y, blay)        # NB: density increases with depth
    #accept = (zmin < depth_threshold) & (gradmin > grad_threshold) # NB: density increases with depth 
    #zmin    = where(accept, zmin,    0.0)
    #gradmin = where(accept, gradmin, 0.0)
    
    g2d = data_frame.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf_depth,  reshape(zmax,   (nx,ny)), info_depth,  time_frame_number=it)
    g2d.write_data_as_COARDS(ncf_valmax, reshape(maxval, (nx,ny)), info_valmax, time_frame_number=it)
#
ncf_depth.variables["time"].units = data.ncfdata.ncf.variables["time"].units   # pass through
ncf_depth.close()
ncf_valmax.variables["time"].units  = data.ncfdata.ncf.variables["time"].units   # pass through
ncf_valmax.close()
# 
