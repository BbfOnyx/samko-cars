from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Car, Feature

def car_list_view(request):
    """
    Marketplace listing page with comprehensive backend filtering, sorting,
    and fast pagination.
    """
    queryset = Car.objects.filter(is_active=True).prefetch_related('images', 'features')
    
    # 1. Search Query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(make__icontains=q) |
            Q(model__icontains=q) |
            Q(description__icontains=q) |
            Q(location__icontains=q) |
            Q(vin__icontains=q)
        )

    # 2. Make & Model
    make = request.GET.get('make', '').strip()
    if make:
        queryset = queryset.filter(make__iexact=make)
        
    model = request.GET.get('model', '').strip()
    if model:
        queryset = queryset.filter(model__icontains=model)

    # 3. Price Filter
    min_price = request.GET.get('min_price', '').strip()
    if min_price:
        try:
            queryset = queryset.filter(price__gte=Decimal(min_price))
        except (ValueError, ArithmeticError):
            pass

    max_price = request.GET.get('max_price', '').strip()
    if max_price:
        try:
            queryset = queryset.filter(price__lte=Decimal(max_price))
        except (ValueError, ArithmeticError):
            pass

    # 4. Year Filter
    year_min = request.GET.get('year_min', '').strip()
    if year_min:
        try:
            queryset = queryset.filter(year__gte=int(year_min))
        except ValueError:
            pass

    year_max = request.GET.get('year_max', '').strip()
    if year_max:
        try:
            queryset = queryset.filter(year__lte=int(year_max))
        except ValueError:
            pass

    # 5. Mileage
    max_mileage = request.GET.get('max_mileage', '').strip()
    if max_mileage:
        try:
            queryset = queryset.filter(mileage__lte=int(max_mileage))
        except ValueError:
            pass

    # 6. Attributes (Condition, Transmission, Fuel, Body, Location, Status)
    condition = request.GET.get('condition', '').strip()
    if condition:
        queryset = queryset.filter(condition=condition)

    transmission = request.GET.get('transmission', '').strip()
    if transmission:
        queryset = queryset.filter(transmission=transmission)

    fuel_type = request.GET.get('fuel_type', '').strip()
    if fuel_type:
        queryset = queryset.filter(fuel_type=fuel_type)

    body_type = request.GET.get('body_type', '').strip()
    if body_type:
        queryset = queryset.filter(body_type=body_type)

    location = request.GET.get('location', '').strip()
    if location:
        queryset = queryset.filter(location__icontains=location)

    status = request.GET.get('status', '').strip()
    if status:
        queryset = queryset.filter(status=status)

    # 7. Sorting
    sort_by = request.GET.get('sort', 'newest').strip()
    if sort_by == 'price_low':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort_by == 'mileage_low':
        queryset = queryset.order_by('mileage')
    elif sort_by == 'year_new':
        queryset = queryset.order_by('-year')
    elif sort_by == 'oldest':
        queryset = queryset.order_by('created_at')
    else:  # newest
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Total match count
    total_matches = queryset.count()

    # 8. Pagination (12 cars per page for responsive grid)
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page', 1)
    try:
        cars = paginator.page(page_number)
    except PageNotAnInteger:
        cars = paginator.page(1)
    except EmptyPage:
        cars = paginator.page(paginator.num_pages)

    # Query params string for pagination links preserving active filters
    query_params = request.GET.copy()
    if 'page' in query_params:
        del query_params['page']
    filter_querystring = query_params.urlencode()

    # Collect available filter options for dropdowns
    all_active = Car.objects.filter(is_active=True)
    available_makes = all_active.values_list('make', flat=True).distinct().order_by('make')
    available_body_types = Car.BODY_CHOICES
    available_conditions = Car.CONDITION_CHOICES
    available_transmissions = Car.TRANSMISSION_CHOICES
    available_fuel_types = Car.FUEL_CHOICES

    context = {
        'cars': cars,
        'total_matches': total_matches,
        'filter_querystring': filter_querystring,
        'sort_by': sort_by,
        'available_makes': available_makes,
        'available_body_types': available_body_types,
        'available_conditions': available_conditions,
        'available_transmissions': available_transmissions,
        'available_fuel_types': available_fuel_types,
        # Active filter values for form controls
        'selected_make': make,
        'selected_model': model,
        'selected_min_price': min_price,
        'selected_max_price': max_price,
        'selected_year_min': year_min,
        'selected_year_max': year_max,
        'selected_condition': condition,
        'selected_transmission': transmission,
        'selected_fuel_type': fuel_type,
        'selected_body_type': body_type,
        'selected_location': location,
        'selected_status': status,
        'search_query': q,
    }
    return render(request, 'website/cars.html', context)


def car_detail_view(request, pk=None, slug=None):
    """
    Detailed vehicle presentation page with image gallery, specs,
    WhatsApp CTA, enquiry form, and purchase/inspection request modal.
    """
    if pk:
        car = get_object_or_404(Car.objects.prefetch_related('images', 'features'), pk=pk, is_active=True)
    else:
        car = get_object_or_404(Car.objects.prefetch_related('images', 'features'), slug=slug, is_active=True)

    # Related cars (same make or body type, excluding current car)
    related_cars = Car.objects.filter(
        is_active=True
    ).exclude(pk=car.pk).filter(
        Q(make=car.make) | Q(body_type=car.body_type)
    ).order_by('-is_featured', '-created_at')[:4]

    whatsapp_link = car.get_whatsapp_url(request)

    context = {
        'car': car,
        'images': car.images.all(),
        'features': car.features.all(),
        'related_cars': related_cars,
        'whatsapp_link': whatsapp_link,
    }
    return render(request, 'website/car_detail.html', context)
