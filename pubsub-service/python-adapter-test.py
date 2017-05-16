from google.cloud import pubsub
import sys


ps = pubsub.Client()
topic = ps.topic('home-hub-message')

topic.publish('Testing python script and publishing from the cli')

print 'No Pub ISSUE encountered; exiting'

sys.exit()