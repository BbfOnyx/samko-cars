from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from apps.cars.models import Car
from .models import Enquiry

def submit_enquiry(request):
    """
    Handles customer enquiry submission from car detail modal or general form.
    Supports both AJAX JSON requests and standard POST redirects.
    """
    if request.method != 'POST':
        return redirect('cars:list')

    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()
    car_id = request.POST.get('car_id', '').strip()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

    if not name or not phone or not message:
        err_msg = "Please fill in all required fields (Name, Phone, and Message)."
        if is_ajax:
            return JsonResponse({'success': False, 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect(request.META.get('HTTP_REFERER', 'core:contact'))

    car = None
    if car_id:
        try:
            car = Car.objects.get(pk=int(car_id))
        except (Car.DoesNotExist, ValueError):
            pass

    enquiry = Enquiry.objects.create(
        name=name,
        email=email,
        phone=phone,
        message=message,
        car=car,
        status='new'
    )

    enquiry.notify_admin()

    success_msg = "Thank you! Your enquiry has been sent to our sales team. We will contact you shortly."
    if is_ajax:
        return JsonResponse({'success': True, 'message': success_msg})

    messages.success(request, success_msg)
    return redirect(request.META.get('HTTP_REFERER', 'core:contact'))
