import json

with open("F:/assignment4_data/osm/fire_stations.geojson") as f:
    data = json.load(f)

coordinates=[]
for feature in data['features']:
    print (feature['geometry']['type'])
    print (feature['geometry']['coordinates'])
    if feature['geometry']['type']=='Polygon':
        coordinates.append(feature['geometry']['coordinates'][0][0])
    elif feature['geometry']['type']=='Point':
        coordinates.append(feature['geometry']['coordinates'][0:2])
    else:
        skip
print('STOP')
print(coordinates)
    
