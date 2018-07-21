from app.tasks import add, mul
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def run_gc(request):
    t = add.delay(1, 4)
    return Response({'task_id': t.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def gc_results(request):
    t = mul.delay(10, 42)
    return Response({'task_id': t.id}, status=status.HTTP_200_OK)
