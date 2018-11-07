import homeassistant.remote as remote
import sys

state = sys.argv[1]

api = remote.API('192.168.1.3', 'homeRP')

domain = 'switch'
service = "turn_" + state.lower()
switch_name = 'switch.aeotec_zw096_smart_switch_6_switch'
service_data = {"entity_id": switch_name}

remote.call_service(api, domain, service, service_data)  ##control switch
