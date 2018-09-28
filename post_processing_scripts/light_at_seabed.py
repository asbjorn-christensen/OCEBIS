#!/usr/bin/env python
##############################################################################################################
#
#   Generate logarithm of light at seabed as minus integral of ATTN (volume beam attenuation coefficient)
#
#   input  in CMEMS netcdf format   
#   output in COARDS netcdf format
#   
#   usage: light_at_seabed.py  < ATTN-data >   < log_light_at_seabed  >
#
##############################################################################################################
from GridWetData.CMEMS.NWS.NWS_grid_data  import *
from GridWetData.oceanography.water_column  import find_vertical_integral
import netCDF4  as netcdf
import matplotlib.pyplot as plt # debugging
import sys


data = NWS_GridData_3DwithTime(sys.argv[1])   # assumes prop attribute gets set
nt   = data.get_number_of_frames()
nx   = data.grid.nx
ny   = data.grid.ny
nz   = data.grid.nz
#
ncf_val  = netcdf.Dataset(sys.argv[2],  "w")
info_val = {'variable_name':"log_light_at_seabed",
            'units':'NA',    # hack
            'time' : data.ncfdata.ncf.variables["time"][:],
            'long_name':'logarithm of light at seabed as minus vertical integral of ATTN'}   
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
    #
    g2d = data_frame.grid.export_horizontal_grid()
    g2d.write_data_as_COARDS(ncf_val, -vert_intg, info_val, time_frame_number=it)
#
ncf_val.variables["time"].units  = data.ncfdata.ncf.variables["time"].units   # pass through
ncf_val.close()
# 
