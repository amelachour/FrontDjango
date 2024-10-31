from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import JsonResponse
import json
from .nlp import nlp_processor  # Importer l'instance du processeur NLP
from .utils import fetch_content_by_theme  # Importer la fonction utilitaire
from .models import Flashcard  # Si vous souhaitez sauvegarder les flashcards dans la base de données
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy



def index(request):
    return render(request, 'flashcards/flashcard_auto.html')

# Vues CRUD

class FlashcardListView( ListView):
    model = Flashcard
    template_name = 'flashcards/flashcard_list.html'
    context_object_name = 'flashcards'
    ordering = ['-created_at']
    login_url = 'index'  # Assurez-vous d'avoir une URL de connexion

class FlashcardDetailView( DetailView):
    model = Flashcard
    template_name = 'flashcards/flashcard_detail.html'
    context_object_name = 'flashcard'
    login_url = 'index'

class FlashcardCreateView( CreateView):
    model = Flashcard
    fields = ['question', 'answer']
    template_name = 'flashcards/flashcard_form.html'
    success_url = reverse_lazy('flashcards:flashcard-list')
    login_url = 'index'

class FlashcardUpdateView(UpdateView):
    model = Flashcard
    fields = ['question', 'answer']
    template_name = 'flashcards/flashcard_form.html'
    success_url = reverse_lazy('flashcards:flashcard-list')
    #login_url = 'login'

class FlashcardDeleteView( DeleteView):
    model = Flashcard
    template_name = 'flashcards/flashcard_confirm_delete.html'
    success_url = reverse_lazy('flashcards:flashcard-list')
    #login_url = 'login'
    
def display_flashcards_view(request):
    if request.method == 'GET':
        # Récupérer toutes les flashcards de la base de données
        flashcards = Flashcard.objects.all().order_by('-created_at')[:10]  # Limiter à 10 flashcards
        flashcards_data = [{'question': fc.question, 'answer': fc.answer} for fc in flashcards]

        return render(request, 'flashcards/display_flashcards.html', {'flashcards': flashcards_data})
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée.'}, status=405)



def generate_flashcards_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            input_method = 'text'  # Par défaut
            text = data.get('text', '').strip()
            num_flashcards = data.get('num_flashcards_limit')
            theme = data.get('theme', '').strip()

            # Déterminer l'option choisie
            if theme and text:
                # Si les deux sont fournis, prioriser l'option choisie
                # Vous pouvez ajuster cette logique selon vos préférences
                # Ici, si le thème est spécifié, utiliser le thème
                input_method = 'theme'
            elif theme:
                input_method = 'theme'
            elif text:
                input_method = 'text'
            else:
                # Aucun des deux n'est fourni
                return JsonResponse({'error': "Le champ 'text' ou 'theme' est requis pour générer des flashcards."}, status=400)

            if input_method == 'theme':
                theme_content = fetch_content_by_theme(theme)
                if theme_content:
                    text = theme_content
                else:
                    return JsonResponse({'error': f"Aucun contenu trouvé pour le thème '{theme}'."}, status=400)
            elif input_method == 'text':
                if not text:
                    return JsonResponse({'error': "Le champ 'text' est requis pour générer des flashcards."}, status=400)

            if not num_flashcards:
                return JsonResponse({'error': "Le champ 'num_flashcards_limit' est requis."}, status=400)

            # Générer les flashcards en utilisant le processeur NLP
            flashcards = nlp_processor.generate_flashcards(text, num_flashcards)

            # Optionnel : Sauvegarder les flashcards dans la base de données
            for fc in flashcards:
                Flashcard.objects.create(question=fc['question'], answer=fc['answer'])

            return JsonResponse({'flashcards': flashcards}, status=200)
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée.'}, status=405)
def list_flashcards_view(request):
    if request.method == 'GET':
        flashcards = Flashcard.objects.all().order_by('-created_at')[:100]  # Limite à 100 flashcards récentes
        flashcards_data = [{'question': fc.question, 'answer': fc.answer} for fc in flashcards]
        return JsonResponse({'flashcards': flashcards_data}, status=200)
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée.'}, status=405)