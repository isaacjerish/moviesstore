from django import forms
from .models import Petition


class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ['title', 'description', 'movie_title', 'movie_year', 'movie_director', 'movie_genre']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Add The Dark Knight to our catalog'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why this movie should be added to our catalog...'
            }),
            'movie_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Movie title'
            }),
            'movie_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Release year (optional)',
                'min': '1900',
                'max': '2030'
            }),
            'movie_director': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Director name (optional)'
            }),
            'movie_genre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Genre (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make movie_year, movie_director, and movie_genre optional
        self.fields['movie_year'].required = False
        self.fields['movie_director'].required = False
        self.fields['movie_genre'].required = False
