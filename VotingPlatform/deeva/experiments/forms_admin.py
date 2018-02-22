from django import forms
from django.forms import ModelForm
from .models import Generation


class UploadForm(forms.Form):
    file = forms.FileField()