from .models import SiteSetting, SocialMedia

def site_context(request):
    """
    Context processor to make dealership settings and active social media links
    available across all templates globally.
    Also provides pending enquiry and purchase badges for staff members.
    """
    try:
        settings = SiteSetting.get_settings()
        socials = SocialMedia.objects.filter(is_active=True).order_by('order')
    except Exception:
        settings = None
        socials = []

    pending_enquiries_count = 0
    pending_purchases_count = 0

    if request.user.is_authenticated and request.user.is_staff:
        try:
            from apps.enquiries.models import Enquiry
            from apps.purchases.models import PurchaseRequest
            pending_enquiries_count = Enquiry.objects.filter(status='new').count()
            pending_purchases_count = PurchaseRequest.objects.filter(status='new').count()
        except Exception:
            pass

    return {
        'site_settings': settings,
        'social_links': socials,
        'admin_unread_count': pending_enquiries_count + pending_purchases_count,
        'pending_enquiries_count': pending_enquiries_count,
        'pending_purchases_count': pending_purchases_count,
    }
