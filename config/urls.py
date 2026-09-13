"""
URL configuration for Samko Cars project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

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

# Django's static() helper is deliberately DEBUG-only. Use an explicit route
# for local media so committed inventory files and local-storage uploads work
# in production when S3-compatible storage is not configured.
if not settings.S3_BUCKET_NAME:
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]
