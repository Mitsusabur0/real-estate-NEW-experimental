# apps/management_rentals/forms.py
from django import forms
from .models import RentalManagement
from apps.management_clients.models import Client
from apps.management_clients.forms import TenantForm
from django.utils import timezone

class RentalManagementForm(forms.ModelForm):
    class Meta:
        model = RentalManagement
        fields = [
            'rental_property', 'owner', 'tenant', 'month_year',
            'rent_amount', 'commission_amount', 'rent_status',
            'transfer_status', 'comments'
        ]
        widgets = {
            'month_year': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter owner choices to show only active owners
        self.fields['owner'].queryset = Client.objects.filter(
            client_type=Client.ClientType.OWNER,
            is_active=True
        )
        
        # Filter tenant choices to show only active tenants
        self.fields['tenant'].queryset = Client.objects.filter(
            client_type=Client.ClientType.TENANT,
            is_active=True
        )

        # If this is a new instance, set default month_year to first day of current month
        if not self.instance.pk:
            today = timezone.now()
            self.fields['month_year'].initial = today.replace(day=1)

        # Add styling classes and placeholders
        self.fields['rental_property'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['owner'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['tenant'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['rent_amount'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '$'
        })
        self.fields['commission_amount'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': '$'
        })
        self.fields['month_year'].widget.attrs.update({
            'class': 'form-field'
        })
        self.fields['rent_status'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['transfer_status'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['comments'].widget.attrs.update({
            'class': 'form-field',
            'placeholder': 'Comentarios adicionales...'
        })

    def clean(self):
        cleaned_data = super().clean()
        rental_property = cleaned_data.get('rental_property')
        month_year = cleaned_data.get('month_year')
        
        # Check if there's already a management for this property in this month
        if rental_property and month_year:
            existing = RentalManagement.objects.filter(
                rental_property=rental_property,
                month_year__month=month_year.month,
                month_year__year=month_year.year
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    'Ya existe una gestión para esta propiedad en el mes seleccionado.'
                )
        
        return cleaned_data

class CreateTenantForm(TenantForm):
    """Form for creating a new tenant from the rental management page"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any additional tenant-specific fields or customizations here