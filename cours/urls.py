# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


from .views import course_list 

urlpatterns = [
    
  path('listcourses/', course_list, name='listcourses'),
  path('courses/<int:course_id>/', views.course_detail, name='course_detail'),  

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)