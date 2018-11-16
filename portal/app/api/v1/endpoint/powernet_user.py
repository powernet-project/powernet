from rest_framework import (viewsets, serializers)
from rest_framework.authentication import BasicAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import PowernetUser


class PowernetUserSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = PowernetUser
        fields = '__all__'


class PowernetUserViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = PowernetUserSerializer

    def get_queryset(self):
        queryset = PowernetUser.objects.filter(user=self.request.user).order_by('id')
        return queryset

