from django.urls import path, re_path
from home import views

urlpatterns = [

    # The home page
    path('', views.home, name='home'),

    # Matches any html file

]