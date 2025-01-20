# apps/management_clients/urls.py

from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # List view - shows all clients
    path('', views.ClientListView.as_view(), name='client_list'),
]