# apps/management_rentals/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import F
from .models import RentalManagement
from .forms import RentalManagementForm, CreateTenantForm
from apps.management_clients.models import Client
from django.contrib.auth.mixins import LoginRequiredMixin

class RentalManagementListView(LoginRequiredMixin, ListView):
    model = RentalManagement
    template_name = 'management_rentals/rental_management_list.html'
    context_object_name = 'managements'

    def get_queryset(self):
        queryset = super().get_queryset()
        
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        
        if month and year:
            queryset = queryset.filter(
                month_year__month=month,
                month_year__year=year
            )
            
        return queryset.select_related('rental_property', 'owner', 'tenant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        years = RentalManagement.objects.dates('month_year', 'year')
        months = range(1, 13)
        
        context.update({
            'years': years,
            'months': months,
            'current_month': self.request.GET.get('month'),
            'current_year': self.request.GET.get('year')
        })
        return context

class RentalManagementCreateView(LoginRequiredMixin, CreateView):
    model = RentalManagement
    form_class = RentalManagementForm
    template_name = 'management_rentals/rental_management_form.html'
    success_url = reverse_lazy('rentals:list')  # Updated URL name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tenant_form'] = CreateTenantForm()
        return context

class RentalManagementUpdateView(LoginRequiredMixin, UpdateView):
    model = RentalManagement
    form_class = RentalManagementForm
    template_name = 'management_rentals/rental_management_form.html'
    success_url = reverse_lazy('rentals:list')  # Updated URL name

class RentalManagementDeleteView(LoginRequiredMixin, DeleteView):
    model = RentalManagement
    template_name = 'management_rentals/rental_management_confirm_delete.html'
    success_url = reverse_lazy('rentals:list')  # Updated URL name

class CreateTenantView(LoginRequiredMixin, FormView):
    form_class = CreateTenantForm
    template_name = 'management_rentals/tenant_form.html'
    success_url = reverse_lazy('rentals:create')

    def form_valid(self, form):
        print("Form submission received")  # Debug line
        print("Is AJAX?:", self.request.headers.get('x-requested-with') == 'XMLHttpRequest')  # Debug line
        tenant = form.save()
        messages.success(self.request, 'Arrendatario creado exitosamente.')
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'id': tenant.id,
                'name': tenant.name
            })
            
        return redirect('rentals:create')