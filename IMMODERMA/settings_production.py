from .settings import *  # noqa: F401,F403


if DEBUG:
    raise ImproperlyConfigured(
        "Production tidak boleh berjalan dengan IMMODERMA_DEBUG=True."
    )

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "IMMODERMA_ALLOWED_HOSTS wajib diisi pada production."
    )

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"

