from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.management_properties.models import Property
from apps.management_clients.models import Client


class RentalAgreement(models.Model):
    """
    Model representing a rental agreement between an owner, a tenant, and the agent.
    
    Args:
        property: The property being rented
        owner: The client who owns the property
        tenant: The client who is renting the property
        rent_amount: The monthly rent amount
        commission_amount: The agent's commission for managing the property
        start_date: When the rental agreement begins
        end_date: When the rental agreement ends (optional)
        is_active: Whether the rental agreement is currently active
        created_at: When the record was created
        updated_at: When the record was last updated
    """
    property = models.ForeignKey(
        Property, 
        on_delete=models.PROTECT,
        related_name='rental_agreements',
        help_text="The property being rented"
    )
    owner = models.ForeignKey(
        Client, 
        on_delete=models.PROTECT,
        related_name='properties_rented_out',
        help_text="The client who owns the property"
    )
    tenant = models.ForeignKey(
        Client, 
        on_delete=models.PROTECT,
        related_name='properties_rented',
        help_text="The client who is renting the property"
    )
    rent_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        help_text="Monthly rent amount"
    )
    commission_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        help_text="Agent's commission amount"
    )
    start_date = models.DateField(help_text="When the rental agreement begins")
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text="When the rental agreement ends (if applicable)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rental agreement is currently active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_active', '-start_date']
        verbose_name = "Rental Agreement"
        verbose_name_plural = "Rental Agreements"
    
    def __str__(self):
        return f"{self.property} - {self.tenant} - {self.start_date}"
    
    def clean(self):
        """Validate the rental agreement data."""
        # Ensure commission is less than rent
        if self.commission_amount >= self.rent_amount:
            raise ValidationError({
                'commission_amount': 'Commission cannot be greater than or equal to rent amount'
            })
        
        # Ensure end_date is after start_date if provided
        if self.end_date and self.end_date <= self.start_date:
            raise ValidationError({
                'end_date': 'End date must be after start date'
            })
        
        # Ensure owner is actually the owner of the property
        if self.property.current_owner != self.owner:
            raise ValidationError({
                'owner': 'Selected client is not the current owner of this property'
            })
        
        # Ensure owner and tenant are different people
        if self.owner == self.tenant:
            raise ValidationError({
                'tenant': 'Owner and tenant cannot be the same person'
            })
    
    def calculate_transfer_amount(self):
        """Calculate the amount to transfer to the owner (rent minus commission)."""
        return self.rent_amount - self.commission_amount
    
    def is_termination_date_valid(self, termination_date):
        """Check if a termination date is valid for this agreement."""
        today = timezone.now().date()
        
        if termination_date < self.start_date:
            return False
        
        if termination_date < today:
            return False
            
        if self.end_date and termination_date > self.end_date:
            return False
            
        return True


