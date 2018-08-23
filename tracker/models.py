from django.db import models
from django.utils.dateformat import format


class Launch(models.Model):
    name = models.CharField(max_length=100)
    balloon_dry_mass = models.DecimalField(
        "Mass of empty balloon (g)",
        max_digits=16, decimal_places=4, null=True, blank=True)
    parachute_dry_mass = models.DecimalField(
        "Mass of parachute (g)",
        max_digits=16, decimal_places=4, null=True, blank=True)
    payload_dry_mass = models.DecimalField(
        "Mass off payload (g)",
        max_digits=16, decimal_places=4, null=True, blank=True)
    nozzle_lift = models.DecimalField(
        "Nozzle lift (g)",
        max_digits=16, decimal_places=4, null=True, blank=True)
    parachute_area = models.DecimalField(
        "Area of parachute (m^2)",
        max_digits=16, decimal_places=4, null=True, blank=True)
    parachute_drag_c = models.DecimalField(
        "Drag coefficient of parachute",
        max_digits=16, decimal_places=4, null=True, blank=True)
    balloon_drag_c = models.DecimalField(
        "Drag coefficient of balloon",
        max_digits=16, decimal_places=4, null=True, blank=True)
    design_burst_diam = models.DecimalField(
        "Design burst diameter of balloon (m)",
        max_digits=16, decimal_places=4, null=True, blank=True)

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

    def get_balloon_properties(self):
        return {
            'balloon_dry_mass': self.balloon_dry_mass,
            'parachute_dry_mass': self.parachute_dry_mass,
            'payload_dry_mass': self.payload_dry_mass,
            'nozzle_lift': self.nozzle_lift,
            'parachute_area': self.parachute_area,
            'parachute_drag_c': self.parachute_drag_c,
            'balloon_drag_c': self.balloon_drag_c,
            'design_burst_diam': self.design_burst_diam
        }


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
            'launch': self.launch.id,
        }
