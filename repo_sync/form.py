from django import forms
from .models import Repository

class RepositoryForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['name', 'url']
        labels = {
            'name': 'Repository Name',
            'url': 'Repository URL',
        }
        help_texts = {
            'name': 'Enter a unique name for this repository.',
            'url': 'Enter the Git URL of the repository.',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }
