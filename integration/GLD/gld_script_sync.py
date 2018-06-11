import gridlabd_functions
import os


houses = gridlabd_functions.get('houselist')

#print(houses)

#print(houses['houselist'].split(';'))
prop="air_temperature"
objects=houses['houselist'].split(';')
data=gridlabd_functions.get_blocks(objects,prop)

house_key=objects[5]

print(gridlabd_functions.get_blocks_double(data,house_key))
print(os.getenv("clock"))

