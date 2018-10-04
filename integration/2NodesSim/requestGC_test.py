import requests
import pickle
import json
import time


PWRNET_API_BASE_URL = 'http://pwrnet-158117.appspot.com/api/v1/'

soc = [0.05, 0.05]
r = requests.post(PWRNET_API_BASE_URL+'run_gc/', json={'q0':soc},timeout=60)
response_json = r.json()
print response_json
task_id = response_json['task_id']
i=0
time.sleep(10)

while(i<40):
    g = requests.get(PWRNET_API_BASE_URL+'gc_results/?task_id='+task_id)
    if g.status_code == 200:
      break
    i=i+1
    time.sleep(5)

response_json = g.json()

try:
    array_json = json.loads(response_json['result'])

except:
    print 'A Key error was generated from trying to deserialize the numpy array'

pricesCurrent = pickle.loads(array_json['pricesCurrent'])
print pricesCurrent
realS = pickle.loads(array_json['realS'])
print realS
LCtime = array_json['LCtime']
print LCtime
rampFlag = array_json['rampFlag']
print rampFlag
ramp_next = array_json['ramp_next']
print ramp_next
RstartList = pickle.loads(array_json['RstartList'])
print RstartList
QiList = pickle.loads(array_json['QiList'])
print QiList
RsignList = pickle.loads(array_json['RsignList'])
print RsignList
