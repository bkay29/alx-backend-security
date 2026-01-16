from django.conf import settings
from django.http import HttpResponseForbidden
from .models import RequestLog, BlockedIP

class IPTrackingMiddleware:
    """
    Logs requests and blocks IPs in BlockedIP table.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self._get_client_ip(request)

        # Block IP if in blacklist
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Log the request if logging is enabled
        if getattr(settings, "ENABLE_IP_LOGGING", False):
            RequestLog.objects.create(
                ip_address=ip_address,
                path=request.path
            )

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        """Retrieve client IP address, accounting for proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")