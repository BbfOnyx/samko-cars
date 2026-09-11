from django.contrib import admin
from .models import PurchaseRequest

@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'customer_phone', 'customer_email', 'car', 'price_at_request', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'customer_email', 'car__make', 'car__model')
