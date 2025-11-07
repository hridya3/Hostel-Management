from django import forms
from .models import *

class Image_form(forms.ModelForm):
    class Meta:
        model=Image_table
        fields=['name','price','description','image']

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['gender', 'dob', 'phone', 'profile_image']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

