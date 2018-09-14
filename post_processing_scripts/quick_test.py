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

test_NWS_TEMP = "testdata/NWS/MetO-NWS-PHYS-hi-TEM.nc"
test_NWS_SALT = "testdata/NWS/MetO-NWS-PHYS-hi-SAL.nc"
test_NWS_CURR = "testdata/NWS/MetO-NWS-PHYS-hi-CUR.nc"
test_NWS_TBOT = "testdata/NWS/MetO-NWS-PHYS-dm-BED.nc"
test_NWS_MLD  = "testdata/NWS/MetO-NWS-PHYS-dm-MLD.nc"

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
                         "output": "mixed_layer_depth.nc"}
}
 

for script in schedule.keys():
    print 100*"-"
    print "executing: ", script
    cmd = script
    for key in ("args", "input", "output"):
        token = schedule[script][key]
        print " %s : %s" % (key, token)
        cmd = cmd + (" %s " % token)
    print ">",
    os.system(cmd)
    #print cmd,
    print "<",
    
