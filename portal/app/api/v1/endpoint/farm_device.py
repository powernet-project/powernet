from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import FarmDevice, FarmData


class FarmDeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = FarmDevice
        fields = '__all__'


class FarmDeviceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmDevice
        fields = '__all__'


class FarmDeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = FarmDeviceSerializer

    def get_queryset(self, **kwargs):
        queryset = FarmDevice.objects.filter(home__owner__user=self.request.user).order_by('id')
        return queryset


class FarmDeviceDataViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = FarmDeviceDataSerializer

    def get_queryset(self, **kwargs):
        queryset = FarmData.objects.filter(home__owner__user=self.request.user).order_by('id')
        return queryset


