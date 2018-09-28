#!/usr/bin/env python
###################################################################################################
#
#   Generate a bloom index as d/dt(vertically integrated PPRD) using GridWetData
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#   
#   usage: bloom_index.py  < PPRD-data >   < bloom-index >
#
#   TODO: fix integer time -> float time, corresponding to center point
###################################################################################################
from GridWetData.CMEMS.NWS.NWS_grid_data  import *
from GridWetData.oceanography.water_column  import find_vertical_integral
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging

import sys


#
data = NWS_GridData_3DwithTime(sys.argv[1])   # assumes prop attribute gets set
nt   = data.get_number_of_frames()
nx   = data.grid.nx
ny   = data.grid.ny
nz   = data.grid.nz
#

#
time_input = data.ncfdata.ncf.variables["time"][:]
time_output = 0.5*(time_input[:-1] + time_input[1:] ) # assign to time mid points to have a centered difference
ncf_val  = netcdf.Dataset(sys.argv[2],  "w")
info_val = {'variable_name':"bloom_index",
              'units':'1/day',    # hack
              'time' : time_output,
              'long_name':'bloom index as d/dt(vertically integrated PPRD)'}
#
#
# --- scan over time frames in file
#
for it in range(nt):
    print "%d / %d" % (it+1,nt)
    data_frame  = data.load_frame(it)
    # --- loop over water columns ---
    vert_intg  = zeros((nx,ny), float)
    for ix in range(nx):
        for iy in range(ny):
            ib = data_frame.grid.bottom_layer[ix,iy]    # short hand, assume temp+salt in sync
            if ib<0:                                    # skip land points
                continue
            z  = data_frame.grid.ccdepth[ix,iy,:(ib+1)] # short hand
            cw = data_frame.grid.cellw[ix,iy,:(ib+1)]   # short hand
            y  = data_frame.data[ix,iy,:(ib+1)]         # short hand
            vert_intg[ix,iy] = find_vertical_integral(z, y, cw, ib)
    if it==0:
        vert_intg_last = vert_intg
        continue
    #
    g2d = data_frame.grid.export_horizontal_grid()
    bloom = vert_intg - vert_intg_last
    g2d.write_data_as_COARDS(ncf_val, bloom, info_val, time_frame_number=it-1) # starts writing at it==1
    vert_intg_last = vert_intg # roll integrals
#
ncf_val.variables["time"].units  = data.ncfdata.ncf.variables["time"].units   # pass through
ncf_val.close()
# 
