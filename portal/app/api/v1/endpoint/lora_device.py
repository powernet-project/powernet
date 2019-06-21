from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from app.api.v1 import CsrfExemptAuth
from rest_framework.decorators import action
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import FarmDevice
from rest_framework import (viewsets, serializers, status)


class LoraDeviceSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = FarmDevice
        fields = '__all__'


class LoraDeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = LoraDeviceSerializer
    queryset = FarmDevice.objects.all()

    @action(detail=True, methods=['PUT'])
    def loradata(self, request):
        data = request.data
        print('data: ', data)



