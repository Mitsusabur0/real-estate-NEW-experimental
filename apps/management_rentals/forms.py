from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Field

from .models import RentalAgreement, MonthlyRental


class RentalAgreementForm(forms.ModelForm):
    """Form for creating and updating rental agreements."""
    
    class Meta:
        model = RentalAgreement
        fields = [
            'property', 'owner', 'tenant', 'rent_amount', 
            'commission_amount', 'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter owners and tenants by client type
        from apps.management_clients.models import Client
        self.fields['owner'].queryset = Client.objects.filter(client_type=Client.ClientType.OWNER)
        self.fields['tenant'].queryset = Client.objects.filter(client_type=Client.ClientType.TENANT)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('property', css_class='form-group col-md-6'),
                Column('is_active', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('owner', css_class='form-group col-md-6'),
                Column('tenant', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('rent_amount', css_class='form-group col-md-6'),
                Column('commission_amount', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('start_date', css_class='form-group col-md-6'),
                Column('end_date', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', 'Save', css_class='btn-primary')
        )
    
    def clean(self):
        """Additional form validation."""
        cleaned_data = super().clean()
        
        # If this is an update, ensure we're not trying to change property or owner
        if self.instance.pk:
            if self.instance.property != cleaned_data.get('property'):
                self.add_error('property', "Cannot change property once agreement is created")
            
            if self.instance.owner != cleaned_data.get('owner'):
                self.add_error('owner', "Cannot change owner once agreement is created")
        
        return cleaned_data


class RentalAgreementTerminationForm(forms.Form):
    """Form for terminating a rental agreement."""
    termination_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="When the rental agreement will end"
    )
    reason = forms.CharField(
        widget=forms.Textarea(),
        required=False,
        help_text="Reason for termination"
    )
    delete_future_records = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Delete future monthly rental records"
    )
    
    def __init__(self, *args, **kwargs):
        self.rental_agreement = kwargs.pop('rental_agreement')
        super().__init__(*args, **kwargs)
        
        # Set min date to today
        self.fields['termination_date'].initial = timezone.now().date()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('termination_date'),
            Field('reason'),
            Field('delete_future_records'),
            Submit('submit', 'Terminate Agreement', css_class='btn-danger')
        )
    
    def clean_termination_date(self):
        """Validate termination date."""
        termination_date = self.cleaned_data.get('termination_date')
        
        if not self.rental_agreement.is_termination_date_valid(termination_date):
            raise forms.ValidationError("Invalid termination date")
        
        return termination_date


class RecordPaymentForm(forms.ModelForm):
    """Form for recording a rent payment."""
    
    class Meta:
        model = MonthlyRental
        fields = ['payment_date', 'rent_status', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_date'].initial = timezone.now().date()
        self.fields['rent_status'].choices = [
            (MonthlyRental.PAID, 'Paid'),
            (MonthlyRental.LATE, 'Late'),
        ]
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('rent_status'),
            Field('payment_date'),
            Field('notes'),
            Submit('submit', 'Record Payment', css_class='btn-success')
        )


class RecordTransferForm(forms.ModelForm):
    """Form for recording a transfer to owner."""
    
    class Meta:
        model = MonthlyRental
        fields = ['transfer_date', 'transfer_amount', 'notes']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transfer_date'].initial = timezone.now().date()
        
        # If this is an existing instance, set initial transfer_amount
        if kwargs.get('instance'):
            instance = kwargs['instance']
            if not instance.transfer_amount:
                self.fields['transfer_amount'].initial = instance.rental_agreement.calculate_transfer_amount()
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('transfer_amount'),
            Field('transfer_date'),
            Field('notes'),
            Submit('submit', 'Record Transfer', css_class='btn-success')
        )
    
    def save(self, commit=True):
        """Override save to set transfer_status."""
        instance = super().save(commit=False)
        instance.transfer_status = 'completed'
        if commit:
            instance.save()
        return instance


class MonthFilterForm(forms.Form):
    """Form for filtering monthly rentals by year and month."""
    year = forms.ChoiceField(label="Year")
    month = forms.ChoiceField(
        label="Month",
        choices=[
            (1, 'January'), (2, 'February'), (3, 'March'),
            (4, 'April'), (5, 'May'), (6, 'June'),
            (7, 'July'), (8, 'August'), (9, 'September'),
            (10, 'October'), (11, 'November'), (12, 'December')
        ]
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate years from current year minus 3 to current year plus 1
        current_year = timezone.now().year
        years = [(year, year) for year in range(current_year - 3, current_year + 2)]
        self.fields['year'].choices = years
        self.fields['year'].initial = current_year
        
        # Set initial month to current month
        current_month = timezone.now().month
        self.fields['month'].initial = current_month
        
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            Field('year', css_class='mr-2'),
            Field('month', css_class='mr-2'),
            Submit('submit', 'Filter', css_class='btn-info')
        )