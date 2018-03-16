from rest_framework import (viewsets, serializers)

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
    serializer_class = HomeSerializer
    queryset = Home.objects.all().order_by('id')


class HomeDataViewSet(viewsets.ModelViewSet):
    serializer_class = HomeDataSerializer
    queryset = HomeData.objects.all()
