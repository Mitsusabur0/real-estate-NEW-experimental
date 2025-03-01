# REAL_ESTATE_MANAGER/apps/management_properties/admin.py

from django.contrib import admin
from .models import Property

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    # List view configuration
    list_display = (
        'property_code',
        'address',
        'property_type',
        'offer_type',
        'status',
        'price',
        'square_meters',
        'date_published',
        'current_owner'  # Added current_owner to list display
    )
    
    list_filter = (
        'status',
        'property_type',
        'offer_type',
        'bedrooms',
        'bathrooms',
        'has_parking',
        'has_storage_unit',
        # 'pets_allowed'
    )
    
    readonly_fields = ('property_code', 'created_at', 'updated_at')
    
    # Detail view configuration with fieldsets
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'property_code',
                'property_type',
                'offer_type',
                'status',
                'current_owner'  # Added current_owner field
            )
        }),
        ('Location Details', {
            'fields': (
                'address',
                'floor_number'
            )
        }),
        ('Property Characteristics', {
            'fields': (
                'square_meters',
                'bedrooms',
                'bathrooms',
                'has_parking',
                'has_storage_unit',
                'pets_allowed'
            )
        }),
        ('Commercial Information', {
            'fields': (
                'price',
                'common_expenses',
                'date_published'
            )
        }),
        ('Additional Information', {
            'fields': (
                'property_description',
                'amenities',
                'requirements',
                'comments'
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    # Ordering
    ordering = ('-date_published', 'property_code')

    def save_model(self, request, obj, form, change):
        if change:  # If this is an edit, not a new property
            old_obj = Property.objects.get(pk=obj.pk)
            if old_obj.current_owner != obj.current_owner:
                # Owner has changed, use our method
                super().save_model(request, obj, form, change)
                obj.change_owner(obj.current_owner)
            else:
                # No owner change, normal save
                super().save_model(request, obj, form, change)
        else:
            # New property
            super().save_model(request, obj, form, change)
            if obj.current_owner:
                # If new property has an owner, create initial ownership record
                obj.change_owner(obj.current_owner)