from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import Device, DeviceState
from django.dispatch import receiver
from django.db.models.signals import post_save
from google.cloud import pubsub_v1
from rest_framework.renderers import JSONRenderer


class DeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = '__all__'


class DeviceStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceState
        fields = '__all__'


class DeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = DeviceSerializer

    def get_queryset(self, **kwargs):
        queryset = Device.objects.filter(home__owner__user=self.request.user).order_by('id')
        return queryset


class DeviceStateViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = DeviceStateSerializer

    def get_queryset(self, **kwargs):
        queryset = DeviceState.objects.filter(device__home__owner__user=self.request.user).order_by('id')
        return queryset


@receiver(post_save, sender=Device)
def publish_device_change(sender, **kwargs):
    # get the object generating the signal and serialize it for transport
    obj = kwargs.get('instance')
    obj_ser = JSONRenderer().render(DeviceSerializer(obj).data)

    # init the publisher with our project params - will need HH ref in the future so we can discriminate
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path('pwrnet-158117', 'home-hub-message')

    # publish the message
    publisher.publish(topic_path, data=obj_ser.encode('utf-8'))
    print('Message published...')


