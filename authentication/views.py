from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .forms import UserProfile 

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

import face_recognition
import numpy as np
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model

from .forms import UserProfileForm
from django.shortcuts import render, redirect
from .forms import SignUpForm

from PIL import Image
import numpy as np
import face_recognition
from io import BytesIO
from django.db import transaction
from django.core.exceptions import ValidationError 
from django.urls import reverse

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
                return redirect('index')  
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})



def load_encodings():
    user_encodings = {}
    for user in users_list:
        encoding = get_stored_encoding(user)
        if encoding is None or len(encoding) == 0:
            print(f"No encoding data found for user {user}")
            continue
        if encoding.shape != (128,):
            print(f"Skipping user {user} due to invalid encoding shape: {encoding.shape}")
            continue
        user_encodings[user] = encoding
    return user_encodings




def get_stored_encoding(profile):
    encoding_data = profile.face_encoding
    if not encoding_data:
        print(f"No encoding data found for user {profile.user.username}")
        return np.array([])

    try:
        return np.array(json.loads(encoding_data))
    except (ValueError, TypeError) as e:
        print(f"Error loading face encoding for user {profile.user.username}: {str(e)}")
        return np.array([])  



@csrf_exempt
def face_recognition_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            image_data = data['image']

           
            header, encoded = image_data.split(',', 1)
            decoded_image = base64.b64decode(encoded)
            image = Image.open(BytesIO(decoded_image)).convert('RGB')
            image_np = np.array(image)

          
            face_encodings = face_recognition.face_encodings(image_np)

            if len(face_encodings) == 0:
                return JsonResponse({'success': False, 'message': 'Aucun visage détecté'})

            if len(face_encodings) > 1:
                return JsonResponse({'success': False, 'message': 'Plusieurs visages détectés. Un seul visage autorisé.'})

            uploaded_encoding = face_encodings[0]

            
            user_profiles = UserProfile.objects.all()
            for profile in user_profiles:
                stored_encoding = get_stored_encoding(profile)

                
                if stored_encoding.shape != (128,):
                    print(f"Utilisateur ignoré {profile.user.username} à cause d'un encodage invalide.")
                    continue  

                
                results = face_recognition.compare_faces([stored_encoding], uploaded_encoding, tolerance=0.5)

                if results[0]:  
                    user = profile.user
                    login(request, user)
                    return JsonResponse({'success': True, 'message': 'Authentification réussie'})

            return JsonResponse({'success': False, 'message': 'Aucun utilisateur correspondant trouvé'})

        except Exception as e:
            print("Erreur :", str(e))
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False}, status=400)



def profile_view(request):
    return render(request, 'profile.html')


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST, request.FILES)

        if form.is_valid():
            try:
               
                face_image = form.cleaned_data.get('face_image')
                validate_image_format(face_image)  

                with transaction.atomic():  
                    
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data.get('password1')) 
                    user.save()
                    print("User created successfully.")  

                    
                    image = Image.open(face_image)
                    image_np = np.array(image)
                    face_encodings = face_recognition.face_encodings(image_np)

                    if face_encodings:
                        face_encoding = face_encodings[0].tolist()  

                      
                        user_profile = UserProfile(
                            user=user,
                            face_image=face_image,
                            role='student', 
                            teaching_subject=form.cleaned_data.get('teaching_subject', ''),
                            about_me=form.cleaned_data.get('about_me', ''),
                            address=form.cleaned_data.get('address', ''),
                            phone=form.cleaned_data.get('phone', ''),
                            face_encoding=json.dumps(face_encoding)  
                        )
                        user_profile.save()
                        print("UserProfile created successfully.")  

                      
                        return redirect(reverse('login')) 

                    else:
                        msg = "No face detected in the uploaded image. Please upload a clear face image."
                        print("No face detected in the image.")  

            except ValidationError as ve:
                msg = str(ve) 
                print(f"Validation error occurred: {msg}")  
            except Exception as e:
                msg = f"Error processing the image or saving the user profile: {str(e)}"
                print(f"Exception occurred: {e}") 

        else:
            msg = 'The form is invalid. Please correct the errors below.'
            print(f"Form errors: {form.errors}") 

    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})









def user_list(request):
    
    users = User.objects.all()
    user_profiles = UserProfile.objects.select_related('user')  

 
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(Q(username__icontains=search_query) | Q(email__icontains=search_query))

  
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(userprofile__role=role_filter)

   
    from django.core.paginator import Paginator
    paginator = Paginator(users, 10) 
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    return render(request, 'authentication/user_list.html', {'users': users})



def edit_user(request, pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)  
    user_profile = get_object_or_404(UserProfile, user=user) 

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  
        if form.is_valid():
           
            user.username = request.POST.get('username')
            user.email = request.POST.get('email')
            user.save()  

            form.save()  
            return redirect('user_list')  
    else:
        form = UserProfileForm(instance=user_profile)  

    return render(request, 'authentication/edit_user.html', {'form': form, 'user': user})


def delete_user(request, pk):
    User = get_user_model()  
    user = get_object_or_404(User, pk=pk)  

    if request.method == 'POST':
        user.delete()  
        messages.success(request, f'User {user.username} has been deleted successfully.')
        return redirect('user_list')  

    return render(request, 'authentication/delete_user.html', {'user': user})

def register_view(request):
    return render(request, 'authentication/register.html')

def password_reset_view(request):
    return render(request, 'authentication/password_reset.html')


def profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'profile.html', {'profile': profile})


def edit_profile_view(request):
    user = request.user

    
    user_profile = get_object_or_404(UserProfile, user=user)

    if request.method == 'POST':
        
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)  
        
        if profile_form.is_valid():
            
            user.username = request.POST.get('username', user.username)  
            user.email = request.POST.get('email', user.email) 
            user.first_name = request.POST.get('first_name', user.first_name)  
            user.last_name = request.POST.get('last_name', user.last_name)  
            
            user.save()  

            
            if 'face_image' in request.FILES:
                user_profile.face_image = request.FILES['face_image']  

                
                face_image = request.FILES['face_image']
                try:
                    image = Image.open(face_image)
                    image_np = np.array(image)
                    face_encodings = face_recognition.face_encodings(image_np)

                    if len(face_encodings) > 0:
                        face_encoding = face_encodings[0].tolist()  
                        user_profile.face_encoding = face_encoding  

                except Exception as e:
                    messages.error(request, f"Error processing the image for encoding: {str(e)}")

            
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')  
    else:
        
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'authentication/edit_profile.html', {
        'form': profile_form,
        'user': user,
    })

def validate_image_format(image):
  
    allowed_formats = ['JPEG', 'PNG', 'JPG']

   
    try:
        img = Image.open(image)
        img_format = img.format

        
        if img_format not in allowed_formats:
            raise ValidationError(f"Unsupported image format: {img_format}. Please upload a JPEG or PNG image.")
    except Exception as e:
        raise ValidationError(f"Could not open the image: {str(e)}")
