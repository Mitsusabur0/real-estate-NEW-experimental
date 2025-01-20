from django.db import models
from django.core.validators import MinValueValidator

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

    property_code = models.CharField(max_length=10, unique=True, editable=False)
    address = models.CharField(max_length=255)
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
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)])
    common_expenses = models.DecimalField(max_digits=8, decimal_places=0, validators=[MinValueValidator(0)], null=True, blank=True)
    square_meters = models.DecimalField(max_digits=8, decimal_places=0, validators=[MinValueValidator(0)])
    bedrooms = models.PositiveSmallIntegerField()
    bathrooms = models.PositiveSmallIntegerField()
    has_parking = models.BooleanField(default=False)
    has_storage_unit = models.BooleanField(default=False)
    floor_number = models.IntegerField(null=True, blank=True)
    amenities = models.TextField(blank=True)
    pets_allowed = models.BooleanField(default=False)
    requirements = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    property_description = models.TextField()
    date_published = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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