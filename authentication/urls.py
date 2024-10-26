

from django.urls import path
from .views import login_view, face_recognition_login,register_user, edit_profile_view, user_list, profile_view, edit_user, delete_user
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', login_view, name="login"),
     path('face-recognition-login/', face_recognition_login, name='face_recognition_login'),
    path('register/', register_user, name="register"),
   path('logout/', LogoutView.as_view(next_page='index'), name="logout"),
   
    path('users/', user_list, name='user_list'),
    path('users/edit/<int:pk>/', edit_user, name='edit_user'),
      path('edit_profile/', edit_profile_view, name='edit_profile'),
    path('users/delete/<int:pk>/', delete_user, name='delete_user'),
    path('profile/', profile_view, name='profile'),  
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
