from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from apps.cars.models import Car
from .models import PurchaseRequest

def submit_purchase_request(request):
    """
    Handles purchase / vehicle reservation / inspection requests.
    Snapshots vehicle price, stores contact details, and notifies dealership.
    """
    if request.method != 'POST':
        return redirect('cars:list')

    car_id = request.POST.get('car_id', '').strip()
    customer_name = request.POST.get('customer_name', '').strip()
    customer_email = request.POST.get('customer_email', '').strip()
    customer_phone = request.POST.get('customer_phone', '').strip()
    inspection_date = request.POST.get('inspection_date', '').strip()
    message = request.POST.get('message', '').strip()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.POST.get('is_ajax') == '1'

    if not car_id or not customer_name or not customer_phone:
        err_msg = "Please provide your name, phone number, and select a vehicle."
        if is_ajax:
            return JsonResponse({'success': False, 'message': err_msg}, status=400)
        messages.error(request, err_msg)
        return redirect(request.META.get('HTTP_REFERER', 'cars:list'))

    car = get_object_or_404(Car, pk=int(car_id))

    parsed_date = None
    if inspection_date:
        try:
            parsed_date = inspection_date
        except Exception:
            parsed_date = None

    purchase_req = PurchaseRequest.objects.create(
        car=car,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        price_at_request=car.price,
        preferred_inspection_date=parsed_date or None,
        message=message,
        status='new'
    )

    purchase_req.notify_admin()

    success_msg = (
        f"Your purchase/inspection request for the {car.year} {car.make} {car.model} "
        f"has been received! Our dealership representative will call you immediately on {customer_phone}."
    )
    if is_ajax:
        return JsonResponse({'success': True, 'message': success_msg})

    messages.success(request, success_msg)
    return redirect('cars:detail', pk=car.pk)
