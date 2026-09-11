from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def staff_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff member or superuser.
    Redirects to the admin login page if unauthenticated or unauthorized.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in with your administrator credentials.")
            return redirect(f"/admin-panel/login/?next={request.path}")
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access restricted to authorized dealership administrators only.")
            return redirect('/admin-panel/login/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
