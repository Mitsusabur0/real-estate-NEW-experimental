from django.db import models
from django.core.validators import EmailValidator
from apps.management_properties.models import Property

class Client(models.Model):
    """
    Represents a property owner (client) in the real estate system.
    Stores basic contact information.
    """
    name = models.CharField(
        max_length=200,
        help_text="Full name of the property owner"
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Primary contact email"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Contact phone number"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the client currently has any properties listed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        ordering = ['name']
        verbose_name = "Property Owner"
        verbose_name_plural = "Property Owners"


class PropertyOwnership(models.Model):
    """
    Historical record of property ownership.
    Tracks when properties change hands between clients.
    """
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='ownership_history',
        help_text="The property being owned"
    )
    owner = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='property_history',
        help_text="The owner of the property"
    )
    start_date = models.DateField(
        help_text="Date when ownership began"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when ownership ended (if applicable)"
    )

    def __str__(self):
        return f"{self.property} owned by {self.owner} ({self.start_date})"

    class Meta:
        verbose_name = "Property Ownership"
        verbose_name_plural = "Property Ownerships"
        ordering = ['-start_date'] 