from rest_framework import (viewsets, serializers)
from rest_framework.authentication import BasicAuthentication
from app.api.v1 import CsrfExemptAuth
from app.common.enum_field_handler import EnumFieldSerializerMixin
from app.models import Home, HomeData


class HomeSerializer(EnumFieldSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Home
        fields = '__all__'


class HomeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeData
        fields = '__all__'


class HomeViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = HomeSerializer
    queryset = Home.objects.all().order_by('id')


class HomeDataViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, BasicAuthentication)
    serializer_class = HomeDataSerializer
    queryset = HomeData.objects.all()
