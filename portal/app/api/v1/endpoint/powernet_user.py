from app.models import PowernetUser
from app.api.v1 import CsrfExemptAuth
from rest_framework.decorators import action
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import (viewsets, serializers, status)
from rest_framework.authentication import BasicAuthentication
from app.common.enum_field_handler import EnumFieldSerializerMixin


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

    @action(detail=False, methods=['POST'])
    def auth(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        invalid_response = {
            'data': {'detail': 'Invalid user credentials.'},
            'status': status.HTTP_401_UNAUTHORIZED
        }

        if email and password:
            email = email.strip()
            try:
                powernet_user = PowernetUser.objects.get(email__iexact=email)
                if not powernet_user.user:
                    return Response(**invalid_response)

            except ObjectDoesNotExist:
                return Response(**invalid_response)

            user = authenticate(username=powernet_user.user.username, password=password)

            if user is None:
                return Response(**invalid_response)

            if not user.is_active:
                return Response({'detail': 'User account is disabled.'}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return Response(**invalid_response)

        # check if this user already has an existing token
        if Token.objects.filter(user=user).count() > 0:
            token = Token.objects.get(user=user)
        else:
            token = Token.objects.create(user=user)

        return Response({'token': token.key}, headers={'X-Authentication-Token': token})
