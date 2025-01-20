# apps/management_clients/urls.py

from django.urls import path
from apps.management_clients import views

app_name = 'clients'

urlpatterns = [
    # List view - shows all clients
    path('', views.ClientListView.as_view(), name='client_list'),
    
    # Create view - add new client
    path('create/', views.ClientCreateView.as_view(), name='client_create'),
    
    # Update view - edit existing client
    path('<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    
    # Delete view - remove client
    path('<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
]