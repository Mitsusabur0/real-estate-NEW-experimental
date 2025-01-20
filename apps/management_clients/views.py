# apps/management_clients/views.py

from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Client

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'management_clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add filtering by active status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        # Add search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search) | \
                      queryset.filter(email__icontains=search)
        
        # Order by status (active first) and then by name
        return queryset.order_by('-is_active', 'name')