# REAL_ESTATE_MANAGER/apps/management_properties/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Property(models.Model):
    class PropertyType(models.TextChoices):
        HOUSE = 'HOUSE', 'Casa'
        APARTMENT = 'APT', 'Departamento'
        OFFICE = 'OFC', 'Oficina'
        LAND = 'LAND', 'Terreno'

    class OfferType(models.TextChoices):
        RENT = 'RENT', 'Arriendo'
        SALE = 'SALE', 'Venta'
    
    class PropertyStatus(models.TextChoices):
        AVAILABLE = 'AVL', 'Disponible'
        RESERVED = 'RSV', 'Reservada'
        RENTED = 'RNT', 'Arrendada'
        SOLD = 'SLD', 'Vendida'

    # Property identification
    property_code = models.CharField(max_length=10, unique=True, editable=False)
    address = models.CharField(max_length=255)
    
    # Owner information
    current_owner = models.ForeignKey(
        'management_clients.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        help_text="Current owner of the property"
    )

    # Property characteristics
    property_type = models.CharField(
        max_length=10, 
        choices=PropertyType.choices,
        default=PropertyType.HOUSE
    )
    offer_type = models.CharField(
        max_length=4, 
        choices=OfferType.choices
    )
    status = models.CharField(
        max_length=3,
        choices=PropertyStatus.choices,
        default=PropertyStatus.AVAILABLE
    )
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=0, 
        validators=[MinValueValidator(0)]
    )
    common_expenses = models.DecimalField(
        max_digits=8, 
        decimal_places=0, 
        validators=[MinValueValidator(0)], 
        null=True, 
        blank=True
    )
    square_meters = models.DecimalField(
        max_digits=8, 
        decimal_places=0, 
        validators=[MinValueValidator(0)]
    )
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    has_parking = models.BooleanField(default=False)
    has_storage_unit = models.BooleanField(default=False)
    floor_number = models.IntegerField(null=True, blank=True)
    
    # Additional information
    amenities = models.TextField(blank=True)
    pets_allowed = models.BooleanField(default=False)
    requirements = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    property_description = models.TextField()
    
    # Dates
    date_published = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def change_owner(self, new_owner, change_date=None):
        """
        Changes the current owner of the property and creates a historical record.
        
        Args:
            new_owner (Client): The new owner of the property
            change_date (date, optional): Date of ownership change. Defaults to today.
        """
        from apps.management_clients.models import PropertyOwnership
        
        change_date = change_date or timezone.now().date()
        
        # If there was a previous owner, close their ownership period
        if self.current_owner:
            # Get the latest ownership record
            current_ownership = PropertyOwnership.objects.filter(
                property=self,
                owner=self.current_owner,
                end_date=None
            ).first()
            
            if current_ownership:
                current_ownership.end_date = change_date
                current_ownership.save()
                
        # Only create new ownership record if there's a new owner
        if new_owner is not None:
            PropertyOwnership.objects.create(
                property=self,
                owner=new_owner,
                start_date=change_date
            )
        
        # Update current owner
        self.current_owner = new_owner
        self.save()

    def save(self, *args, **kwargs):
        if not self.property_code:
            last_property = Property.objects.order_by('-property_code').first()
            if not last_property:
                next_number = 1
            else:
                last_number = int(last_property.property_code[1:])
                next_number = last_number + 1
            self.property_code = f'P{next_number:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.property_code} - {self.address} ({self.get_property_type_display()})"

    class Meta:
        verbose_name_plural = "Properties"