from django.conf import settings
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.contrib.gis.geoip2 import GeoIP2
from django.contrib.gis.geoip2 import GeoIP2Exception

from .models import RequestLog, BlockedIP

CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours


class IPTrackingMiddleware:
    """
    Logs IP addresses, blocks blacklisted IPs,
    and enriches logs with optional GeoIP data.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.geoip = None

        # Initialize GeoIP ONLY if configured and available
        if getattr(settings, "GEOIP_PATH", None):
            try:
                self.geoip = GeoIP2()
            except GeoIP2Exception:
                self.geoip = None

    def __call__(self, request):
        ip_address = self._get_client_ip(request)

        # Block blacklisted IPs
        if ip_address and BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Your IP has been blocked.")

        # Log request if enabled
        if getattr(settings, "ENABLE_IP_LOGGING", False) and ip_address:
            geo = self._get_geo_data(ip_address)

            RequestLog.objects.create(
                ip_address=ip_address,
                path=request.path,
                city=geo.get("city"),
                country=geo.get("country"),
            )

        return self.get_response(request)

    def _get_geo_data(self, ip_address):
        """
        Fetch geolocation data with caching.
        Safe to call even if GeoIP is unavailable.
        """
        cache_key = f"ip_geo:{ip_address}"
        geo = cache.get(cache_key)

        if geo is not None:
            return geo

        geo = {"city": None, "country": None}

        if self.geoip:
            try:
                data = self.geoip.city(ip_address)
                geo["city"] = data.get("city")
                geo["country"] = data.get("country_name")
            except Exception:
                pass

        cache.set(cache_key, geo, CACHE_TIMEOUT)
        return geo

    @staticmethod
    def _get_client_ip(request):
        """
        Retrieve client IP address, accounting for proxies.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")