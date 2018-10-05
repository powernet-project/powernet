import os
import pycurl
from StringIO import StringIO
import json


###############################################################################
# GET
###############################################################################
def get(name,property=[]) :
	""" Get a GridLAB-D global variables or object properties
	
	Syntax:
		get(global-name): get the value of a global variable
		get(object-name,property): get the value of an object property
		get(object-name,'*'): get all the properties of an object
	
	Arguments:
		global-name(string): the name of the global variable
		object-name(string): the name of the object
		property(string): the name of the object property ([] for globals)
	
	Returns:
		When a global variable value is obtained, the result is returned
		as a list containing the following entities:
		{	u'<name>': u'<value>' }
		where <name> is the name of the global variable, and <value> is the
		value of the global variable.
		
		When a list of object properties is obtained, the result is returned
		as a list containing the following entities:
		{
			u'<property_1>': u'<value_1>',
			u'<property_2>': u'<value_2>',
			...
			u'<property_N>': u'<value_N>',
		}
		where <property_n> is the name of the nth property, and <value_n> is
		the value of the nth property.
		
		When a single value is obtained for an object property, the result 
		is returned as a list containing the following entities:
		{	u'object': u'<name>',
			u'type': u'<type>',
			u'name': u'<property>',
			u'value': u'<value>'
		}
		where <name> is the name of the object or global variable, <type> is
		the GridLAB-D property type, <property> is the name of the property
		
		When an error is encountered, the return list will include the "error"
		property, with the remaining properties describing the nature and 
		origin of the error.
	"""
	buffer = StringIO()
	c = pycurl.Curl()
	if property == [] : # global property get
		c.setopt(c.URL,'http://localhost:6267/json/{}'.format(name))
	elif property == '*' : # object property get all
			c.setopt(c.URL,'http://localhost:6267/json/{}/*[dict]'.format(name))
	else : # object property get
		c.setopt(c.URL,'http://localhost:6267/json/{}/{}'.format(name,property))
	c.setopt(c.WRITEFUNCTION,buffer.write)
	c.perform()
	c.close()
	body = buffer.getvalue()
	#return body
	return json.loads(body)

###############################################################################
### GET UTILITIES
###############################################################################

def get_double(data,key) :
	try :
		value = data[key].split(' ')
		return float(value[0])
	except :
		print "ERROR: can't find double value for key='{}'".format(key)

def get_str(data,key) :
	try :
		value = data[key].split(' ')
		return value
	except :
		print "ERROR: can't find double value for key='{}'".format(key)


###############################################################################
# SET
###############################################################################
def set(name,property,value=[]) :
	""" Set a GridLAB-D global variable or object property
	
	Syntax:
		set(global-name,value): set a global variable
		set(object-name,property,value): set a property of a object
	
	Arguments:
		global-name(string): the name of a global variable
	
	Returns:
		When the set() command is successful, the previous value of the global 
		variable or object property is returned in the same format as the 
		get() command. 
		
		When an error is encountered, the return list will include the "error"
		property, with the remaining properties describing the nature and 
		origin of the error.
	"""
	buffer = StringIO()
	c = pycurl.Curl()
	if value == [] : # global property set
		c.setopt(c.URL,'http://localhost:6267/json/{}={}'.format(name,property))
	else : # object property set
		c.setopt(c.URL,'http://localhost:6267/json/{}/{}={}'.format(name,property,value))
	c.setopt(c.WRITEFUNCTION,buffer.write)
	c.perform()
	c.close()
	body = buffer.getvalue()
	return json.loads(body)


###################################################################################
### FIND
####################################################################################

def find(search) :
	""" GridLAB-D object search command
	
	Syntax: 
		find(filter)
		
	Arguments:
		filter(string): search filter, see 
			http://gridlab-d.shoutwiki.com/wiki/Collections for details
	
	Returns:
		When the query succeed a list of object names is returned.
	"""
	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL,'http://localhost:6267/find/{}'.format(search))
	c.setopt(c.WRITEFUNCTION,buffer.write)
	c.perform()
	c.close()
	body = buffer.getvalue()
	return json.loads(body)


#######################################################################################
### GET BLOCKS
#######################################################################################


def get_blocks(objects,prop):

	"""
	Get property data from multiple GridLAB-D objects at once
	Request is limited to 1024 characters (20-30 objects)

	objects is a vector of object names to get a single property from
	property is the property that you would like to query for all objects
	returns data in json format
	"""

	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL,'http://localhost:6267/read/{}'.format(";".join([m+"."+prop for m in objects])))
	c.setopt(c.WRITEFUNCTION,buffer.write)
	c.perform()
	c.close()
	body = buffer.getvalue()
	return json.loads(body)


######################################################################################
#### GET BLOCKS UTILITIES
######################################################################################

def get_blocks_double(data,obj):
	"""
	Get double value corresponding to specific object for the data from a get_blocks() call
	"""

	try :
		for i in range(len(data)):
			if obj in data[i].values():
				value = data[i]['value'].split(' ')
		return float(value[0])
	except :
		print "ERROR: can't find double value for object='{}'".format(obj)


######################################################################################
#### SET BLOCKS
######################################################################################

def set_blocks(objects,prop,values):
	"""
	Set property data for multiple GridLAB-D objects at once
	Request is limited to 1024 characters (20-30 objects)

	objects is a vector of object names to set a single property for
	property is the property you would like to set
	values is a vector of values that correpond to the property of the objects you are setting
	"""

	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL,'http://localhost:6267/modify/{}'.format(";".join([objects[m]+"."+prop+"="+str(values[m]) for m in range(len(objects))])))
	c.setopt(c.WRITEFUNCTION,buffer.write)
	c.perform()
	c.close()
	body = buffer.getvalue()
