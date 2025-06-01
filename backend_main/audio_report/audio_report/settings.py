import os
import environ
from pathlib import Path
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Connecting the .env file
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DJANGO_DEBUG")

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "axes",
    # "channels",

    # Apps
    "posts",
    "departments",
    "employees",
    "tasks",
    "meetings",
    "ai",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]


# Настройки CORS
# адреса фронта (фронт запущен из контейнера)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://react_frontend_main_audio_report:5173",
]
# (фронт запущен локально)
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:5173",
# ]

CORS_ALLOW_CREDENTIALS = True  # Разрешаем передавать cookies и заголовки авторизации
CORS_ALLOW_HEADERS = [
    "content-type",
    "authorization",
    "x-csrftoken",
]


# Разрешаем доверенные источники для CSRF
# (фронт запущен из контейнера)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://react_frontend_main_audio_report:5173",
]
# (фронт запущен локально)
# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:5173",
# ]


# Настройки REST API
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DATE_FORMAT": "%d.%m.%Y",  # Отображение дат
}


# Настройки JWT
# SIMPLE_JWT = {
#     "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # Время жизни токена
#     "REFRESH_TOKEN_LIFETIME": timedelta(days=7), # Время жизни refresh-токена
#     "AUTH_HEADER_TYPES": ("Bearer",),  # Формат заголовка Authorization: Bearer <token>
# }
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # Уменьшаем срок жизни
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # Обновление refresh-токена при каждом использовании
    "BLACKLIST_AFTER_ROTATION": True,  # Старые refresh-токены нельзя использовать
    "AUTH_COOKIE": "access_token",  # Название куки
    "AUTH_COOKIE_REFRESH": "refresh_token",  # Название refresh куки
    "AUTH_COOKIE_SECURE": False,  # Только HTTPS (на проде True)
    "AUTH_COOKIE_HTTP_ONLY": True,  # Нельзя получить через JS (защита от XSS)
    "AUTH_COOKIE_SAMESITE": "Lax",  # Защита от CSRF
}


CSRF_COOKIE_SECURE = False # (на проде True)
CSRF_COOKIE_HTTPONLY = False  # Доступен JS
CSRF_COOKIE_SAMESITE = "Lax"


AXES_FAILURE_LIMIT = 5  # Блокировка после 5 неудачных попыток
AXES_COOLOFF_TIME = timedelta(minutes=10)  # Разблокировка через 10 минут
AXES_LOCKOUT_TEMPLATE = "lockout.html"  # Страница блокировки


SECURE_HSTS_SECONDS = 0  # Принудительный HTTPS на 1 год (31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False # (на проде True)
SECURE_HSTS_PRELOAD = False # (на проде True)
SECURE_SSL_REDIRECT = False  # Редирект HTTP → HTTPS (на проде True)


SECURE_BROWSER_XSS_FILTER = True  # Защита от XSS
SECURE_CONTENT_TYPE_NOSNIFF = True  # Блокировка подделки MIME-типа
X_FRAME_OPTIONS = "DENY"  # Защита от Clickjacking


ROOT_URLCONF = 'audio_report.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'audio_report.wsgi.application'


# Подключение ASGI
# ASGI_APPLICATION = "audio_report.asgi.application"
# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {"hosts": [("redis", 6379)]},
#     },
# }


# Настройки Celery
# CELERY_BROKER_URL = "redis://redis:6379/0"
# CELERY_ACCEPT_CONTENT = ["json"]
# CELERY_TASK_SERIALIZER = "json"


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # или другой SMTP-сервер
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'alekseevalekseykla203040@gmail.com'
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

# Database
DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}


AUTH_USER_MODEL = 'employees.Employee'


AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",  # Правильный бэкенд django-axes
    "django.contrib.auth.backends.ModelBackend",  # Обычная аутентификация Django
]


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Yekaterinburg'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Каталог для сбора статики для продакшена
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]  # Дополнительные папки (если есть)


# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Каталог для сбора статики


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
