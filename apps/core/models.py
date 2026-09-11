from django.db import models

class SiteSetting(models.Model):
    """
    Singleton model to manage general dealership settings,
    contact info, WhatsApp numbers, homepage copy, and about details.
    """
    site_name = models.CharField(max_length=100, default="Samko Cars")
    tagline = models.CharField(max_length=255, default="Nigeria's Premier Verified Automobile Marketplace")
    phone = models.CharField(max_length=50, default="+234 802 345 6789")
    whatsapp_number = models.CharField(
        max_length=30,
        default="2348023456789",
        help_text="Format with country code without plus sign (e.g. 2348023456789)"
    )
    whatsapp_default_message = models.TextField(
        default="Hello Samko Cars, I am interested in inquiring about vehicles on your website."
    )
    email = models.EmailField(default="sales@samkocars.com")
    address = models.CharField(max_length=255, default="Plot 14, Admiralty Way, Lekki Phase 1, Lagos, Nigeria")
    city = models.CharField(max_length=100, default="Lagos, Nigeria")
    opening_hours = models.CharField(
        max_length=255,
        default="Mon - Fri: 8:00 AM - 6:00 PM | Sat: 9:00 AM - 5:00 PM | Sun: Closed"
    )
    
    # Homepage CMS
    hero_title = models.CharField(max_length=200, default="Find Your Next Dream Car in Nigeria")
    hero_subtitle = models.TextField(
        default="Explore our carefully curated selection of inspected Tokunbo, clean Nigerian-used, and brand-new cars with transparent pricing in Naira."
    )
    
    # About Us CMS
    about_story = models.TextField(
        default=(
            "Established with a vision for transparency, Samko Cars has evolved into one of Nigeria's "
            "most trusted automobile dealerships. We bridge the gap between discerning car buyers and "
            "premium, verified vehicles across Lagos, Abuja, and all 36 states."
        )
    )
    mission = models.TextField(
        default="To deliver unmatched automotive satisfaction through strict 150-point vehicle inspections, upfront pricing, and frictionless dealership support."
    )
    vision = models.TextField(
        default="To be West Africa's leading benchmark in certified pre-owned and luxury automobile sales."
    )
    quality_assurance = models.TextField(
        default="Every single vehicle on our lot undergoes an extensive computer diagnostic scan, flood damage inspection, chassis alignment audit, and customs clearance authentication."
    )
    
    # Footer CMS
    footer_text = models.TextField(
        default="Samko Cars is a licensed dealership registered with the Corporate Affairs Commission (CAC) of Nigeria. Delivering automotive excellence and customer integrity."
    )

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class SocialMedia(models.Model):
    """
    Dynamic social media links manageable directly through the admin panel.
    """
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('tiktok', 'TikTok'),
        ('twitter', 'X (Twitter)'),
        ('youtube', 'YouTube'),
        ('linkedin', 'LinkedIn'),
        ('whatsapp', 'WhatsApp Channel'),
        ('other', 'Other Platform'),
    ]
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='instagram')
    platform_name = models.CharField(max_length=100, blank=True, help_text="Custom name if 'Other' selected")
    url = models.URLField()
    icon_class = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional icon identifier or SVG code"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'platform']
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"

    def __str__(self):
        return self.platform_name or self.get_platform_display()


class Testimonial(models.Model):
    """
    Customer reviews and testimonials displayed on the homepage.
    """
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, default="Lekki, Lagos")
    vehicle_purchased = models.CharField(max_length=150, default="2021 Lexus RX 350")
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.vehicle_purchased}"
