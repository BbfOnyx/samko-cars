from django.contrib import admin
from .models import SiteSetting, SocialMedia, Testimonial

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'whatsapp_number', 'email', 'city')

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('platform', 'platform_name', 'url', 'is_active', 'order')
    list_editable = ('is_active', 'order')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'vehicle_purchased', 'rating', 'is_active')
    list_editable = ('is_active',)
