from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """
    Decorator that checks if user is staff/admin.
    Returns JSON error for AJAX requests if unauthorized.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'You do not have permission to access the admin panel.'
                }, status=403)
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Keep the old function for backward compatibility
def check_admin(user):
    return user.is_authenticated and user.is_staff