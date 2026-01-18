from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.contrib.gis.geoip2 import GeoIP2
from .models import RequestLog, BlockedIP

CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours

class IPTrackingMiddleware:
    """
    Logs requests, blocks blacklisted IPs, and adds geolocation info using GeoIP2.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip = GeoIP2(settings.GEOIP_PATH)

    def __call__(self, request):
        ip_address = self._get_client_ip(request)

        # Block IP if in blacklist
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Log request if logging is enabled
        if getattr(settings, "ENABLE_IP_LOGGING", False):
            # Check cache first
            geo = cache.get(f"geo_{ip_address}")
            if not geo:
                try:
                    geo = {
                        "city": self.geoip.city(ip_address)["city"],
                        "country": self.geoip.city(ip_address)["country_name"]
                    }
                except Exception:
                    geo = {"city": None, "country": None}

                cache.set(f"geo_{ip_address}", geo, CACHE_TIMEOUT)

            RequestLog.objects.create(
                ip_address=ip_address,
                path=request.path,
                city=geo.get("city"),
                country=geo.get("country")
            )

        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request):
        """Retrieve client IP address, accounting for proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")