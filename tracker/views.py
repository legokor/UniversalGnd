import json

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Task
from .consumers import broadcast


def index(request):
    return render(request, 'tracker/index.html')


@login_required(login_url='/admin/login/')
def admin(request):
    return render(request, 'tracker/admin.html', {})


def checklist(request):
    data = [obj.serialized_fields() for obj in Task.objects.all()]
    return JsonResponse(data, safe=False)


@csrf_exempt
def update_task(request, pk):
    task = Task.objects.get(pk=pk)
    data = json.loads(request.body)
    if data['finished'] and task.actual_timestamp is None:
        task.actual_timestamp = timezone.now()
    elif not data['finished'] and task.actual_timestamp is not None:
        task.actual_timestamp = None
    if task.has_value:
        task.value = data.get('value')
    task.save()
    broadcast(task.serialized_fields())
    return HttpResponse(request)
