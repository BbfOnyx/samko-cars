from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .decorators import staff_required
from apps.cars.models import Car, CarImage, Feature
from apps.enquiries.models import Enquiry
from apps.purchases.models import PurchaseRequest
from apps.core.models import SiteSetting, SocialMedia, Testimonial

# ==================== AUTHENTICATION ====================

def admin_login_view(request):
    """
    Secure login page for Samko Cars Dealership Administrators.
    Staff and Superusers only.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_panel:dashboard')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)
        if user is None and '@' in username_or_email:
            # Attempt lookup by email
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                next_url = request.GET.get('next') or 'admin_panel:dashboard'
                return redirect(next_url)
            else:
                messages.error(request, "Access restricted. Your account does not have staff permissions.")
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'admin_panel/login.html')


def admin_logout_view(request):
    """Safely logs out the administrator."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('admin_panel:login')


# ==================== DASHBOARD HOME ====================

@staff_required
def dashboard_view(request):
    """
    Main executive dashboard with summary metric cards, alerts,
    and recent activity feeds.
    """
    total_vehicles = Car.objects.count()
    available_vehicles = Car.objects.filter(status='available').count()
    sold_vehicles = Car.objects.filter(status='sold').count()
    reserved_vehicles = Car.objects.filter(status='reserved').count()
    featured_vehicles = Car.objects.filter(is_featured=True).count()

    total_enquiries = Enquiry.objects.count()
    new_enquiries = Enquiry.objects.filter(status='new').count()

    total_purchases = PurchaseRequest.objects.count()
    new_purchases = PurchaseRequest.objects.filter(status='new').count()

    recent_cars = Car.objects.prefetch_related('images').order_by('-created_at')[:6]
    recent_enquiries = Enquiry.objects.order_by('-created_at')[:5]
    recent_purchases = PurchaseRequest.objects.prefetch_related('car').order_by('-created_at')[:5]

    context = {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'sold_vehicles': sold_vehicles,
        'reserved_vehicles': reserved_vehicles,
        'featured_vehicles': featured_vehicles,
        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,
        'total_purchases': total_purchases,
        'new_purchases': new_purchases,
        'recent_cars': recent_cars,
        'recent_enquiries': recent_enquiries,
        'recent_purchases': recent_purchases,
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ==================== CAR MANAGEMENT ====================

@staff_required
def car_list_view(request):
    """
    Admin table listing all vehicles with filter, search,
    and instant status modification actions.
    """
    cars = Car.objects.prefetch_related('images').all()

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        cars = cars.filter(
            Q(make__icontains=q) |
            Q(model__icontains=q) |
            Q(location__icontains=q) |
            Q(vin__icontains=q)
        )

    # Status filter
    status = request.GET.get('status', '').strip()
    if status:
        cars = cars.filter(status=status)

    # Make filter
    make = request.GET.get('make', '').strip()
    if make:
        cars = cars.filter(make__iexact=make)

    # Sorting
    cars = cars.order_by('-created_at')

    paginator = Paginator(cars, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    all_makes = Car.objects.values_list('make', flat=True).distinct().order_by('make')

    context = {
        'page_obj': page_obj,
        'all_makes': all_makes,
        'search_query': q,
        'selected_status': status,
        'selected_make': make,
    }
    return render(request, 'admin_panel/car_list.html', context)


@staff_required
def car_create_view(request):
    """
    Form to add a new car to inventory with multi-image upload
    and dynamic features selection.
    """
    all_features = Feature.objects.all().order_by('name')

    if request.method == 'POST':
        make = request.POST.get('make', '').strip()
        model = request.POST.get('model', '').strip()
        year = request.POST.get('year', '').strip()
        price = request.POST.get('price', '').strip().replace(',', '')
        mileage = request.POST.get('mileage', '').strip().replace(',', '')
        condition = request.POST.get('condition', 'foreign_used')
        transmission = request.POST.get('transmission', 'automatic')
        fuel_type = request.POST.get('fuel_type', 'petrol')
        body_type = request.POST.get('body_type', 'suv')
        engine = request.POST.get('engine', '').strip()
        exterior_color = request.POST.get('exterior_color', 'Black').strip()
        interior_color = request.POST.get('interior_color', 'Black').strip()
        location = request.POST.get('location', 'Lekki, Lagos').strip()
        status = request.POST.get('status', 'available')
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        description = request.POST.get('description', '').strip()
        vin = request.POST.get('vin', '').strip()

        if not make or not model or not year or not price:
            messages.error(request, "Please fill in all required fields (Make, Model, Year, Price).")
            return render(request, 'admin_panel/car_form.html', {
                'all_features': all_features,
                'action': 'Add'
            })

        try:
            car = Car.objects.create(
                make=make,
                model=model,
                year=int(year),
                price=Decimal(price),
                mileage=int(mileage) if mileage else 0,
                condition=condition,
                transmission=transmission,
                fuel_type=fuel_type,
                body_type=body_type,
                engine=engine or "3.5L V6",
                exterior_color=exterior_color,
                interior_color=interior_color,
                location=location,
                status=status,
                is_featured=is_featured,
                is_active=is_active,
                description=description,
                vin=vin,
            )

            # Features
            selected_features = request.POST.getlist('features')
            if selected_features:
                car.features.set(selected_features)

            # Custom features input
            custom_features_str = request.POST.get('custom_features', '').strip()
            if custom_features_str:
                for f_name in [x.strip() for x in custom_features_str.split(',') if x.strip()]:
                    f_obj, _ = Feature.objects.get_or_create(name=f_name)
                    car.features.add(f_obj)

            # Image uploads
            images = request.FILES.getlist('images')
            for index, img_file in enumerate(images):
                CarImage.objects.create(
                    car=car,
                    image=img_file,
                    is_cover=(index == 0),
                    order=index
                )

            messages.success(request, f"Vehicle '{car.year} {car.make} {car.model}' added successfully!")
            return redirect('admin_panel:car_list')

        except Exception as e:
            messages.error(request, f"Error saving vehicle: {str(e)}")

    context = {
        'all_features': all_features,
        'action': 'Add',
    }
    return render(request, 'admin_panel/car_form.html', context)


@staff_required
def car_edit_view(request, pk):
    """
    Form to edit an existing car. Allows changing price, mileage,
    status, features, and managing car photos.
    """
    car = get_object_or_404(Car.objects.prefetch_related('images', 'features'), pk=pk)
    all_features = Feature.objects.all().order_by('name')

    if request.method == 'POST':
        make = request.POST.get('make', '').strip()
        model = request.POST.get('model', '').strip()
        year = request.POST.get('year', '').strip()
        price = request.POST.get('price', '').strip().replace(',', '')
        mileage = request.POST.get('mileage', '').strip().replace(',', '')
        condition = request.POST.get('condition', car.condition)
        transmission = request.POST.get('transmission', car.transmission)
        fuel_type = request.POST.get('fuel_type', car.fuel_type)
        body_type = request.POST.get('body_type', car.body_type)
        engine = request.POST.get('engine', car.engine).strip()
        exterior_color = request.POST.get('exterior_color', car.exterior_color).strip()
        interior_color = request.POST.get('interior_color', car.interior_color).strip()
        location = request.POST.get('location', car.location).strip()
        status = request.POST.get('status', car.status)
        is_featured = request.POST.get('is_featured') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        description = request.POST.get('description', '').strip()
        vin = request.POST.get('vin', '').strip()

        if not make or not model or not year or not price:
            messages.error(request, "Make, Model, Year, and Price cannot be empty.")
            return render(request, 'admin_panel/car_form.html', {
                'car': car,
                'all_features': all_features,
                'action': 'Edit'
            })

        try:
            car.make = make
            car.model = model
            car.year = int(year)
            car.price = Decimal(price)
            car.mileage = int(mileage) if mileage else 0
            car.condition = condition
            car.transmission = transmission
            car.fuel_type = fuel_type
            car.body_type = body_type
            car.engine = engine
            car.exterior_color = exterior_color
            car.interior_color = interior_color
            car.location = location
            car.status = status
            car.is_featured = is_featured
            car.is_active = is_active
            car.description = description
            car.vin = vin
            car.save()

            # Features
            selected_features = request.POST.getlist('features')
            car.features.set(selected_features)

            # Custom features input
            custom_features_str = request.POST.get('custom_features', '').strip()
            if custom_features_str:
                for f_name in [x.strip() for x in custom_features_str.split(',') if x.strip()]:
                    f_obj, _ = Feature.objects.get_or_create(name=f_name)
                    car.features.add(f_obj)

            # New Image uploads
            new_images = request.FILES.getlist('images')
            start_order = car.images.count()
            has_cover = car.images.filter(is_cover=True).exists()
            for index, img_file in enumerate(new_images):
                CarImage.objects.create(
                    car=car,
                    image=img_file,
                    is_cover=(not has_cover and index == 0),
                    order=start_order + index
                )

            messages.success(request, f"Vehicle '{car}' updated successfully!")
            return redirect('admin_panel:car_list')

        except Exception as e:
            messages.error(request, f"Error updating vehicle: {str(e)}")

    context = {
        'car': car,
        'all_features': all_features,
        'action': 'Edit',
    }
    return render(request, 'admin_panel/car_form.html', context)


@staff_required
def car_delete_view(request, pk):
    """Deletes a car with verification safeguard."""
    car = get_object_or_404(Car, pk=pk)

    if request.method == 'POST':
        title = str(car)
        car.delete()
        messages.success(request, f"Vehicle '{title}' has been deleted.")
        return redirect('admin_panel:car_list')

    return render(request, 'admin_panel/car_delete.html', {'car': car})


@staff_required
def car_toggle_status_view(request, pk, status):
    """Quickly switch status to available, reserved, or sold."""
    car = get_object_or_404(Car, pk=pk)
    if status in dict(Car.STATUS_CHOICES):
        car.status = status
        car.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"{car} marked as {car.get_status_display()}.")

    next_url = request.META.get('HTTP_REFERER') or 'admin_panel:car_list'
    return redirect(next_url)


@staff_required
def car_toggle_featured_view(request, pk):
    """Toggle featured status on/off."""
    car = get_object_or_404(Car, pk=pk)
    car.is_featured = not car.is_featured
    car.save(update_fields=['is_featured', 'updated_at'])
    status_text = "Featured on homepage" if car.is_featured else "Removed from Featured"
    messages.success(request, f"{car} {status_text}.")
    next_url = request.META.get('HTTP_REFERER') or 'admin_panel:car_list'
    return redirect(next_url)


@staff_required
def car_image_delete_view(request, img_id):
    """Delete a specific image of a car."""
    image = get_object_or_404(CarImage, pk=img_id)
    car_id = image.car.id
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('admin_panel:car_edit', pk=car_id)


@staff_required
def car_image_set_cover_view(request, img_id):
    """Set a specific image as the cover photo."""
    image = get_object_or_404(CarImage, pk=img_id)
    car = image.car
    car.images.update(is_cover=False)
    image.is_cover = True
    image.save(update_fields=['is_cover'])
    messages.success(request, "Cover photo updated.")
    return redirect('admin_panel:car_edit', pk=car.id)


# ==================== ENQUIRIES ====================

@staff_required
def enquiries_view(request):
    """Manage customer enquiries with status filtering."""
    enquiries = Enquiry.objects.prefetch_related('car').all()

    status = request.GET.get('status', '').strip()
    if status:
        enquiries = enquiries.filter(status=status)

    paginator = Paginator(enquiries, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_status': status,
    }
    return render(request, 'admin_panel/enquiries.html', context)


@staff_required
def enquiry_update_status_view(request, pk, status):
    """Updates enquiry status (new, contacted, resolved)."""
    enquiry = get_object_or_404(Enquiry, pk=pk)
    if status in dict(Enquiry.STATUS_CHOICES):
        enquiry.status = status
        enquiry.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Enquiry #{enquiry.id} marked as {enquiry.get_status_display()}.")
    return redirect('admin_panel:enquiries')


@staff_required
def enquiry_delete_view(request, pk):
    """Delete an enquiry."""
    enquiry = get_object_or_404(Enquiry, pk=pk)
    enquiry.delete()
    messages.success(request, "Enquiry deleted.")
    return redirect('admin_panel:enquiries')


# ==================== PURCHASES ====================

@staff_required
def purchases_view(request):
    """Manage customer purchase and inspection requests."""
    purchases = PurchaseRequest.objects.prefetch_related('car').all()

    status = request.GET.get('status', '').strip()
    if status:
        purchases = purchases.filter(status=status)

    paginator = Paginator(purchases, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_status': status,
    }
    return render(request, 'admin_panel/purchases.html', context)


@staff_required
def purchase_update_status_view(request, pk, status):
    """Updates purchase request workflow status."""
    purchase = get_object_or_404(PurchaseRequest, pk=pk)
    if status in dict(PurchaseRequest.STATUS_CHOICES):
        purchase.status = status
        purchase.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Purchase request #{purchase.id} updated to {purchase.get_status_display()}.")
    return redirect('admin_panel:purchases')


# ==================== SITE SETTINGS ====================

@staff_required
def site_settings_view(request):
    """
    Manage dealership information, WhatsApp numbers, opening hours,
    homepage hero copy, about story, and footer text without touching source code.
    """
    settings_obj = SiteSetting.get_settings()

    if request.method == 'POST':
        settings_obj.site_name = request.POST.get('site_name', 'Samko Cars').strip()
        settings_obj.tagline = request.POST.get('tagline', '').strip()
        settings_obj.phone = request.POST.get('phone', '').strip()
        settings_obj.whatsapp_number = request.POST.get('whatsapp_number', '').strip()
        settings_obj.whatsapp_default_message = request.POST.get('whatsapp_default_message', '').strip()
        settings_obj.email = request.POST.get('email', '').strip()
        settings_obj.address = request.POST.get('address', '').strip()
        settings_obj.city = request.POST.get('city', '').strip()
        settings_obj.opening_hours = request.POST.get('opening_hours', '').strip()
        settings_obj.hero_title = request.POST.get('hero_title', '').strip()
        settings_obj.hero_subtitle = request.POST.get('hero_subtitle', '').strip()
        settings_obj.about_story = request.POST.get('about_story', '').strip()
        settings_obj.mission = request.POST.get('mission', '').strip()
        settings_obj.vision = request.POST.get('vision', '').strip()
        settings_obj.quality_assurance = request.POST.get('quality_assurance', '').strip()
        settings_obj.footer_text = request.POST.get('footer_text', '').strip()
        settings_obj.save()

        messages.success(request, "Dealership settings updated successfully! Public website is immediately updated.")
        return redirect('admin_panel:settings')

    return render(request, 'admin_panel/settings.html', {'settings': settings_obj})


# ==================== SOCIAL MEDIA ====================

@staff_required
def social_media_view(request):
    """Manage dynamic social media channels."""
    socials = SocialMedia.objects.all().order_by('order')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            platform = request.POST.get('platform', 'instagram')
            platform_name = request.POST.get('platform_name', '').strip()
            url = request.POST.get('url', '').strip()
            order = request.POST.get('order', '0')
            if url:
                SocialMedia.objects.create(
                    platform=platform,
                    platform_name=platform_name,
                    url=url,
                    order=int(order) if order.isdigit() else 0,
                    is_active=True
                )
                messages.success(request, "Social media platform added.")
        return redirect('admin_panel:social')

    return render(request, 'admin_panel/social_media.html', {'socials': socials})


@staff_required
def social_delete_view(request, pk):
    """Delete a social media link."""
    social = get_object_or_404(SocialMedia, pk=pk)
    social.delete()
    messages.success(request, "Social media channel removed.")
    return redirect('admin_panel:social')


@staff_required
def social_toggle_view(request, pk):
    """Toggle active state of a social link."""
    social = get_object_or_404(SocialMedia, pk=pk)
    social.is_active = not social.is_active
    social.save(update_fields=['is_active'])
    messages.success(request, f"{social} {'activated' if social.is_active else 'deactivated'}.")
    return redirect('admin_panel:social')


# ==================== TESTIMONIALS ====================

@staff_required
def testimonials_view(request):
    """Manage customer reviews displayed on the website."""
    testimonials = Testimonial.objects.all().order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            location = request.POST.get('location', 'Lagos').strip()
            vehicle_purchased = request.POST.get('vehicle_purchased', '').strip()
            rating = request.POST.get('rating', '5')
            comment = request.POST.get('comment', '').strip()

            if name and comment:
                Testimonial.objects.create(
                    name=name,
                    location=location,
                    vehicle_purchased=vehicle_purchased,
                    rating=int(rating) if rating.isdigit() else 5,
                    comment=comment,
                    is_active=True
                )
                messages.success(request, "Customer testimonial added.")
        return redirect('admin_panel:testimonials')

    return render(request, 'admin_panel/testimonials.html', {'testimonials': testimonials})


@staff_required
def testimonial_delete_view(request, pk):
    """Delete a customer testimonial."""
    item = get_object_or_404(Testimonial, pk=pk)
    item.delete()
    messages.success(request, "Testimonial removed.")
    return redirect('admin_panel:testimonials')
