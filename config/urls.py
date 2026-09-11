"""
URL configuration for Samko Cars project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Custom Staff & Dealership Executive Dashboard
    path('admin-panel/', include('apps.admin_panel.urls', namespace='admin_panel')),

    # Django built-in admin (secondary fallback)
    path('admin/', admin.site.urls),

    # Customer Enquiries & Lead Submission
    path('enquiries/', include('apps.enquiries.urls', namespace='enquiries')),

    # Vehicle Purchase / Inspection Requests
    path('purchases/', include('apps.purchases.urls', namespace='purchases')),

    # Vehicles & Marketplace
    path('cars/', include('apps.cars.urls', namespace='cars')),

    # Core Dealership Website (Home, About, Contact, SEO)
    path('', include('apps.core.urls', namespace='core')),
]

# Serve committed/local media through Django only when explicitly enabled.
# User uploads need object storage for durable production persistence.
if settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
