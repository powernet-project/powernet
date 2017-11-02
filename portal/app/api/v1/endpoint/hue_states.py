from app.models import HueStates
from rest_framework import (viewsets, serializers)
from app.common.enum_field_handler import EnumFieldSerializerMixin


class HueStatesSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = HueStates
        fields = '__all__'


class HueStatesViewSet(viewsets.ModelViewSet):
    serializer_class = HueStatesSerializer
    queryset = HueStates.objects.all()
