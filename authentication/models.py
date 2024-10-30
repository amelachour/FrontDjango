from django.db import models
from django.contrib.auth.models import User
import json
from .validators import validate_image_format
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    face_image = models.ImageField(upload_to='face_images/', validators=[validate_image_format])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    teaching_subject = models.CharField(max_length=100, null=True, blank=True, default="unknown")
    about_me = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    face_encoding = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def save(self, *args, **kwargs):
        
        if isinstance(self.face_encoding, list):
            self.face_encoding = json.dumps(self.face_encoding)
        super().save(*args, **kwargs)

    def set_face_encoding(self, encoding):
        if isinstance(encoding, list):
            self.face_encoding = json.dumps(encoding)
        else:
            raise ValueError("Encoding must be a list.")

    def get_face_encoding(self):
        try:
            return json.loads(self.face_encoding) if self.face_encoding else None
        except json.JSONDecodeError:
            return None  

    def __str__(self):
        return self.user.username
