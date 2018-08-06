from django import forms
from django.forms import ModelForm
from .models import Generation


class UploadForm(forms.Form):
    file = forms.FileField()


class IndividualsGenerationForm(forms.Form):
    num_individuals = forms.IntegerField(min_value=1, label="Number of Individuals", initial=100)
    num_randomization_segments =\
        forms.IntegerField(min_value=2, label="Randomizer Segments", initial="11",
                           help_text="Number of segments for the discretization of the random process")
