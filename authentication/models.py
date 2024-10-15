from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_image = models.ImageField(upload_to='face_images/')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')  # Set default to "student"

    def __str__(self):
        return self.user.username
