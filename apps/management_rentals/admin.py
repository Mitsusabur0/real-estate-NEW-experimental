from django.contrib import admin
from .models import RentalAgreement, MonthlyRental


class MonthlyRentalInline(admin.TabularInline):
    """Inline admin for monthly rentals."""
    model = MonthlyRental
    extra = 0
    fields = ('period_year', 'period_month', 'rent_status', 'payment_date', 
              'transfer_status', 'transfer_date', 'transfer_amount')
    readonly_fields = ('period_year', 'period_month')


@admin.register(RentalAgreement)
class RentalAgreementAdmin(admin.ModelAdmin):
    """Admin for rental agreements."""
    list_display = ('property', 'owner', 'tenant', 'rent_amount', 
                   'commission_amount', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('property__address', 'owner__first_name', 'owner__last_name',
                    'tenant__first_name', 'tenant__last_name')
    date_hierarchy = 'start_date'
    inlines = [MonthlyRentalInline]
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields readonly after creation."""
        if obj: # editing an existing object
            return ('property', 'owner')
        return ()


@admin.register(MonthlyRental)
class MonthlyRentalAdmin(admin.ModelAdmin):
    """Admin for monthly rentals."""
    list_display = ('rental_agreement', 'period_month', 'period_year', 
                   'rent_status', 'payment_date', 'transfer_status', 'transfer_date')
    list_filter = ('rent_status', 'transfer_status', 'period_year', 'period_month')
    search_fields = ('rental_agreement__property__address', 
                    'rental_agreement__owner__first_name', 'rental_agreement__owner__last_name',
                    'rental_agreement__tenant__first_name', 'rental_agreement__tenant__last_name')
    date_hierarchy = 'payment_date'
    fieldsets = (
        (None, {
            'fields': ('rental_agreement', 'period_year', 'period_month')
        }),
        ('Rent Information', {
            'fields': ('rent_status', 'payment_date')
        }),
        ('Transfer Information', {
            'fields': ('transfer_amount', 'transfer_status', 'transfer_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    readonly_fields = ('rental_agreement', 'period_year', 'period_month')