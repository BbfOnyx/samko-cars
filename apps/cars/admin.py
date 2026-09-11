from django.contrib import admin
from .models import Car, CarImage, Feature

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'mileage', 'condition', 'transmission', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'condition', 'make', 'body_type', 'is_featured')
    search_fields = ('make', 'model', 'vin', 'description')
    prepopulated_fields = {'slug': ('year', 'make', 'model')}
    inlines = [CarImageInline]

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_name')
    search_fields = ('name',)

@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car', 'is_cover', 'order', 'caption')
    list_editable = ('is_cover', 'order')
