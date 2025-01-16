from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Property
from .forms import PropertyForm

class PropertyListView(LoginRequiredMixin, ListView):
    model = Property
    template_name = 'management_properties/property_list.html'
    context_object_name = 'properties'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add basic filtering
        status = self.request.GET.get('status')
        property_type = self.request.GET.get('type')
        offer_type = self.request.GET.get('offer')
        
        if status:
            queryset = queryset.filter(status=status)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if offer_type:
            queryset = queryset.filter(offer_type=offer_type)
            
        return queryset.order_by('status', '-created_at')

class PropertyDetailView(LoginRequiredMixin, DetailView):
    model = Property
    template_name = 'management_properties/property_detail.html'
    context_object_name = 'property'
    slug_field = 'property_code'
    slug_url_kwarg = 'property_code'

class PropertyCreateView(LoginRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = 'management_properties/property_form.html'
    
    def get_success_url(self):
        return reverse_lazy('properties:property_detail', 
                          kwargs={'property_code': self.object.property_code})

class PropertyUpdateView(LoginRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = 'management_properties/property_form.html'
    slug_field = 'property_code'
    slug_url_kwarg = 'property_code'
    
    def get_success_url(self):
        return reverse_lazy('properties:property_detail', 
                          kwargs={'property_code': self.object.property_code})

class PropertyDeleteView(LoginRequiredMixin, DeleteView):
    model = Property
    template_name = 'management_properties/property_confirm_delete.html'
    success_url = reverse_lazy('properties:property_list')
    slug_field = 'property_code'
    slug_url_kwarg = 'property_code'