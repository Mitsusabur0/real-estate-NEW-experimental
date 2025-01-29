# apps/management_rentals/urls.py

from django.urls import path
from . import views

app_name = 'rentals'  # Add namespace

urlpatterns = [
    path('', views.RentalManagementListView.as_view(), name='list'),
    path('create/', views.RentalManagementCreateView.as_view(), name='create'),
    path('<int:pk>/update/', views.RentalManagementUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.RentalManagementDeleteView.as_view(), name='delete'),
    path('tenant/create/', views.CreateTenantView.as_view(), name='tenant_create'),
]