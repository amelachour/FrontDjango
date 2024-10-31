from django.contrib import admin

# Register your models here.
from .models import Flashcard

@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'created_at')  # Affiche ces champs dans la liste
    search_fields = ('question', 'answer')  # Ajoute une barre de recherche
    list_filter = ('created_at',)  # Ajoute des filtres par date
