from django import forms
from .models import Cours

class CourseForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['title', 'description', 'file']
    
   
from django import forms

class QuizForm(forms.Form):
    answers = forms.JSONField()  
