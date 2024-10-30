# models.py
from django.db import models
from django.contrib.auth.models import User


class StressAssessment(models.Model):
    Q1 = models.IntegerField()
    Q2 = models.IntegerField()
    Q3 = models.IntegerField()
    Q4 = models.IntegerField(default=0)  
    Q5 = models.IntegerField(default=0)  

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Évaluation de stress: Q1={self.Q1}, Q2={self.Q2}, Q3={self.Q3}, Q4={self.Q4}, Q5={self.Q5}"
