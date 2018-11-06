import requests
import copy
import json

PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'
REQUEST_TIMEOUT = 10

device = {
    "status": None,
    "name": None,
    "type": None,
    "value": None,
    "home": None,
    "cosphi": None
}


house_name = "HHLab"
house_id = 3
house_devstatus = 'OFF'

def dev_init():
    # dev_info = {"id": 48, "name": "Test_Dev", "type": "AIR_CONDITIONER", "status": "OFF", "value": 0, "cosphi": 1.0, "home": 2}
    # r_post_rms = requests.post(self.PWRNET_API_BASE_URL + "device/", json=dev_info, timeout=self.REQUEST_TIMEOUT)
    dev_status = requests.get(PWRNET_API_BASE_URL + "device", timeout=REQUEST_TIMEOUT).json()["results"]
    h_list = []
    for h in dev_status:
        h_list.append(h['home'])
    h_list = list(set(h_list))
    exist_hh = 3 in h_list
    if exist_hh == True:
        print 'dont create devices'
    else:
        print 'create devices'
        create_devices(8)

def create_devices(number_of_devices):
    for i in range(number_of_devices+1)[1:]:
        dev = copy.deepcopy(device)
        dev['name'] = house_name+str(house_id)+'_dev'+str(i)
        dev['home'] = house_id
        dev['status'] = house_devstatus
        dev['type'] = "SDF"
        dev['value'] = 0
        dev['cosphi'] = 1.0
        # headers = {"media-type": "application/json"}
        json_dev = json.dumps(dev)
        print 'dev: ', dev
        # print json_dev
        print 'json_dev: ', json_dev
        r_post_rms = requests.post(url = PWRNET_API_BASE_URL + "device/", json=dev, timeout=REQUEST_TIMEOUT)
        print "status code", r_post_rms.status_code
        if r_post_rms.status_code == 201:
            print 'request was successful'
        else:
            print 'request not successful'
            print 
        
if __name__=='__main__':
    try:
        dev_init()
    except Exception as exc:
        print exc