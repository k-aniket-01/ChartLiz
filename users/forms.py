from django import forms
from .models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = ['first_name', 'last_name', 'email', 'avatar', 'timezone', 'experience_level']
        widgets = {
            'first_name' : forms.TextInput(attrs={'class':'form-control'}),
            'last_name' : forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.TextInput(attrs={'class':'form-control'}),
            'avatar': forms.FileInput(attrs={'class':'form-control'}),
            'timezone':forms.TextInput(attrs={'class':'form-control'}),
            'experience_level': forms.Select(attrs={'class':'form-select'})
        }
