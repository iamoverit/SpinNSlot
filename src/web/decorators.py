from functools import wraps

from django.shortcuts import redirect

from web.models import SiteConfiguration


def club_open_required(view_func):
    """Prevent public booking/registration mutations while the club is closed."""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if SiteConfiguration.get_solo().is_closed:
            return redirect('index')
        return view_func(request, *args, **kwargs)

    return wrapped_view
