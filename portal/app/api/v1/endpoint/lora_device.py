from rest_framework.authentication import BasicAuthentication
from app.api.v1 import CsrfExemptAuth
from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import FarmDevice
import json


class LoraDeviceViewSet(APIView):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)

    def dataparsing(self, data):
        try:
            temperature = data['event_data']['payload'][2]['value']
            rel_humidity = data['event_data']['payload'][3]['value']
            batt_value = data['event_data']['payload'][4]['value']
            timestamp = data['event_data']['timestamp']
            dev_internal_id = data['device']['id']
            device_uid = data['device']['thing_name'][1:3]
            return [device_uid, json.dumps({'temperature': temperature, 'rel_humidity': rel_humidity, 'batt_value': batt_value,
                           'dev_internal_id': dev_internal_id,'timestamp': timestamp})]
        except Exception as e:
            print('Error in Lora dataparsing: ', e)
            return None

    def post(self, request):
        try:
            lora_data = self.dataparsing(request.data)
        except Exception as e:
            lora_data = None
            print('Error: ', e)

        if lora_data is not None:
            try:
                lora_device = FarmDevice.objects.get(device_uid=lora_data[0])
                lora_device.device_data = lora_data[1]
                lora_device.save()
                print('saving...\n', lora_device)
                return Response({'message': 'dev_id {} and data {}'.format(lora_data[0], lora_data[1])})
            except FarmDevice.DoesNotExist as e:
                print('Error update_battery_status', e)
                return Response({'Error':'Somehting went wrong with Lora request'})