class MonthlyRental(models.Model):
    """
    Model representing a monthly rental record for a specific rental agreement.
    
    Args:
        rental_agreement: The associated rental agreement
        period_year: The year of this rental period
        period_month: The month of this rental period (1-12)
        rent_status: Current status of the rent payment
        payment_date: When the rent was paid (if applicable)
        transfer_amount: Amount to be transferred to owner
        transfer_status: Current status of the transfer to owner
        transfer_date: When the transfer to owner was completed (if applicable)
        notes: Additional notes about this monthly rental
        created_at: When the record was created
        updated_at: When the record was last updated
    """
    
    # Status choices
    PENDING = 'pending'
    PAID = 'paid'
    LATE = 'late'
    UNPAID = 'unpaid'
    
    RENT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PAID, 'Paid'),
        (LATE, 'Late'),
        (UNPAID, 'Unpaid'),
    ]
    
    TRANSFER_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        ('completed', 'Completed'),
    ]
    
    rental_agreement = models.ForeignKey(
        RentalAgreement, 
        on_delete=models.PROTECT,
        related_name='monthly_rentals',
        help_text="The associated rental agreement"
    )
    period_year = models.PositiveSmallIntegerField(help_text="Year of this rental period")
    period_month = models.PositiveSmallIntegerField(
        help_text="Month of this rental period (1-12)",
        choices=[(i, i) for i in range(1, 13)]
    )
    rent_status = models.CharField(
        max_length=10,
        choices=RENT_STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of the rent payment"
    )
    payment_date = models.DateField(
        null=True, 
        blank=True,
        help_text="When the rent was paid"
    )
    transfer_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=0,
        help_text="Amount to be transferred to owner"
    )
    transfer_status = models.CharField(
        max_length=10,
        choices=TRANSFER_STATUS_CHOICES,
        default=PENDING,
        help_text="Current status of the transfer to owner"
    )
    transfer_date = models.DateField(
        null=True, 
        blank=True,
        help_text="When the transfer to owner was completed"
    )
    notes = models.TextField(blank=True, help_text="Additional notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-period_year', '-period_month']
        verbose_name = "Monthly Rental"
        verbose_name_plural = "Monthly Rentals"
        # Ensure uniqueness for rental agreement + period year + period month
        unique_together = ['rental_agreement', 'period_year', 'period_month']
    
    def __str__(self):
        return f"{self.rental_agreement.property} - {self.period_month}/{self.period_year}"
    
    def clean(self):
        """Validate the monthly rental data."""
        # Ensure payment_date is provided if rent_status is PAID or LATE
        if self.rent_status in [self.PAID, self.LATE] and not self.payment_date:
            raise ValidationError({
                'payment_date': 'Payment date is required when rent is marked as paid or late'
            })
        
        # Ensure transfer_date is provided if transfer_status is completed
        if self.transfer_status == 'completed' and not self.transfer_date:
            raise ValidationError({
                'transfer_date': 'Transfer date is required when transfer is marked as completed'
            })
        
        # Ensure period is valid (within rental agreement dates)
        start_date = self.rental_agreement.start_date
        end_date = self.rental_agreement.end_date
        
        # Check if rental period is before start date
        if (self.period_year < start_date.year or 
            (self.period_year == start_date.year and self.period_month < start_date.month)):
            raise ValidationError("Rental period cannot be before the agreement start date")
        
        # Check if rental period is after end date (if end_date exists)
        if end_date and (self.period_year > end_date.year or 
            (self.period_year == end_date.year and self.period_month > end_date.month)):
            raise ValidationError("Rental period cannot be after the agreement end date")
    
    def save(self, *args, **kwargs):
        """Override save to set transfer_amount if not provided."""
        if not self.transfer_amount:
            self.transfer_amount = self.rental_agreement.calculate_transfer_amount()
        super().save(*args, **kwargs)
    
    @classmethod
    def initialize_month(cls, year, month):
        """
        Initialize monthly rental records for all active rental agreements for a specific month.
        
        Args:
            year: The year to initialize
            month: The month to initialize (1-12)
            
        Returns:
            tuple: (created_count, existing_count)
        """
        from django.db.models import Q
        
        created_count = 0
        existing_count = 0
        
        # Get all active rental agreements that are valid for the given month/year
        active_agreements = RentalAgreement.objects.filter(
            is_active=True,
            start_date__lte=timezone.datetime(year, month, 1).date(),
        ).filter(
            Q(end_date__isnull=True) | 
            Q(end_date__gte=timezone.datetime(year, month, 1).date())
        )
        
        # Create monthly rental records for each active agreement
        for agreement in active_agreements:
            # Check if a record already exists for this agreement in this period
            existing = cls.objects.filter(
                rental_agreement=agreement,
                period_year=year,
                period_month=month
            ).exists()
            
            if existing:
                existing_count += 1
                continue
                
            # Create new monthly rental record
            cls.objects.create(
                rental_agreement=agreement,
                period_year=year,
                period_month=month,
                transfer_amount=agreement.calculate_transfer_amount()
            )
            created_count += 1
            
        return created_count, existing_count