from django.contrib import admin

from .models import Launch, Task, TaskGroup

admin.site.register(Launch)
admin.site.register(TaskGroup)
admin.site.register(Task)
