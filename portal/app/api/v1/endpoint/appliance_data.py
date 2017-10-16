from app.models import ApplianceJsonData
from rest_framework import (viewsets, serializers)


class ApplianceJsonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplianceJsonData
        fields = '__all__'


class ApplianceJsonDataViewSet(viewsets.ModelViewSet):
    serializer_class = ApplianceJsonDataSerializer
    queryset = ApplianceJsonData.objects.all()
