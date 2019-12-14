#!/usr/bin/env python

import grass.script as gscript


def main():
    
    gscript.run_command('g.region', flags='p')
    
    #calculate hazard with weigthing factors of 1
    gscript.run_command('r.mapcalc', overwrite=True, expression='hazard=Reclass_fireprobability_per*1+Reclass_DEM_merged_slope*1+Reclass_landcover_per*1')

    #calculate risk (Reconsider that the distance to firestations in given in meters)
    gscript.run_command('r.mapcalc', overwrite=True, expression='risk=hazard*Reclass_buildings_per*Reclass_distFirestations_per')
    
    #BONUS
    gscript.run_command('r.mapcalc', overwrite=True, expression='risk_BONUS=hazard*Reclass_buildings_per*Reclass_isochrones_per')

if __name__ == '__main__':

    main()
