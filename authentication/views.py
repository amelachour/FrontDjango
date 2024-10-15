from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .forms import UserProfile  # Assurez-vous d'avoir un formulaire pour cela

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages

from django.shortcuts import render
from django.contrib.auth.models import User
from authentication.models import UserProfile

from django.shortcuts import render
from django.contrib.auth.models import User
from authentication.models import UserProfile
from django.db.models import Q

from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import UserProfile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from .models import UserProfile
import face_recognition
from django.core.files.storage import default_storage
import json
import base64
import os
import io
from django.http import JsonResponse
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from .models import User


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from .models import UserProfile
import face_recognition
import numpy as np
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import UserProfile
from .forms import UserProfileForm



def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')  # Redirect to the dashboard if credentials are correct
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def profile_view(request):
    return render(request, 'accounts/profile.html')


@csrf_exempt
def facial_recognition_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        descriptor = np.array(data.get("descriptor"))

        # Compare with known faces
        known_faces = load_known_faces()

        for username, known_descriptor in known_faces.items():
            results = face_recognition.compare_faces([known_descriptor], descriptor)

            if results[0]:  # Face recognized
                user = authenticate(username=username)  # Authenticate user based on username
                if user:
                    login(request, user)  # Log in the user
                    return JsonResponse({"success": True, "username": username})

        return JsonResponse({"success": False, "message": "Face not recognized"})
    return JsonResponse({"error": "Invalid request"}, status=400)

def load_known_faces():
    known_faces = {}
    users = UserProfile.objects.all()

    for user_profile in users:
        face_image_path = user_profile.face_image.path
        known_image = face_recognition.load_image_file(face_image_path)
        known_face_encoding = face_recognition.face_encodings(known_image)[0]
        known_faces[user_profile.user.username] = known_face_encoding

    return known_faces




def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)
        print("Form Data:", request.POST)  # Debug: Print form data
        if form.is_valid():
            user = form.save()
            # Save face image and role in user profile
            UserProfile.objects.create(user=user, face_image=form.cleaned_data.get('face_image'), role='student')  # Set role to "student"
            # Redirect the user to the login page after registration
            return redirect('accounts//login')
        else:
            print("Form Errors:", form.errors)  # Debug: Print form errors
            msg = 'The form is invalid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


# def register_user(request):
#     msg = None
#     success = False

#     if request.method == "POST":
#         form = SignUpForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save()
#             # Save face image and role in user profile
#             UserProfile.objects.create(user=user, face_image=form.cleaned_data.get('face_image'), role='student')  # Set role to "student"
#             msg = 'User created - please <a href="/login">log in</a>.'
#             success = True
#         else:
#             msg = 'The form is invalid'
#     else:
#         form = SignUpForm()

#     return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})
def user_list(request):
    # Get all users and their corresponding profiles
    users = User.objects.all()
    user_profiles = UserProfile.objects.select_related('user')  # Use select_related for optimization

    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))

    # Apply role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(userprofile__role=role_filter)

    # Implement pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'authentication/user_list.html', {'users': users})



def edit_user(request, pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)  # Récupère l'utilisateur par son identifiant
    user_profile = get_object_or_404(UserProfile, user=user)  # Récupérer le UserProfile lié à cet utilisateur

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  # Utilisez request.FILES pour gérer les fichiers
        if form.is_valid():
            # Mettre à jour le nom d'utilisateur et l'email
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()  # Sauvegarder les modifications de l'utilisateur

            form.save()  # Sauvegarder les modifications du UserProfile
            return redirect('user_list')  # Redirige vers la liste des utilisateurs
    else:
        form = UserProfileForm(instance=user_profile)  # Pré-remplit le formulaire avec les données de UserProfile

    return render(request, 'authentication/edit_user.html', {'form': form, 'user': user})


def delete_user(request, pk):
    User = get_user_model()  # Récupère le modèle utilisateur personnalisé
    user = get_object_or_404(User, pk=pk)  # Récupère l'utilisateur par son identifiant

    if request.method == 'POST':
        user.delete()  # Supprime l'utilisateur
        messages.success(request, f'User {user.username} has been deleted successfully.')
        return redirect('user_list')  # Redirige vers la liste des utilisateurs

    return render(request, 'authentication/delete_user.html', {'user': user})

def register_view(request):
    return render(request, 'authentication/register.html')

def password_reset_view(request):
    return render(request, 'authentication/password_reset.html')


def profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile.html', {'profile': profile})