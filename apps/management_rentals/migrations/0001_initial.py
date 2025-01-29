# Generated by Django 5.1.4 on 2025-01-29 17:01

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('management_clients', '0004_rename_client_type_idx_management__client__95b1f0_idx_and_more'),
        ('management_properties', '0002_property_current_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='RentalManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month_year', models.DateField(help_text='Month and year this management corresponds to')),
                ('rent_amount', models.DecimalField(decimal_places=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('commission_amount', models.DecimalField(decimal_places=0, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('rent_status', models.CharField(choices=[('PENDING', 'Pendiente'), ('PAID', 'Pagado')], default='PENDING', max_length=10)),
                ('transfer_status', models.CharField(choices=[('PENDING', 'Pendiente'), ('ON_HOLD', 'En Espera'), ('PAID', 'Pagado')], default='PENDING', max_length=10)),
                ('comments', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(limit_choices_to={'client_type': 'OWNER'}, on_delete=django.db.models.deletion.PROTECT, related_name='properties_rented_out', to='management_clients.client')),
                ('rental_property', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rental_managements', to='management_properties.property')),
                ('tenant', models.ForeignKey(limit_choices_to={'client_type': 'TENANT'}, on_delete=django.db.models.deletion.PROTECT, related_name='rented_properties', to='management_clients.client')),
            ],
            options={
                'ordering': ['-month_year'],
                'unique_together': {('rental_property', 'month_year')},
            },
        ),
    ]
