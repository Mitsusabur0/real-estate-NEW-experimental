from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.views.generic.edit import ModelFormMixin
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import RentalAgreement, MonthlyRental
from .forms import (
    RentalAgreementForm, RentalAgreementTerminationForm,
    RecordPaymentForm, RecordTransferForm, MonthFilterForm
)


class RentalAgreementListView(LoginRequiredMixin, ListView):
    """View for displaying all rental agreements."""
    model = RentalAgreement
    context_object_name = 'rental_agreements'
    
    def get_queryset(self):
        """Filter queryset based on active status and search parameters."""
        queryset = super().get_queryset()
        
        # Filter by active status if specified
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search by property address or tenant name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(property__address__icontains=search) |
                Q(tenant__first_name__icontains=search) |
                Q(tenant__last_name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['status'] = self.request.GET.get('status', '')
        context['search'] = self.request.GET.get('search', '')
        return context


class RentalAgreementDetailView(LoginRequiredMixin, DetailView):
    """View for displaying details of a rental agreement."""
    model = RentalAgreement
    context_object_name = 'rental_agreement'
    
    def get_context_data(self, **kwargs):
        """Add monthly rentals to context."""
        context = super().get_context_data(**kwargs)
        
        # Get monthly rentals for this agreement, ordered by date
        monthly_rentals = self.object.monthly_rentals.all().order_by('-period_year', '-period_month')
        context['monthly_rentals'] = monthly_rentals
        
        # Add stats for rental agreement
        paid_rentals = monthly_rentals.filter(rent_status='paid').count()
        pending_rentals = monthly_rentals.filter(rent_status='pending').count()
        late_rentals = monthly_rentals.filter(rent_status='late').count()
        unpaid_rentals = monthly_rentals.filter(rent_status='unpaid').count()
        
        context['rental_stats'] = {
            'paid': paid_rentals,
            'pending': pending_rentals,
            'late': late_rentals,
            'unpaid': unpaid_rentals,
            'total': monthly_rentals.count()
        }
        
        # Calculate financial summary
        total_rent = self.object.rent_amount * monthly_rentals.count()
        total_paid = self.object.rent_amount * paid_rentals
        total_commission = self.object.commission_amount * paid_rentals
        
        context['financial_summary'] = {
            'total_rent': total_rent,
            'total_paid': total_paid,
            'total_commission': total_commission,
            'total_transfers': total_paid - total_commission
        }
        
        return context


class RentalAgreementCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new rental agreement."""
    model = RentalAgreement
    form_class = RentalAgreementForm
    
    def get_context_data(self, **kwargs):
        """Add today's date to context."""
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context
    
    def get_success_url(self):
        """Return URL to redirect to on successful creation."""
        return reverse('management_rentals:rental_agreement_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process valid form data."""
        messages.success(self.request, 'Rental agreement created successfully!')
        return super().form_valid(form)


class RentalAgreementUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating an existing rental agreement."""
    model = RentalAgreement
    form_class = RentalAgreementForm
    
    def get_context_data(self, **kwargs):
        """Add today's date to context."""
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context
    
    def get_success_url(self):
        """Return URL to redirect to on successful update."""
        return reverse('management_rentals:rental_agreement_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process valid form data."""
        messages.success(self.request, 'Rental agreement updated successfully!')
        return super().form_valid(form)


class RentalAgreementDeleteView(LoginRequiredMixin, DeleteView):
    """View for deleting a rental agreement."""
    model = RentalAgreement
    success_url = reverse_lazy('management_rentals:rental_agreement_list')
    
    def delete(self, request, *args, **kwargs):
        """Override delete method to add success message."""
        messages.success(request, 'Rental agreement deleted successfully!')
        return super().delete(request, *args, **kwargs)


class RentalAgreementTerminateView(LoginRequiredMixin, FormView):
    """View for terminating a rental agreement."""
    template_name = 'management_rentals/rental_agreement_terminate.html'
    form_class = RentalAgreementTerminationForm
    
    def get_form_kwargs(self):
        """Pass rental agreement to form."""
        kwargs = super().get_form_kwargs()
        self.rental_agreement = get_object_or_404(RentalAgreement, pk=self.kwargs['pk'])
        kwargs['rental_agreement'] = self.rental_agreement
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add rental agreement to context."""
        context = super().get_context_data(**kwargs)
        context['rental_agreement'] = self.rental_agreement
        context['today'] = timezone.now().date()
        return context
    
    def form_valid(self, form):
        """Process valid form data."""
        termination_date = form.cleaned_data['termination_date']
        delete_future_records = form.cleaned_data['delete_future_records']
        reason = form.cleaned_data['reason']
        
        # Update rental agreement
        self.rental_agreement.is_active = False
        self.rental_agreement.end_date = termination_date
        self.rental_agreement.save()
        
        # Add termination reason to notes if provided
        if reason:
            termination_month = MonthlyRental.objects.filter(
                rental_agreement=self.rental_agreement,
                period_year=termination_date.year,
                period_month=termination_date.month
            ).first()
            
            if termination_month:
                termination_month.notes += f"\nTermination reason: {reason}"
                termination_month.save()
        
        # Delete future monthly rental records if requested
        if delete_future_records:
            future_records = MonthlyRental.objects.filter(
                rental_agreement=self.rental_agreement,
                period_year__gt=termination_date.year
            ) | MonthlyRental.objects.filter(
                rental_agreement=self.rental_agreement,
                period_year=termination_date.year,
                period_month__gt=termination_date.month
            )
            
            future_records.delete()
        
        messages.success(self.request, 'Rental agreement terminated successfully!')
        return HttpResponseRedirect(reverse('management_rentals:rental_agreement_detail', 
                                            kwargs={'pk': self.rental_agreement.pk}))


class DashboardView(LoginRequiredMixin, TemplateView):
    """View for the main rental dashboard."""
    template_name = 'management_rentals/dashboard.html'
    
    def get_context_data(self, **kwargs):
        """Add monthly rentals and filter form to context."""
        context = super().get_context_data(**kwargs)
        
        # Get year and month from request or use current date
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        today = timezone.now().date()
        context['today'] = today
        current_year = today.year
        current_month = today.month
        
        try:
            year = int(year) if year else current_year
            month = int(month) if month else current_month
        except ValueError:
            year = current_year
            month = current_month
        
        try:
            # Get monthly rentals for the selected period
            monthly_rentals = MonthlyRental.objects.filter(
                period_year=year,
                period_month=month
            )
            
            # Create filter form
            filter_form = MonthFilterForm(initial={'year': year, 'month': month})
            
            # Check if month needs initialization
            active_agreements = RentalAgreement.objects.filter(is_active=True)
            initialized_count = monthly_rentals.count()
            needs_initialization = initialized_count < active_agreements.count()
            
            # Get rental stats
            total_rent = monthly_rentals.aggregate(
                total=Sum('rental_agreement__rent_amount')
            )['total'] or 0
            
            total_commission = monthly_rentals.aggregate(
                total=Sum('rental_agreement__commission_amount')
            )['total'] or 0
            
            pending_payments = monthly_rentals.filter(rent_status='pending').count()
            pending_transfers = monthly_rentals.filter(
                rent_status='paid', 
                transfer_status='pending'
            ).count()
            
            # Add to context
            context.update({
                'monthly_rentals': monthly_rentals,
                'filter_form': filter_form,
                'selected_year': year,
                'selected_month': month,
                'needs_initialization': needs_initialization,
                'stats': {
                    'total_rent': total_rent,
                    'total_commission': total_commission,
                    'total_transfer': total_rent - total_commission,
                    'pending_payments': pending_payments,
                    'pending_transfers': pending_transfers
                }
            })
        except Exception as e:
            # Handle database errors gracefully
            messages.error(self.request, f"Could not load dashboard data. Database may not be fully migrated: {str(e)}")
            context.update({
                'filter_form': MonthFilterForm(initial={'year': year, 'month': month}),
                'selected_year': year,
                'selected_month': month,
                'monthly_rentals': [],
                'needs_initialization': False,
                'stats': {
                    'total_rent': 0,
                    'total_commission': 0,
                    'total_transfer': 0,
                    'pending_payments': 0,
                    'pending_transfers': 0
                },
                'error_loading_data': True
            })
        
        return context


@method_decorator(require_POST, name='dispatch')
class InitializeMonthView(LoginRequiredMixin, TemplateView):
    """View for initializing a month's rental records."""
    template_name = 'management_rentals/initialize_month.html'
    
    def post(self, request, *args, **kwargs):
        """Process POST request to initialize a month."""
        year = int(request.POST.get('year', timezone.now().year))
        month = int(request.POST.get('month', timezone.now().month))
        
        try:
            created, existing = MonthlyRental.initialize_month(year, month)
            
            messages.success(
                request, 
                f'Month initialized successfully! {created} new records created, {existing} already existed.'
            )
        except Exception as e:
            messages.error(
                request,
                f'Error initializing month: {str(e)}. Please ensure database migrations are up to date.'
            )
        
        return redirect(reverse('management_rentals:dashboard') + f'?year={year}&month={month}')


class MonthlyRentalDetailView(LoginRequiredMixin, DetailView):
    """View for displaying details of a monthly rental."""
    model = MonthlyRental
    context_object_name = 'monthly_rental'
    
    def get_context_data(self, **kwargs):
        """Add rental agreement to context."""
        context = super().get_context_data(**kwargs)
        context['rental_agreement'] = self.object.rental_agreement
        return context


class RecordPaymentView(LoginRequiredMixin, UpdateView):
    """View for recording a rent payment."""
    model = MonthlyRental
    form_class = RecordPaymentForm
    template_name = 'management_rentals/record_payment.html'
    
    def get_context_data(self, **kwargs):
        """Add rental agreement to context."""
        context = super().get_context_data(**kwargs)
        context['rental_agreement'] = self.object.rental_agreement
        context['today'] = timezone.now().date()
        return context
    
    def get_success_url(self):
        """Return URL to redirect to on successful update."""
        return reverse('management_rentals:monthly_rental_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process valid form data."""
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)


class RecordTransferView(LoginRequiredMixin, UpdateView):
    """View for recording a transfer to owner."""
    model = MonthlyRental
    form_class = RecordTransferForm
    template_name = 'management_rentals/record_transfer.html'
    
    def get_context_data(self, **kwargs):
        """Add rental agreement to context."""
        context = super().get_context_data(**kwargs)
        context['rental_agreement'] = self.object.rental_agreement
        context['today'] = timezone.now().date()
        return context
    
    def get_success_url(self):
        """Return URL to redirect to on successful update."""
        return reverse('management_rentals:monthly_rental_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process valid form data."""
        messages.success(self.request, 'Transfer recorded successfully!')
        return super().form_valid(form)


class ReportView(LoginRequiredMixin, TemplateView):
    """View for displaying rental reports."""
    template_name = 'management_rentals/report.html'
    
    def get_context_data(self, **kwargs):
        """Add report data to context."""
        context = super().get_context_data(**kwargs)
        
        # Get year from request or use current year
        year = self.request.GET.get('year')
        
        today = timezone.now().date()
        context['today'] = today
        
        try:
            year = int(year) if year else today.year
        except ValueError:
            year = today.year
        
        # Get monthly statistics for the selected year
        monthly_stats = []
        
        for month in range(1, 13):
            # Get monthly rentals for this period
            monthly_rentals = MonthlyRental.objects.filter(
                period_year=year,
                period_month=month
            )
            
            # Calculate statistics
            total_rent = monthly_rentals.aggregate(
                total=Sum('rental_agreement__rent_amount')
            )['total'] or 0
            
            total_commission = monthly_rentals.aggregate(
                total=Sum('rental_agreement__commission_amount')
            )['total'] or 0
            
            paid_count = monthly_rentals.filter(rent_status='paid').count()
            pending_count = monthly_rentals.filter(rent_status='pending').count()
            late_count = monthly_rentals.filter(rent_status='late').count()
            unpaid_count = monthly_rentals.filter(rent_status='unpaid').count()
            
            monthly_stats.append({
                'month': month,
                'month_name': [
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'
                ][month-1],
                'total_rent': total_rent,
                'total_commission': total_commission,
                'total_transfer': total_rent - total_commission,
                'paid_count': paid_count,
                'pending_count': pending_count,
                'late_count': late_count,
                'unpaid_count': unpaid_count,
                'total_count': monthly_rentals.count()
            })
        
        # Calculate annual totals
        annual_rentals = MonthlyRental.objects.filter(period_year=year)
        
        annual_total_rent = annual_rentals.aggregate(
            total=Sum('rental_agreement__rent_amount')
        )['total'] or 0
        
        annual_total_commission = annual_rentals.aggregate(
            total=Sum('rental_agreement__commission_amount')
        )['total'] or 0
        
        # Add to context
        context.update({
            'monthly_stats': monthly_stats,
            'selected_year': year,
            'annual_stats': {
                'total_rent': annual_total_rent,
                'total_commission': annual_total_commission,
                'total_transfer': annual_total_rent - annual_total_commission
            }
        })
        
        return context