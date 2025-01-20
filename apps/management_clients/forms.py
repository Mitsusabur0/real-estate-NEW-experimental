# apps/management_clients/forms.py

from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'is_active']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required field indicators and custom styling
        self.fields['name'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Nombre completo del propietario'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'correo@ejemplo.com'
        })
        self.fields['phone'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '+56 9 1234 5678'
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-checkbox'
        })