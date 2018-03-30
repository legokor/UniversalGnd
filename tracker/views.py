from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from .models import Task
from .consumers import broadcast


def index(request):
    return render(request, 'tracker/base.html')


@login_required(login_url='/admin/login/')
def admin(request):
    return render(request, 'tracker/admin.html', {})


def checklist(request):
    data = [obj.serialized_fields() for obj in Task.objects.all()]
    return JsonResponse(data, safe=False)


def toggle(request, id):
    task = Task.objects.get(pk=id)
    if task.actual_timestamp is not None:
        task.actual_timestamp = None
    else:
        task.actual_timestamp = timezone.now()
    task.save()
    broadcast({'id': task.id, 'actual_timestamp': task.actual_timestamp})
    return HttpResponse(request, "")
