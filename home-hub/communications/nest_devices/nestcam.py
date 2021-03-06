import hashlib
import json
import os
import requests

url = "https://developer-api.nest.com/devices/cameras/N1PqCOcwRDGgmz-KU4_-CKLtPslOTzv3qKhzo1E---da3VyVBPcb0Q"

token = "c.I6H8WCo1mRAZroVIpGqEKoxAatrX59fGc6zFX3uk7bgHOj5CNC8v75gOmITYEE1IQgyc9EmAYyigvoIRNGoMAGL9c2njdlXXccJ2zmq8lqojBsfG0nPdrw2UcIdoRvG1Xqf8UBQxQMmW22L9" # Update with your token

# Change state for user input in the API
# state = "OFF"
state = "ON"
# true and false needs to be boolean (for nest api)
payload_true = "{\"is_streaming\": true}"
payload_false = "{\"is_streaming\": false}"

headers = {'Authorization': 'Bearer {0}'.format(token), 'Content-Type': 'application/json'}

# This is for the case when we are doing the long polling
if state == "ON":
    response = requests.put(url, headers=headers, data=payload_true, allow_redirects=False)
    if response.status_code == 307: # indicates a redirect is needed
        response = requests.put(response.headers['Location'], headers=headers, data=payload_true, allow_redirects=False)

elif state == "OFF":
    response = requests.put(url, headers=headers, data=payload_false, allow_redirects=False)
    if response.status_code == 307: # indicates a redirect is needed
        response = requests.put(response.headers['Location'], headers=headers, data=payload_false, allow_redirects=False)
else:
    print "Do nothing..."
    pass
print(response.text)

# This is the code to get camera status
url2 = "https://developer-api.nest.com/devices/cameras/N1PqCOcwRDGgmz-KU4_-CKLtPslOTzv3qKhzo1E---da3VyVBPcb0Q/is_streaming"
response2 = requests.get(url2, headers=headers, allow_redirects=False)
if response2.status_code == 307:
    response2 = requests.get(response2.headers['Location'], headers=headers, allow_redirects=False)

# print response.text["cameras"]["name"]["device_id"]
print response2.text