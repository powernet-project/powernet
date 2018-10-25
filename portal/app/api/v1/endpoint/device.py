from rest_framework import (viewsets, serializers)
from rest_framework.authentication import BasicAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import Device, DeviceState
from django.dispatch import receiver
from django.db.models.signals import post_save


class DeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class DeviceStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceState
        fields = '__all__'


class DeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = DeviceSerializer
    queryset = Device.objects.all().order_by('id')


class DeviceStateViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = DeviceStateSerializer
    queryset = DeviceState.objects.all()


@receiver(post_save, sender=Device)
def publish_device_change(sender, **kwargs):
    obj = kwargs.get('instance')
    print(kwargs.get('created', False))
    print("Sometimes I wonder what goes on")
    obj_ser = DeviceSerializer(obj)
    print(obj_ser)
