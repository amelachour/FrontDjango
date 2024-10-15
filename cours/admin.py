

# myapp/admin.py
from django.contrib import admin
from .models import Cours  # Import the Cours model

admin.site.register(Cours)  # Register the Cours model
