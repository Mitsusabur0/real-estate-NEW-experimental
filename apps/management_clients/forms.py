# apps/management_clients/forms.py

from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'is_active', 'client_type']
        
    def __init__(self, *args, client_type=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add required field indicators and custom styling
        self.fields['name'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Nombre completo'
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
        
        # If client_type is specified, hide the field and set the value
        if client_type:
            self.fields['client_type'].widget = forms.HiddenInput()
            self.fields['client_type'].initial = client_type
        else:
            self.fields['client_type'].widget.attrs.update({
                'class': 'form-select'
            })

class OwnerForm(ClientForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, client_type=Client.ClientType.OWNER, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Nombre completo del propietario'
        self.fields['client_type'].initial = Client.ClientType.OWNER
        self.fields['client_type'].widget = forms.HiddenInput()
        # Add this to make sure the value is set even if not in form data
        if not self.data.get('client_type'):
            self.data = self.data.copy()
            self.data['client_type'] = Client.ClientType.OWNER

class TenantForm(ClientForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, client_type=Client.ClientType.TENANT, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Nombre completo del arrendatario'