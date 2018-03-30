from django.db import models
from django.utils.dateformat import format


class Launch(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "launches"

    def __str__(self):
        return self.name


class Task(models.Model):
    launch = models.ForeignKey(Launch, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    projected_timestamp = models.DateTimeField()
    actual_timestamp = models.DateTimeField(null=True, blank=True, editable=False)

    def __str__(self):
        return self.title

    def serialized_fields(self):
        return {
            'id': self.id,
            'title': self.title,
            'projected_timestamp': format(self.projected_timestamp, 'U'),
            'actual_timestamp': format(self.actual_timestamp, 'U') if self.actual_timestamp is not None else None,
        }
