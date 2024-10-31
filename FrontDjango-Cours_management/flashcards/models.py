from django.db import models

# Create your models here.
class Flashcard(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  # Optionnel: pour enregistrer la date de création

    def __str__(self):
        return self.question[:50]  # Affiche les 50 premiers caractères de la question
