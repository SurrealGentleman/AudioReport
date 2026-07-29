from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405

CORS_ALLOWED_ORIGINS = env.list(  # noqa: F405
    "DJANGO_CORS_ALLOWED_ORIGINS",
    default=[],
)
CSRF_TRUSTED_ORIGINS = env.list(  # noqa: F405
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=[],
)

EMAIL_BACKEND = env(  # noqa: F405
    "DJANGO_EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT")  # noqa: F405
SECURE_HSTS_SECONDS = env("DJANGO_HSTS_SECONDS")  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = env(  # noqa: F405
    "DJANGO_HSTS_INCLUDE_SUBDOMAINS"
)
SECURE_HSTS_PRELOAD = env("DJANGO_HSTS_PRELOAD")  # noqa: F405


DATABASES["default"]["CONN_MAX_AGE"] = env.int(  # noqa: F405
    "DB_CONN_MAX_AGE",
    default=60,
)
