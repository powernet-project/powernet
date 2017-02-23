import calendar

from django.shortcuts import render
from django.http import HttpResponse
from django_ajax.decorators import ajax

from .models import ResInterval60

def index(request):
    service_point_list = ResInterval60.objects.values('sp_id').distinct()
    context = {
        'sp_list' : service_point_list
    }
    return render(request, 'viz/index.html', context)

@ajax
def show(request, sp_id):
    res_intervals = ResInterval60.objects.filter(sp_id=sp_id).order_by('date')

    return {
        'start_date': calendar.timegm(res_intervals[0].date.timetuple()),
        'end_date': calendar.timegm(res_intervals[len(res_intervals) - 1].date.timetuple())
        'chart': {
            'data': {
                'lr': [],
                'ffnn': []
            }
        }
    }

