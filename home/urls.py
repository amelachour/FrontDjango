from django.urls import path, re_path
from .views import home 

urlpatterns = [

    # The home page
   
 path('', home, name='index'),
    # Matches any html file

]