from app.models import ApplianceJsonData
from rest_framework.decorators import list_route
from rest_framework import (viewsets, serializers)


class ApplianceJsonDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplianceJsonData
        fields = '__all__'


class ApplianceJsonDataViewSet(viewsets.ModelViewSet):
    serializer_class = ApplianceJsonDataSerializer
    queryset = ApplianceJsonData.objects.all().order_by('-id')

    # build a list route that takes an id and returns a serialized consumption for the device
    @list_route(methods=['GET'])
    def consumption(self, request):
        pass
