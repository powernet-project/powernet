from rest_framework import (viewsets, serializers, filters, status)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import FarmDevice, FarmData
from rest_framework.decorators import action
from rest_framework.response import Response


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
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    search_fields = ['farm_device__device_uid']
    filter_backends = (filters.SearchFilter,)

    queryset = FarmData.objects.all().order_by('-id')
    serializer_class = FarmDataSerializer



