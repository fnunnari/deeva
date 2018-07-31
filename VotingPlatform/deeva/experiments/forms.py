from django import forms
from django.forms import ModelForm
from .models import Individual


class TestForm(forms.Form):
    CHOICES = (('1', 'First',), ('2', "I don't know",), ('3', 'Second',))
    #from .buttonradioselect import ButtonRadioSelect
    
    test_field = forms.ChoiceField(choices = CHOICES, widget = forms.RadioSelect, label = "text")
    choice_field1 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
            
    choice_field2 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    choice_field3 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)


class CompareForm(forms.Form):
    CHOICES = (('1', 'First',), ('2', "I don't know",), ('3', 'Second',))
    #from .buttonradioselect import ButtonRadioSelect
    
    test_field = forms.ChoiceField(choices = CHOICES, widget = forms.RadioSelect, label = "text")
    choice_field1 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
            
    choice_field2 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
    choice_field3 = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)
