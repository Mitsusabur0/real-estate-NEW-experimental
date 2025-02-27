from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import RentalAgreement, MonthlyRental


@receiver(post_save, sender=RentalAgreement)
def create_initial_monthly_rental(sender, instance, created, **kwargs):
    """Create initial monthly rental record when a new rental agreement is created."""
    if created and instance.is_active:
        # Determine current month and year
        today = timezone.now().date()
        current_year = today.year
        current_month = today.month
        
        # Check if agreement start date is in the future
        start_date = instance.start_date
        if start_date.year > current_year or (start_date.year == current_year and start_date.month > current_month):
            # Use start date month/year instead
            current_year = start_date.year
            current_month = start_date.month
        
        # Check if monthly rental record already exists
        existing = MonthlyRental.objects.filter(
            rental_agreement=instance,
            period_year=current_year,
            period_month=current_month
        ).exists()
        
        if not existing:
            # Create monthly rental record
            MonthlyRental.objects.create(
                rental_agreement=instance,
                period_year=current_year,
                period_month=current_month,
                transfer_amount=instance.calculate_transfer_amount()
            )


@receiver(pre_save, sender=MonthlyRental)
def validate_transfer_status(sender, instance, **kwargs):
    """Ensure transfer status is only set to completed if rent status is paid."""
    if instance.transfer_status == 'completed' and instance.rent_status != 'paid':
        # Force rent status to paid if transfer is completed
        instance.rent_status = 'paid'
        if not instance.payment_date:
            instance.payment_date = timezone.now().date()