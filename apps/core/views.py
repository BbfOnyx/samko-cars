from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Count
from apps.cars.models import Car
from apps.core.models import SiteSetting, Testimonial

def index_view(request):
    """
    Homepage view for Samko Cars.
    Displays automotive hero search, featured cars, latest arrivals,
    popular Nigerian brands with counts, why choose us, and testimonials.
    """
    featured_cars = Car.objects.filter(
        is_active=True, is_featured=True
    ).prefetch_related('images', 'features')[:6]

    latest_cars = Car.objects.filter(
        is_active=True
    ).prefetch_related('images', 'features').order_by('-created_at')[:8]

    # Popular vehicle brands in Nigeria
    popular_brand_names = [
        'Toyota', 'Lexus', 'Mercedes-Benz', 'BMW', 'Honda',
        'Hyundai', 'Kia', 'Ford', 'Land Rover', 'Peugeot'
    ]
    popular_brands = []
    for brand in popular_brand_names:
        count = Car.objects.filter(is_active=True, make__iexact=brand).count()
        popular_brands.append({
            'name': brand,
            'count': count
        })

    testimonials = Testimonial.objects.filter(is_active=True)[:6]

    context = {
        'featured_cars': featured_cars,
        'latest_cars': latest_cars,
        'popular_brands': popular_brands,
        'testimonials': testimonials,
    }
    return render(request, 'website/index.html', context)


def about_view(request):
    """About Samko Cars dealership page."""
    return render(request, 'website/about.html')


def contact_view(request):
    """Contact page with live dealership details and inquiry submission."""
    return render(request, 'website/contact.html')


def robots_txt_view(request):
    """SEO robots.txt file."""
    lines = [
        "User-agent: *",
        "Disallow: /admin-panel/",
        "Disallow: /admin/",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml_view(request):
    """XML sitemap for Google and search engine indexing."""
    cars = Car.objects.filter(is_active=True)
    xml_items = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{request.build_absolute_uri("/")}</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{request.build_absolute_uri("/cars/")}</loc><changefreq>daily</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{request.build_absolute_uri("/about/")}</loc><changefreq>weekly</changefreq><priority>0.6</priority></url>',
        f'  <url><loc>{request.build_absolute_uri("/contact/")}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>',
    ]
    for car in cars:
        url = request.build_absolute_uri(car.get_absolute_url())
        xml_items.append(f'  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')
    xml_items.append('</urlset>')
    return HttpResponse("\n".join(xml_items), content_type="application/xml")
