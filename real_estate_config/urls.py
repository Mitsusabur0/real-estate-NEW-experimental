from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('properties/', include('apps.management_properties.urls')),
    path('clients/', include('apps.management_clients.urls')),
    path('rentals/', include('apps.management_rentals.urls', namespace='rentals')),
]