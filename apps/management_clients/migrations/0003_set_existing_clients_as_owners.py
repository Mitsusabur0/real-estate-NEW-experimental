# apps/management_clients/migrations/XXXX_set_existing_clients_as_owners.py

from django.db import migrations

def set_owners(apps, schema_editor):
    Client = apps.get_model('management_clients', 'Client')
    Client.objects.all().update(client_type='OWNER')

def reverse_owners(apps, schema_editor):
    pass  # No need to reverse as default is already 'OWNER'

class Migration(migrations.Migration):
    dependencies = [
        ('management_clients', '0002_add_client_type'),  # Reference previous migration
    ]

    operations = [
        migrations.RunPython(set_owners, reverse_owners),
    ]