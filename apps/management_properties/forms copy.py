from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            'address', 'property_type', 'offer_type', 'status',
            'price', 'common_expenses', 'square_meters',
            'bedrooms', 'bathrooms', 'has_parking',
            'has_storage_unit', 'floor_number', 'amenities',
            'pets_allowed', 'requirements', 'comments',
            'property_description', 'date_published'
        ]
        widgets = {
            'date_published': forms.DateInput(attrs={'type': 'date'}),
            'property_description': forms.Textarea(attrs={'rows': 4}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 3}),
            'amenities': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'price': 'Enter the price in Chilean Pesos (CLP)',
            'common_expenses': 'Monthly maintenance fees, if applicable',
            'requirements': 'List any specific requirements for potential buyers/tenants',
            'floor_number': 'Only for apartments or offices'
        }

    def clean(self):
        cleaned_data = super().clean()
        property_type = cleaned_data.get('property_type')
        floor_number = cleaned_data.get('floor_number')
        
        # Validate floor number for houses
        if property_type == 'HOUSE' and floor_number:
            raise forms.ValidationError({
                'floor_number': 'Las casas no pueden tener número de piso. Este campo solo aplica para departamentos u oficinas.'
            })
        
        # Additional validation example:
        # Ensure houses have at least 1 bedroom
        if property_type == 'HOUSE' and cleaned_data.get('bedrooms', 0) < 1:
            raise forms.ValidationError({
                'bedrooms': 'Las casas deben tener al menos 1 dormitorio.'
            })

        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')
        offer_type = self.cleaned_data.get('offer_type')
        
        if offer_type == 'RENT' and price and price > 5000000:  # 5 million pesos
            raise forms.ValidationError(
                'Los precios de arriendo superiores a $5.000.000 necesitan verificación. Por favor, revise el monto.'
            )
        return price