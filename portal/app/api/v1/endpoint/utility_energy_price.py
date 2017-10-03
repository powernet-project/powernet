from app.models import UtilityEnergyPrice
from rest_framework import (viewsets, serializers)


class UtilityEnergyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityEnergyPrice
        fields = '__all__'


class UtilityEnergyPriceViewSet(viewsets.ModelViewSet):
    serializer_class = UtilityEnergyPriceSerializer
    queryset = UtilityEnergyPrice.objects.all()
