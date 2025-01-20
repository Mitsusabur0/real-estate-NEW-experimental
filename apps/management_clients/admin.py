# REAL_ESTATE_MANAGER/apps/management_clients/admin.py

from django.contrib import admin
from .models import Client, PropertyOwnership

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'email']


@admin.register(PropertyOwnership)
class PropertyOwnershipAdmin(admin.ModelAdmin):
    list_display = ['property', 'owner', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['property__property_code', 'owner__name']