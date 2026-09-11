import urllib.parse
from decimal import Decimal
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from apps.core.models import SiteSetting

class Feature(models.Model):
    """Features and amenities of vehicles (e.g. Sunroof, Leather, Apple CarPlay)."""
    name = models.CharField(max_length=100, unique=True)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Optional icon class")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Car(models.Model):
    """
    Primary Vehicle model for Samko Cars inventory.
    """
    CONDITION_CHOICES = [
        ('foreign_used', 'Foreign Used (Tokunbo)'),
        ('nigerian_used', 'Nigerian Used'),
        ('brand_new', 'Brand New'),
    ]

    TRANSMISSION_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
        ('cvt', 'CVT'),
        ('other', 'Other'),
    ]

    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ]

    BODY_CHOICES = [
        ('suv', 'SUV'),
        ('sedan', 'Sedan'),
        ('coupe', 'Coupe'),
        ('pickup', 'Pickup Truck'),
        ('hatchback', 'Hatchback'),
        ('convertible', 'Convertible'),
        ('van', 'Van / Minivan'),
        ('wagon', 'Station Wagon'),
    ]

    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
    ]

    # Core details
    make = models.CharField(max_length=80, db_index=True)
    model = models.CharField(max_length=100, db_index=True)
    year = models.PositiveIntegerField(db_index=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, db_index=True, help_text="Price in Nigerian Naira (₦)")
    mileage = models.PositiveIntegerField(help_text="Mileage in Kilometers (km)", db_index=True)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default='foreign_used', db_index=True)
    transmission = models.CharField(max_length=30, choices=TRANSMISSION_CHOICES, default='automatic', db_index=True)
    fuel_type = models.CharField(max_length=30, choices=FUEL_CHOICES, default='petrol', db_index=True)
    body_type = models.CharField(max_length=30, choices=BODY_CHOICES, default='suv', db_index=True)
    engine = models.CharField(max_length=100, default="3.5L V6", help_text="e.g. 2.5L 4-Cylinder, 3.5L V6, 5.7L V8")
    exterior_color = models.CharField(max_length=60, default="Black")
    interior_color = models.CharField(max_length=60, default="Black Leather")
    location = models.CharField(max_length=120, default="Lekki, Lagos", db_index=True)
    
    # Marketplace status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    # Information & specs
    description = models.TextField(blank=True)
    vin = models.CharField(max_length=50, blank=True, verbose_name="VIN / Chassis No")
    features = models.ManyToManyField(Feature, blank=True, related_name='cars')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['make', 'model']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['price', 'year']),
        ]

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.year}-{self.make}-{self.model}")
            candidate = base_slug
            counter = 1
            while Car.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cars:detail', kwargs={'pk': self.pk})

    @property
    def formatted_price(self):
        """Returns price formatted with commas, e.g. ₦25,000,000"""
        try:
            return f"₦{int(self.price):,}"
        except (ValueError, TypeError):
            return f"₦{self.price}"

    @property
    def formatted_mileage(self):
        """Returns mileage formatted with commas, e.g. 45,000 km"""
        try:
            return f"{self.mileage:,} km"
        except (ValueError, TypeError):
            return f"{self.mileage} km"

    def get_cover_image(self):
        """Returns cover photo, or first photo, or placeholder"""
        cover = self.images.filter(is_cover=True).first()
        if not cover:
            cover = self.images.first()
        return cover

    def get_whatsapp_url(self, request=None):
        """Generates a dynamic click-to-chat WhatsApp link containing vehicle details"""
        settings = SiteSetting.get_settings()
        clean_number = "".join(filter(str.isdigit, str(settings.whatsapp_number)))
        if not clean_number:
            clean_number = "2348023456789"
        
        full_title = f"{self.year} {self.make} {self.model}"
        msg = f"Hello Samko Cars, I am interested in the {full_title} listed for {self.formatted_price} on your website."
        if request:
            msg += f" Details link: {request.build_absolute_uri(self.get_absolute_url())}"
        
        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{clean_number}?text={encoded_msg}"


class CarImage(models.Model):
    """Images associated with a car listing."""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/%Y/%m/')
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    caption = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_cover', 'order', 'id']

    def __str__(self):
        return f"Image for {self.car} ({'Cover' if self.is_cover else 'Gallery'})"
