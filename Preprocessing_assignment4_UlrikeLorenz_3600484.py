#!/usr/bin/env python

import grass.script as gscript



def main():
    
    
    #set path
    corine_path = 'C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/corine_landcover_2018/CLC2018_tarragona.tif'
    #print region
    gscript.run_command('g.region', flags='p')
    #adapt region to tarragona and set resolution to 10000m
    gscript.run_command('g.region', vector='tarragona_region@PERMANENT', res=1000)  


    #Import several files if projection differs a on-the-fly projection is done
    #import rasterfile CORINE Landcover
    gscript.run_command('r.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/corine_landcover_2018/CLC2018_tarragona.tif', output='Landcover')
    #import DEM and change projection on-the-fly
    gscript.run_command('r.import', title='DEM_N40E000', input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N40E000.SRTMGL1.hgt/N40E000.hgt', output='N40E000', overwrite=True)
    gscript.run_command('r.import', title='DEM_N41E000', input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N41E000.SRTMGL1.hgt/N41E000.hgt', output='N41E000', overwrite=True)
    gscript.run_command('r.import', title='DEM_N41E001', input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/dem/N41E001.SRTMGL1.hgt/N41E001.hgt', output='N41E001', overwrite=True)
    #import Wildfire incidents
    gscript.run_command('v.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/fire_incidents/fire_archive_V1_89293.shp', output='fire_incidents')        
    #import OSM-Data
    gscript.run_command('v.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/osm/buildings.geojson', output='buildings')
    gscript.run_command('v.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/osm/fire_stations.geojson', output='fire_stations')
    gscript.run_command('v.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/assignment4_data/assignment4_data/osm/tarragona_region.geojson', output='tarragona_region')
    

    #merge DEM to one file
    gscript.run_command('i.image.mosaic', overwrite=True, input= ['N40E000@risk_analysis', 'N41E000@risk_analysis', 'N41E001@risk_analysis'], output='DEM_merged')
    #calculate slope
    gscript.run_command('r.slope.aspect', overwrite=True, elevation='DEM_merged', slope='DEM_merged_slope', format='degrees', precision='FCELL')
    #reclass slope
    gscript.run_command('r.reclass', overwrite=True, input='DEM_merged_slope', output='Reclass_DEM_merged_slope', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_slope.txt')
    #make results permanent
    gscript.run_command('r.resample', overwrite=True, input='Reclass_DEM_merged_slope', output='Reclass_DEM_merged_per')

    
    #reclassify CORINE Landcover
    gscript.run_command('r.reclass', overwrite=True, input='Landcover', output='Reclass_Landcover', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_landcover.txt')
    #make results permanent
    gscript.run_command('r.resample', overwrite=True, input='Reclass_Landcover@risk_analysis', output='Reclass_landcover_per')

    #calculate probability for the ignition of a fire
    #create a region and set diameter for hexagons on 1000m
    gscript.run_command('g.region', res=1000, flags='pa')
    #create a hexagonal grid
    gscript.run_command('v.mkgrid', map='hexagons1', overwrite=True, flags='h')
    #count fire incidents within every hexagon
    gscript.run_command('v.vect.stats', points='fire_incidents@risk_analysis', areas='hexagons1', count_column='fire_count')
    #rasterize the result
    gscript.run_command('v.to.rast', input='hexagons1', overwrite=True, output='probability', use='attr', attribute_column='fire_count')
    

    #calculate with the raster to get the probability
    gscript.run_command('r.mapcalc', expression='fprobability = if (probability> 15, 15,probability * 100 / 15)')
    #reclassify with an txt-file
    gscript.run_command('r.reclass', overwrite=True, input='fprobability@risk_analysis', output='Reclass_fireprobability', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_fireprobability.txt')
    #make results permanent
    gscript.run_command('r.resample', overwrite=True, input='Reclass_fireprobability', output='Reclass_fireprobability_per')

    
    #exposure-resulting from information about buildings (explanations see above)
    gscript.run_command('g.region', res=1000, flags='pa')
    gscript.run_command('v.mkgrid', map='hexagons2', flags='h', overwrite=True)
    gscript.run_command('v.to.db', map='hexagons2', option='area', units='meters', columns='hex_area')
    #clip raster with hexagons to get the area with buildings
    gscript.run_command('v.clip', input='buildings@risk_analysis', clip='hexagons2', output='buildings_clip', overwrite=True)
    #calculate a column with the area in meters
    gscript.run_command('v.to.db', map='buildings_clip@risk_analysis', option='area', units='meters',columns='build_area')
    #rasterize to make the calculation possible
    gscript.run_command('v.to.rast', overwrite=True, input='buildings_clip', output='buildings_clip_rast', type='centroid', use='attr', attribute_column='build_area')
    #assuming that every hexagon has an area of 125000 squaremeters the percentage is calculaed
    gscript.run_command('r.mapcalc', expression='new_buildings = isnull(buildings_clip_rast)', overwrite=True)
    gscript.run_command('r.mapcalc', expression='new_buildings1 = if(new_buildings<1,(buildings_clip_rast/125000)*100, 0)', overwrite=True)
    #reclassification with txt-file
    gscript.run_command('r.reclass', overwrite=True, input='new_buildings1', output='Reclass_buildings', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_buildings.txt')
    #make results permanent
    gscript.run_command('r.resample', overwrite=True, input='Reclass_buildings', output='Reclass_buildings_per')

    
    #calculating proximity to fire stations

    #rasterize fire stations 
    gscript.run_command('v.to.rast', overwrite=True, input='fire_stations', output='fire_stations_rast', type='centroid', use='val', value=3)
    #calculate distance to raster-layer
    gscript.run_command('r.grow.distance', overwrite=True, input='fire_stations_rast', distance='distance_firestations')
    #group the values
    gscript.run_command('r.reclass', overwrite=True, input='distance_firestations', output='Reclass_distFirestations', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_distFirestationstxt.txt')
    gscript.run_command('r.resample', overwrite=True, input='Reclass_distFirestations', output='Reclass_distFirestations_per')

    

    #BONUS    #isochrones are gained by openroutservice and coordinates gained by a python script called BONUS.py
    gscript.run_command('v.import', overwrite=True, input='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/Isochrones_openrouteservice_n.geojson', output='isochrones')
    gscript.run_command('v.clip', overwrite=True, input='isochrones', clip='tarragona_region', output='isochrones_clip')
    gscript.run_command('v.mkgrid', map='hexagons3', flags='h', overwrite=True)
    gscript.run_command('v.clip', input='isochrones_clip', clip='hexagons3', output='isochrones_clip2', overwrite=True)
    gscript.run_command('v.to.rast', overwrite=True, input='isochrones_clip', output='isochrones_rast', type='centroid', use='attr', attribute_column='value')
    gscript.run_command('r.mapcalc', expression='new_isochrones = isnull(isochrones_rast)', overwrite=True)
    gscript.run_command('r.mapcalc', expression='new_isochrones1 = if(new_isochrones<1, isochrones_rast, 0)', overwrite=True)
    gscript.run_command('r.reclass', overwrite=True, input='new_isochrones1', output='Reclass_isochrones', rules='C:/Users/Ulrike/Desktop/Studium Heidelberg/1. Semester/FOSSGIS/fossgis_ws19_assignment4/rules_reclassification_isochrones.txt')
    gscript.run_command('r.resample', overwrite=True, input='Reclass_isochrones', output='Reclass_isochrones_per')
 
 
    
if __name__ == '__main__':
    main()
