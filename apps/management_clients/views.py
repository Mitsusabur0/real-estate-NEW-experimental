# apps/management_clients/views.py

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from .models import Client
from .forms import ClientForm
from django.db.models import Count, Q

# class ClientListView(LoginRequiredMixin, ListView):
#     model = Client
#     template_name = 'management_clients/client_list.html'
#     context_object_name = 'clients'
#     paginate_by = 10
    
#     def get_queryset(self):
#         queryset = super().get_queryset()
        
#         # Add filtering by active status
#         status = self.request.GET.get('status')
#         if status == 'active':
#             queryset = queryset.filter(is_active=True)
#         elif status == 'inactive':
#             queryset = queryset.filter(is_active=False)
            
#         # Add search functionality
#         search = self.request.GET.get('search')
#         if search:
#             queryset = queryset.filter(name__icontains=search) | \
#                       queryset.filter(email__icontains=search)
        
#         return queryset.order_by('-is_active', 'name')


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'management_clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10
    
    # def get_queryset(self):
    #     queryset = super().get_queryset().annotate(
    #         current_properties_count=Count('properties')
    #     )        
    #     status = self.request.GET.get('status')
    #     if status == 'active':
    #         queryset = queryset.filter(is_active=True)
    #     elif status == 'inactive':
    #         queryset = queryset.filter(is_active=False)
            
    #     search = self.request.GET.get('search')
    #     if search:
    #         queryset = queryset.filter(
    #             Q(name__icontains=search) | 
    #             Q(email__icontains=search)
    #         )
        
    #     return queryset.order_by('-is_active', 'name')
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            current_properties_count=Count('properties')
        ).filter(client_type=Client.ClientType.OWNER)  # Add this line to filter only owners
        
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(email__icontains=search)
            )
        
        return queryset.order_by('-is_active', 'name')

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'management_clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Propietario creado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'management_clients/client_form.html'
    success_url = reverse_lazy('clients:client_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Propietario actualizado exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario.')
        return super().form_invalid(form)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'management_clients/client_confirm_delete.html'
    success_url = reverse_lazy('clients:client_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add property count to context
        context['property_count'] = self.object.property_set.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.property_set.exists():
            messages.error(request, 
                'No se puede eliminar el propietario porque tiene propiedades asociadas.')
            return redirect('clients:client_list')
        
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, 'Propietario eliminado exitosamente.')
        return redirect(success_url)
    

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'management_clients/client_detail.html'
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the clients properties ordered by address
        context['properties'] = self.object.properties.all().order_by('address')
        return context          