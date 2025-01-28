# apps/management_clients/migrations/XXXX_add_client_type.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('management_clients', '0001_initial'),  # Replace with actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='client_type',
            field=models.CharField(
                choices=[('OWNER', 'Property Owner'), ('TENANT', 'Tenant')],
                default='OWNER',
                help_text='Type of client (property owner or tenant)',
                max_length=6
            ),
        ),
        migrations.AddIndex(
            model_name='client',
            index=models.Index(fields=['client_type'], name='client_type_idx'),
        ),
        migrations.AlterModelOptions(
            name='client',
            options={
                'ordering': ['name'],
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients'
            },
        ),
    ]

