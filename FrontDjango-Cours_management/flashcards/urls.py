# flashcards/urls.py

from django.urls import path
from . import views

app_name = 'flashcards'  # Définir le namespace

urlpatterns = [
    # URLs CRUD
    path('ai/', views.index, name='index'),
    path('flashcards/', views.FlashcardListView.as_view(), name='flashcard-list'),
    path('flashcard/<int:pk>/', views.FlashcardDetailView.as_view(), name='flashcard-detail'),
    path('flashcard/create/', views.FlashcardCreateView.as_view(), name='flashcard-create'),
    path('flashcard/<int:pk>/update/', views.FlashcardUpdateView.as_view(), name='flashcard-update'),
    path('flashcard/<int:pk>/delete/', views.FlashcardDeleteView.as_view(), name='flashcard-delete'),
    path('flashcards/display/', views.display_flashcards_view, name='display-flashcards'),

    # URLs existantes
    path('generate_flashcards/', views.generate_flashcards_view, name='generate_flashcards'),
    path('list_flashcards/', views.list_flashcards_view, name='list_flashcards'),

    # URL de base pour la génération automatique
    #path('', views.index, name='index'),
]
