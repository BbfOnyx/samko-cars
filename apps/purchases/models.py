from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from apps.cars.models import Car

class PurchaseRequest(models.Model):
    """
    Formal vehicle purchase/inspection reservation submitted by customers.
    """
    STATUS_CHOICES = [
        ('new', 'New Request'),
        ('contacted', 'Customer Contacted'),
        ('processing', 'Inspection Scheduled / Processing'),
        ('completed', 'Deal Completed / Sold'),
        ('cancelled', 'Request Cancelled'),
    ]

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='purchase_requests'
    )
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    price_at_request = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        help_text="Snapshot of the car price at the time request was made"
    )
    preferred_inspection_date = models.DateField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Purchase / Inspection Request"
        verbose_name_plural = "Purchase / Inspection Requests"

    def __str__(self):
        return f"Purchase Request: {self.customer_name} -> {self.car}"

    @property
    def formatted_price(self):
        try:
            return f"₦{int(self.price_at_request):,}"
        except (ValueError, TypeError):
            return f"₦{self.price_at_request}"

    def notify_admin(self):
        """Dispatches an email notification to the dealership administrator."""
        subject = f"🚗 [Samko Cars] NEW VEHICLE PURCHASE REQUEST for {self.car}"
        body = (
            f"URGENT: A customer has submitted a purchase/inspection request!\n\n"
            f"Vehicle: {self.car} ({self.formatted_price})\n"
            f"Customer Name: {self.customer_name}\n"
            f"Phone: {self.customer_phone}\n"
            f"Email: {self.customer_email}\n"
            f"Preferred Inspection Date: {self.preferred_inspection_date or 'Not specified'}\n"
            f"Additional Note: {self.message or 'None'}\n\n"
            f"Please log in to the admin panel to contact the buyer immediately:\n"
            f"/admin-panel/purchases/\n"
        )
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
