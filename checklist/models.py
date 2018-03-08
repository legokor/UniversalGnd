from django.db import models
import time

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
    actual_timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def serialized_fields(self):
        data = {
            'id': self.id,
            'title': self.title,
            'projected_timestamp': time.mktime(self.projected_timestamp.timetuple()),
            'actual_timestamp': time.mktime(self.actual_timestamp.timetuple()) if self.actual_timestamp is not None else None,
        }
        return data
