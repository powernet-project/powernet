from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import FarmDevice, FarmData
from rest_framework.exceptions import APIException


class FarmDeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = FarmDevice
        fields = '__all__'


class FarmDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmData
        fields = '__all__'


class FarmDeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = FarmDeviceSerializer

    def get_queryset(self, **kwargs):
        queryset = FarmDevice.objects.filter(home__owner__user=self.request.user).order_by('id')
        return queryset


class FarmDataViewSet(viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = FarmDataSerializer
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)

    def get_queryset(self, **kwargs):
        device_uid = self.request.query_params.get('device_uid', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if device_uid is None or start_date is None or end_date is None:
            raise InvalidParamException
            return
        queryset = FarmData.objects.filter(farm_device__device_uid=device_uid, timestamp__range=[start_date, end_date])
        return queryset


class InvalidParamException(APIException):
    status_code = 400
    default_detail = 'Could not determine an appropriate data set to retrieve, please ensure ' \
                     'the supplied parameters are correct.'
    default_code = 'invalid_parameters'
