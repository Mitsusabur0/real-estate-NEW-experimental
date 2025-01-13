from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # List view - shows all properties
    path('', views.PropertyListView.as_view(), name='property_list'),
    
    # Create view - add new property
    path('create/', views.PropertyCreateView.as_view(), name='property_create'),

    # Detail view - shows single property details
    path('<str:property_code>/', views.PropertyDetailView.as_view(), name='property_detail'),
    
    # Update view - edit existing property
    path('<str:property_code>/edit/', views.PropertyUpdateView.as_view(), name='property_update'),
    
    # Delete view - remove property
    path('<str:property_code>/delete/', views.PropertyDeleteView.as_view(), name='property_delete'),
]