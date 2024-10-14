from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CourseForm
from cours.models import Cours 
import logging

logger = logging.getLogger(__name__)

def course_list(request):
    logger.info("Début du traitement de la requête course_list")
    try:
        courses = Cours.objects.all()
        
        logger.info(f"Nombre de cours récupérés : {courses.count()}")
        return render(request, "courses.html")
    except Exception as e:
        logger.error(f"Erreur capturée dans course_list: {str(e)}")
        return HttpResponse(f"Une erreur est survenue : {str(e)}")

def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listcourses') 
    else:
        form = CourseForm()
    return render(request, "courses/add_course.html", {"form": form})


from django.shortcuts import get_object_or_404

def update_course(request, pk):
    course = get_object_or_404(Cours, pk=pk)  
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)  
        if form.is_valid():
            form.save()
            return redirect('listcourses') 
    else:
        form = CourseForm(instance=course)  
    return render(request, "courses/update_course.html", {"form": form, "course": course})




def delete_course(request, pk):
    course = get_object_or_404(Cours, pk=pk) 
    if request.method == 'POST':
        course.delete()  
        return redirect('listcourses') 
    return render(request, "courses/delete_course.html", {"course": course})
