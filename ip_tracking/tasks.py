from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import RequestLog, SuspiciousIP


@shared_task
def detect_suspicious_ips():
    """
    Runs hourly to detect suspicious IP activity.
    """

    one_hour_ago = timezone.now() - timedelta(hours=1)

    # 1️⃣ Rule: IPs with more than 100 requests in the last hour
    high_volume_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(count=models.Count('id'))
        .filter(count__gt=100)
    )

    for entry in high_volume_ips:
        SuspiciousIP.objects.get_or_create(
            ip_address=entry['ip_address'],
            defaults={'reason': 'More than 100 requests in one hour'}
        )

    # 2️⃣ Rule: Access to sensitive paths
    sensitive_paths = ['/admin', '/login']

    suspicious_requests = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago,
        path__startswith=tuple(sensitive_paths)
    )

    for log in suspicious_requests:
        SuspiciousIP.objects.get_or_create(
            ip_address=log.ip_address,
            defaults={'reason': f'Accessed sensitive path: {log.path}'}
        )