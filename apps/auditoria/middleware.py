from uuid import uuid4

from apps.auditoria.context import clear_auditoria_context, set_auditoria_context


class AuditoriaContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        set_auditoria_context(
            usuario=user,
            origem='api',
            request_id=request.headers.get('X-Request-ID') or uuid4().hex,
            ip=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        try:
            return self.get_response(request)
        finally:
            clear_auditoria_context()


def _get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
