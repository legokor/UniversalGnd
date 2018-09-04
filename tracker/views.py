import json

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Task
from .consumers import broadcast


def index(request):
    context = {
        'pagetitle': 'UPRA',
        'maintabs': [
            {'id': 'init', 'title': 'Init', 'template': 'tracker/tabs/init.html'},
            {'id': 'tasks', 'title': 'Tasks', 'template': 'tracker/tabs/tasks.html'},
            {'id': 'mam-controls', 'title': 'MaM controls', 'template': 'tracker/tabs/mam-controls.html'},
            {'id': 'qc-controls', 'title': 'QC controls', 'template': 'tracker/tabs/qc-controls.html'},
            {'id': 'program-console', 'title': 'Program Console', 'template': 'tracker/tabs/program-console.html'},
            {'id': 'debug-console', 'title': 'Debug Console', 'template': 'tracker/tabs/debug-console.html'}
        ]
    }
    return render(request, 'tracker/index.html', context)


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
    broadcast({'type': 'update', 'data': task.serialized_fields()})
    return HttpResponse(request)
