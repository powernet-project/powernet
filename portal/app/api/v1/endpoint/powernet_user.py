from rest_framework import (viewsets, serializers)

from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import PowernetUser


class PowernetUserSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PowernetUser
        fields = '__all__'


class PowernetUserViewSet(viewsets.ModelViewSet):
    serializer_class = PowernetUserSerializer
    queryset = PowernetUser.objects.all().order_by('id')

