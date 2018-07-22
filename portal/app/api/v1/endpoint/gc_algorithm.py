from django_celery_results.models import TaskResult
from app.tasks import run_global_controller
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def run_gc(request):
    t = run_global_controller.delay()
    return Response({'task_id': t.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def gc_results(request):
    task = TaskResult.objects.get(task_id=request.query_params.get('task_id'))
    return Response({'result': task.result}, status=status.HTTP_200_OK)
