# apps/management_rentals/models.py
from django.db import models
from django.core.validators import MinValueValidator
from apps.management_properties.models import Property
from apps.management_clients.models import Client
from django.utils import timezone

class RentalManagement(models.Model):
    """Represents a monthly rental management entry"""
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        PAID = 'PAID', 'Pagado'
    
    class TransferStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        ON_HOLD = 'ON_HOLD', 'En Espera'
        PAID = 'PAID', 'Pagado'

    rental_property = models.ForeignKey(
        Property,
        on_delete=models.PROTECT,
        related_name='rental_managements'
    )
    owner = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='properties_rented_out',
        limit_choices_to={'client_type': Client.ClientType.OWNER}
    )
    tenant = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='rented_properties',
        limit_choices_to={'client_type': Client.ClientType.TENANT}
    )
    month_year = models.DateField(
        help_text="Month and year this management corresponds to"
    )
    rent_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    commission_amount = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    rent_status = models.CharField(
        max_length=10,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )
    transfer_status = models.CharField(
        max_length=10,
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING
    )
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def transfer_amount(self):
        """Calculate amount to transfer to owner"""
        return self.rent_amount - self.commission_amount

    class Meta:
        unique_together = ['rental_property', 'month_year']
        ordering = ['-month_year']

    @classmethod
    def create_next_month(cls, previous_management):
        """Create a new management entry for the next month based on previous one"""
        next_month = (previous_management.month_year.replace(day=1) + 
                     timezone.timedelta(days=32)).replace(day=1)
        
        return cls.objects.create(
            rental_property=previous_management.rental_property,
            owner=previous_management.owner,
            tenant=previous_management.tenant,
            month_year=next_month,
            rent_amount=previous_management.rent_amount,
            commission_amount=previous_management.commission_amount
        )