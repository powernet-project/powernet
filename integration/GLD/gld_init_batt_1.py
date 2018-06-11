import os
import gridlabd_functions
import random
import pandas
import pycurl
import json
from StringIO import StringIO


#Get list of house objects in GLM file and assign to global GLD variable "houselist"
houses = gridlabd_functions.find('class=house')
houselist = [];

for house in houses :
	name = house['name']
	houselist.append(name) 
	
gridlabd_functions.set('houselist',';'.join(houselist))

#print(houselist)
