from app.models import ApplianceJsonData
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework import (viewsets, serializers, status)


class ApplianceJsonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplianceJsonData
        fields = '__all__'


class ApplianceJsonDataViewSet(viewsets.ModelViewSet):
    serializer_class = ApplianceJsonDataSerializer
    queryset = ApplianceJsonData.objects.all().order_by('-id')

    # build a list route that takes an id and returns a serialized consumption for the device
    @list_route(methods=['GET'])
    def consumption(self, request):
        id = request.query_params.get('id')
        rms_value = ApplianceJsonData.objects.filter(devices_json__contains=[{'sensor_id': int(id)}]).order_by('-id')

        if rms_value.count() == 0:
            return Response({'result': 'no data for the supplied id'}, status=status.HTTP_404_NOT_FOUND)

        for item in rms_value[0].devices_json:
            if item['sensor_id'] == int(id):
                result = item['samples'][0]['RMS']
                break

        return Response({'result': result, 'id': id}, status=status.HTTP_200_OK)
