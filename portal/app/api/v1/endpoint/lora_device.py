from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from app.api.v1 import CsrfExemptAuth
from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import FarmDevice, FarmData
from rest_framework import status
import json, datetime


@authentication_classes([])
@permission_classes([])
class LoraDeviceViewSet(APIView):

    def _data_parsing(self, data):

        try:
            print('Lora Data: ', data)
            temperature = data['event_data']['payload'][2]['value']
            rel_humidity = data['event_data']['payload'][3]['value']
            ts = datetime.datetime.fromtimestamp(data['event_data']['timestamp'] / 1000.)
            timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")
            dev_internal_id = data['device']['id']
            device_uid = data['device']['thing_name'][1:3]
            if 16 < int(device_uid) < 25:
                co2 = data['event_data']['payload'][4]['value']
                return [device_uid, json.dumps({'temperature': temperature,
                                            'rel_humidity': rel_humidity,
                                            'co2': co2,
                                            'dev_internal_id': dev_internal_id,
                                            'timestamp': timestamp})]
            else:
                batt_value = data['event_data']['payload'][4]['value']
                return [device_uid, json.dumps({'temperature': temperature,
                                                'rel_humidity': rel_humidity,
                                                'batt_value': batt_value,
                                                'dev_internal_id': dev_internal_id,
                                                'timestamp': timestamp})]

        except Exception as e:
            print('Error in Lora _data_parsing: ', e)
            return None

    def post(self, request):
        lora_data = self._data_parsing(request.data)
        if lora_data is not None:
            try:
                lora_device = FarmDevice.objects.get(device_uid=lora_data[0])
                lora_device_data = FarmData(farm_device=lora_device)
                lora_device_data.device_data = lora_data[1]
                lora_device_data.save()
                print('saving...\n', lora_device)
                return Response({'message': 'dev_id {} and data {}'.format(lora_data[0], lora_data[1])})
            except FarmDevice.DoesNotExist as e:
                print('Error update_battery_status', e)
                return Response({'Error':'Device ID not found'}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({'Error': 'Problem with Lora data format'}, status=status.HTTP_400_BAD_REQUEST)



