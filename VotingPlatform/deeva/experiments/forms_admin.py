from django import forms
from django.forms import ModelForm
from .models import Generation


class UploadForm(forms.Form):
    file = forms.FileField()


class IndividualsGenerationForm(forms.Form):
    num_individuals = forms.TextInput()
    num_randomization_segments = forms.TextInput()
