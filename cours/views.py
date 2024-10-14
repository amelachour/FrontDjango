from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CourseForm
from cours.models import Cours 
import logging
from django.shortcuts import get_object_or_404 ,render

logger = logging.getLogger(__name__)

def course_list(request):
    logger.info("Début du traitement de la requête course_list")
    try:
        courses = Cours.objects.all()
        
        logger.info(f"Nombre de cours récupérés : {courses.count()}")
        return render(request, "courses.html", {'courses': courses})  # Ajouter les cours au contexte
    except Exception as e:
        logger.error(f"Erreur capturée dans course_list: {str(e)}")
        return HttpResponse(f"Une erreur est survenue : {str(e)}")



def course_detail(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    return render(request, 'course-single.html', {'course': course})

