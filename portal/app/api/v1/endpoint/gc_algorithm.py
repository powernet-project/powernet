from django_celery_results.models import TaskResult
from app.tasks import run_global_controller, wtf
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def run_gc(request):
    t = run_global_controller.delay()
    return Response({'task_id': t.id}, status=status.HTTP_200_OK)


@api_view(['GET'])
def gc_results(request):
    t_id = request.query_params.get('task_id', -999)
    if t_id == -999:
        return Response({'result': 'Please supply a task id to lookup'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        task = TaskResult.objects.get(task_id=t_id)
    except TaskResult.DoesNotExist:
        return Response({'result': 'The given id doesn\'t exist. The task may have not finished or the id is invalid.'},
                        status=status.HTTP_200_OK)
    return Response({'result': task.result}, status=status.HTTP_200_OK)


@api_view(['GET'])
def test_celery(request):
    t = wtf.delay()
    return Response({'task_id': t.id}, status=status.HTTP_200_OK)
