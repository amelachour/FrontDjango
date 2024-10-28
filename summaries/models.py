from django.db import models

class Summary(models.Model):
    title = models.CharField(max_length=200)
    document = models.FileField(upload_to='documents/')
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title