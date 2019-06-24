from app.api.v1 import CsrfExemptAuth
from rest_framework.decorators import action
from rest_framework.response import Response
from app.models import ApplianceJsonData, Home, Device
from rest_framework import (viewsets, serializers, status)
from rest_framework.authentication import TokenAuthentication


class ApplianceJsonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplianceJsonData
        fields = '__all__'


class ApplianceJsonDataViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = ApplianceJsonDataSerializer
    queryset = ApplianceJsonData.objects.all().order_by('-id')

    # build a list route that takes an id and returns a serialized consumption for the device
    @action(detail=False, methods=['GET'])
    def consumption(self, request):
        """
        Support getting the rms consumption for one or more devices. Also allow the user
        to provide a number of samples they would like to retrieve.

        Based on our current sampling frequency, ~80 samples = 1 hour, therefore, approximately
        2000 samples = 1 day
        :param request:
        :return:
        """
        # the requesting user may be associated with multiple homes, but for now, we'll only allow
        # aggregation on a per home basis
        ds = None
        home_id = request.query_params.get('home_id', None)
        device_id = request.query_params.get('device_id', None)
        number_of_samples = request.query_params.get('number_of_samples', 40)

        # validate the requesting user owns the home he is requesting data for
        home = Home.objects.filter(pk=home_id, owner__user=request.user)

        if home.count() == 1:
            ds = ApplianceJsonData.objects.filter(home=home)

        # validate that the device belongs to the requesting user
        device = Device.objects.filter(home__owner__user=request.user, pk=device_id)
        device_count = device.count()

        if device_count == 1:
            ds = ApplianceJsonData.objects.filter(devices_json__contains=[{'sensor_id': int(device_id)}])

        if ds is not None:
            if ds.count() == 0:
                return Response({'result': 'no data for the supplied id'}, status=status.HTTP_404_NOT_FOUND)

            # THIS IS A HACK FOR BACKWARDS COMPAT WITH THE LAB VIZ
            if ds.count() == 1 and device_count == 1:
                for item in ds[0].devices_json:
                    if item['sensor_id'] == int(device_id):
                        result = item['samples'][0]['RMS']
                        return Response({'result': result, 'id': device_id}, status=status.HTTP_200_OK)
            else:
                ds = ds.order_by('-id')
                ds = ds[:int(number_of_samples)]
        else:
            return Response({'result': 'Could not determine an appropriate data set to retrieve, please ensure'
                                       ' the supplied parameters are correct.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(ds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
