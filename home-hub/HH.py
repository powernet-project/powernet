from google.cloud import pubsub
import urllib2
import json
# This is the start

class HomeHub(object):
    # Credentials
    # PUBSUB user key:
    PUBSUB_KEY = 'user_key'
    # Verification token for pubsub
    VERIFICATION_KEY = 'ver_key'
    # Weather API Key
    WEATHER_KEY = 'w_key'
    CITY = 'Menlo_Park'
    STATE = 'CA'
    URL = 'http://api.wunderground.com/api/'+WEATHER_KEY+'/geolookup/conditions/q/'+STATE+'/'+CITY+'.json'


    def __init__(self):
        self.ps = pubsub.Client()

    def hh_publish(self, value, topic):
        # if the value is not a string should I check for that case?
        # value = str(value)

        # converting data to utf-8
        data = [x.encode('utf-8') for x in value]
        self.ps.publish(data)

    def hh_subscribe(self, topic):
        # Need to define
        pass

    def hh_topic(self, topic_name):
        return self.ps.topic(topic_name)

    def hh_weather(self):
        topic = self.hh_topic('Weather')

        # Accessing weather undeground API
        f = urllib2.urlopen(self.URL)
        json_string = f.read()
        parsed_json = json.loads(json_string)
        temp_f = parsed_json['current_observation']['temp_f']
        humidity = parsed_json['current_observation']['relative_humudity']
        weather = parsed_json['current_observation']['weather']
        precipitation = parsed_json['current_observation']['precip_today_in']
        obs_time = parsed_json['current_observation']['observation_time_rfc822']

        value = [temp_f,humidity,weather,precipitation,obs_time]
        self.hh_publish(value, topic)

    def sensors(self):
        # Need to define
        pass

    def ui(self):
        # Need to define
        pass

    def utility(self):
        # Need to define
        pass

    def inverter(self):
        # Need to define
        pass
