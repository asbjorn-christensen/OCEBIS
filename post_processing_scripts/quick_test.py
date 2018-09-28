#!/usr/bin/env python
###################################################################################################
#   -----------------------------------------------------------------------------------------------
#                             Quick test of script collection
#   -----------------------------------------------------------------------------------------------
#
#   ln -s /home/data/CMEMS  testdata
#   export PYTHONPATH=<PARENTDIR-OF-GridWetData>:${PYTHONPATH}
#   ncview data2D.nc
#   ncview *.nc
###################################################################################################
import os
import subprocess

test_NWS_TEMP = "testdata/NWS/MetO-NWS-PHYS-hi-TEM.nc"
test_NWS_SALT = "testdata/NWS/MetO-NWS-PHYS-hi-SAL.nc"
test_NWS_CURR = "testdata/NWS/MetO-NWS-PHYS-hi-CUR.nc"
test_NWS_TBOT = "testdata/NWS/MetO-NWS-PHYS-dm-BED.nc"
test_NWS_MLD  = "testdata/NWS/MetO-NWS-PHYS-dm-MLD.nc"
test_NWS_PHYT = "testdata/NWS/MetO-NWS-REAN-BIO-daily-PHYT.nc"
schedule = {
"density_strat.py" : {"args":   "",
                      "input":  test_NWS_TEMP + " " + test_NWS_SALT,
                      "output": "pycnocline_depth.nc  pycnocline_strength.nc"},
                      
"estaurine_fronts.py" : {"args":   "",
                         "input":  test_NWS_SALT,
                         "output": "estaurine_front.nc"},

"surf_bott_temp.py" : {"args":   "", 
                         "input":  test_NWS_TEMP,
                         "output": "surf_temperature.nc  surf_bott_stratification.nc  grad_surf_bott_stratification.nc"},
                         
"temp_strat.py" : {"args":   "",
                         "input":  test_NWS_TEMP,
                         "output": "stratification_depth.nc  stratification_strength.nc"},
                         
"vorticity.py" : {"args":   "",
                         "input":  test_NWS_CURR,
                         "output": "vorticity_data.nc"},
                         
"pass_through_BED.py" : {"args":   "",
                         "input":  test_NWS_TBOT,
                         "output": "bott_temperature.nc"},
                         
"pass_through_MLD.py" : {"args":   "",
                         "input":  test_NWS_MLD,
                         "output": "mixed_layer_depth.nc"},
                         
"locate_peak.py" : {"args":   "",
                         "input":  test_NWS_PHYT,
                         "output": "phyto_depth_at_max.nc phyto_vertical_max.nc"},                
}
 

for script in schedule.keys():
    cmd = script
    stem,ext = os.path.splitext(script)
    fh_err = open(stem+".stderr","w")
    fh_out = open(stem+".stdout","w")
    fh_out.write("executing: %s\n" % script)
    for key in ("args", "input", "output"):
        token = schedule[script][key]
        fh_out.write(" %s : %s\n" % (key, token))
        cmd = cmd + (" %s " % token)
    fh_out.write(100*"-" + "\n")
    fh_out.flush()
    retval = subprocess.call(cmd, bufsize=0,
                             stderr=fh_err,
                             stdout=fh_out,
                             shell=True)
    #fh_out.flush()
    #fh_out.close()
    
    #fh_err.close()
    if retval == 0:
        print "%s : success" % script
    else:
        print "%s : FAILED" % script
   
    
