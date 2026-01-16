from django.conf import settings
from .models import RequestLog


class IPTrackingMiddleware:
    """
    Middleware to log IP address, request path, and timestamp
    for every incoming request when ENABLE_IP_LOGGING is True.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "ENABLE_IP_LOGGING", False):
            ip_address = self._get_client_ip(request)
            path = request.path

            RequestLog.objects.create(
                ip_address=ip_address,
                path=path
            )

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        """
        Retrieve client IP address, accounting for proxies.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")