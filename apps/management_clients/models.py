from django.db import models
from django.core.validators import EmailValidator
from apps.management_properties.models import Property

class Client(models.Model):
    """
    Represents a client in the real estate system.
    Can be either a property owner or a tenant.
    """
    class ClientType(models.TextChoices):
        OWNER = 'OWNER', 'Property Owner'
        TENANT = 'TENANT', 'Tenant'

    name = models.CharField(
        max_length=200,
        help_text="Full name of the client"
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
        help_text="Indicates if the client is currently active in the system"
    )
    client_type = models.CharField(
        max_length=6,
        choices=ClientType.choices,
        default=ClientType.OWNER,
        help_text="Type of client (property owner or tenant)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        display_type = 'dueño' if self.client_type == self.ClientType.OWNER else 'arrendatario'
        return f"{self.name} ({display_type})"

    class Meta:
        ordering = ['name']
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        # Add index for client_type for better query performance
        indexes = [
            models.Index(fields=['client_type']),
        ]

    @property
    def is_owner(self):
        """Convenience method to check if client is an owner"""
        return self.client_type == self.ClientType.OWNER

    @property
    def is_tenant(self):
        """Convenience method to check if client is a tenant"""
        return self.client_type == self.ClientType.TENANT


class PropertyOwnership(models.Model):
    """
    Historical record of property ownership.
    Tracks when properties change hands between owners.
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
        help_text="The owner of the property",
        limit_choices_to={'client_type': Client.ClientType.OWNER}  # Only allow owners
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

    def clean(self):
        """Ensure only owners can be assigned to PropertyOwnership"""
        if self.owner and not self.owner.is_owner:
            raise models.ValidationError({
                'owner': 'Only property owners can be assigned to property ownerships.'
            })