from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from django.views.decorators.http import require_POST


@require_POST
@ratelimit(key='user_or_ip', rate='10/m', method='POST')
@ratelimit(key='ip', rate='5/m', method='POST')
def login_view(request):
    """
    Simple rate limiting:
    - Authenticated users: 10 req/min
    - Anonymous users: 5 req/min
    """

    if getattr(request, 'limited', False):
        return JsonResponse(
            {'detail': 'Too many requests. Please try again later.'},
            status=429
        )

    return JsonResponse({'detail': 'Login endpoint'})