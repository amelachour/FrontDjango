from django.urls import path
from .views import stress_evaluation  

urlpatterns = [
    path('stress-evaluation/', stress_evaluation, name='stress_evaluation'),
]
