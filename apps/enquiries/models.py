from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from apps.cars.models import Car

class Enquiry(models.Model):
    """
    Direct vehicle inquiry or general dealership contact submission.
    """
    STATUS_CHOICES = [
        ('new', 'New / Unread'),
        ('contacted', 'Contacted Customer'),
        ('resolved', 'Resolved / Closed'),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries',
        help_text="Optional vehicle associated with inquiry"
    )
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Enquiry"
        verbose_name_plural = "Enquiries"

    def __str__(self):
        car_info = f" re: {self.car}" if self.car else " (General)"
        return f"Inquiry from {self.name}{car_info}"

    def notify_admin(self):
        """Dispatches an email notification to the dealership administrator."""
        subject = f"🔔 [Samko Cars] New Enquiry from {self.name}"
        body = (
            f"You received a new enquiry on Samko Cars:\n\n"
            f"Customer: {self.name}\n"
            f"Phone: {self.phone}\n"
            f"Email: {self.email}\n"
            f"Vehicle: {self.car if self.car else 'General Enquiry'}\n\n"
            f"Message:\n{self.message}\n\n"
            f"Submitted at: {self.created_at.strftime('%Y-%m-%d %H:%M')}\n"
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
