from rest_framework import (viewsets, serializers)

from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import Device, DeviceState


class DeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class DeviceStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceState
        fields = '__all__'


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()


class DeviceStateViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceStateSerializer
    queryset = DeviceState.objects.all()
