from app.models import HueStates
from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin


class HueStatesSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = HueStates
        fields = '__all__'


class HueStatesViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = HueStatesSerializer
    queryset = HueStates.objects.all()
