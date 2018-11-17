from app.models import UtilityEnergyPrice
from rest_framework import (viewsets, serializers)
from rest_framework.authentication import TokenAuthentication
from app.api.v1 import CsrfExemptAuth


class UtilityEnergyPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UtilityEnergyPrice
        fields = '__all__'


class UtilityEnergyPriceViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptAuth.CsrfExemptSessionAuthentication, TokenAuthentication)
    serializer_class = UtilityEnergyPriceSerializer
    queryset = UtilityEnergyPrice.objects.all()
