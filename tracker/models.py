from django.db import models
from django.utils.dateformat import format


class Launch(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "launches"

    def __str__(self):
        return str(self.name)

    def get_organized_tasks(self):
        return [
            dict(
               tasks=[task.serialized_fields() for task in group.task_set.order_by('projected_timestamp').all()],
               name=group.name
            ) for group in self.taskgroup_set.all()
        ] + [{
            'orphaned': True,
            'tasks': [task.serialized_fields() for task in
                      Task.objects.filter(launch=self, group=None).order_by('projected_timestamp')],
        }]


class TaskGroup(models.Model):
    launch = models.ForeignKey(Launch, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{0} ({1})".format(self.name, self.launch)


class Task(models.Model):
    launch = models.ForeignKey(Launch, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    has_value = models.BooleanField(default=False)
    value = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    projected_timestamp = models.DateTimeField()
    actual_timestamp = models.DateTimeField(null=True, blank=True, editable=False)
    group = models.ForeignKey(TaskGroup, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    def serialized_fields(self):
        return {
            'id': self.id,
            'title': self.title,
            'projected_timestamp': format(self.projected_timestamp, 'U'),
            'actual_timestamp': format(self.actual_timestamp, 'U') if self.actual_timestamp is not None else None,
            'has_value': self.has_value,
            'value': str(self.value),
        }
