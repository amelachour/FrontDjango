from django import forms
from .models import Summary

class SummaryForm(forms.ModelForm):
    class Meta:
        model = Summary
        fields = ['title', 'document']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
