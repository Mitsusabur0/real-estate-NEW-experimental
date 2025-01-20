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
        'date_published'
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
                'status'
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