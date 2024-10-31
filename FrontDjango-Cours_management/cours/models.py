from django.db import models
from django.utils import timezone

class Cours(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='courses/')
    date_posted = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return self.title
