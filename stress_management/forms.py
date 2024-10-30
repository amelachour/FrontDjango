from django import forms
from .models import StressAssessment

class StressAssessmentForm(forms.ModelForm):
    class Meta:
        model = StressAssessment
        fields = ['question_1', 'question_2', 'question_3']
