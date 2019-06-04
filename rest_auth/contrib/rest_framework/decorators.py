import functools

from rest_framework.request import Request


def sensitive_post_parameters(*parameters):
    """hide sensitive paramters from Django's error reporting.
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapper(req, *args, **kwargs):
            assert isinstance(req, Request), (
                "sensitive_post_parameters didn't receive an Request. "
            )
            req._request.sensitive_post_parameters = parameters or '__ALL__'
            return view(req, *args, **kwargs)
        return wrapper
    return decorator
