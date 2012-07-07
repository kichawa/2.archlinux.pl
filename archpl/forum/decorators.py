import functools

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden


def moderator_login_required(view):
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.forum_user.is_authenticated():
            path = request.build_absolute_uri()
            return redirect_to_login(path, None, REDIRECT_FIELD_NAME)
        if not request.forum_user.is_moderator:
            return HttpResponseForbidden("Moderator account required")
        return view(request, *args, **kwargs)

    return wrapper
