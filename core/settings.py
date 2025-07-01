# core/settings.py
import os
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import dj_database_url  # type: ignore
from corsheaders.defaults import default_headers

# -------------------------------------------------------------------
# Path & Basic Config
# -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
# Use an explicit environment variable for CI testing to ensure reliability
IS_TESTING = os.environ.get('CI_TESTING', 'False') == 'True'

# Define common variables that might be accessed early, with defaults for non-testing
# These will be overridden in the IS_TESTING block if needed for testing.
SECRET_KEY = config("SECRET_KEY", default="secretkey")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())
# Define CALLBACK_URL here with a robust default, so it's always available.
# This prevents decouple.UndefinedValueError if it's accessed before the IS_TESTING block's override.
CALLBACK_URL = config("CALLBACK_URL", default="http://localhost:5173")


if IS_TESTING:
    # For testing, provide dummy values for all potentially missing env vars
    SECRET_KEY = "test-secret-key"
    DEBUG = True
    ALLOWED_HOSTS = ["localhost"]
    # Override CALLBACK_URL for testing specifically
    CALLBACK_URL = "http://localhost:5173" # Ensure this is used for tests
    # Add dummy values for other variables that might be accessed unconditionally
    # or within structures that are always defined, even if their usage is conditional.
    # This prevents decouple.UndefinedValueError during settings file loading.
    GOOGLE_CLIENT_ID = "dummy-google-client-id-for-test"
    GOOGLE_CLIENT_SECRET = "dummy-google-client-secret-for-test"
    MAILGUN_API_KEY = "dummy-mailgun-api-key-for-test"
    MAILGUN_SENDER_DOMAIN = "dummy.mailgun.org"
    DEFAULT_FROM_EMAIL = "noreply@test.com"
    SERVER_EMAIL = "issues@test.com"
    EXPRESS_SERVICE_URL = "http://localhost:3000/api/services" # Dummy URL
    CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
    CORS_ORIGIN_WHITELIST = ["http://localhost:5173"]
    CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]
    SOCIAL_AUTH_ALLOWED_REDIRECT_URIS = ["http://localhost:5173/login"]
    ACTIVATION_URL = "auth/users/activate/{uid}/{token}" # Dummy URL for testing


# -------------------------------------------------------------------
# Applications & Middleware
# -------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "corsheaders",
    "djoser",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "whitenoise.runserver_nostatic",
    "anymail",
    "django_extensions",
    "django_userforeignkey",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
]

LOCAL_APPS = [
    "users.apps.UsersConfig",
    "orders.apps.OrdersConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.BrokenLinkEmailsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django_userforeignkey.middleware.UserForeignKeyMiddleware",
]

# -------------------------------------------------------------------
# Templates
# -------------------------------------------------------------------
ROOT_URLCONF = "core.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
            ],
        },
    },
]
WSGI_APPLICATION = "core.wsgi.application"

# -------------------------------------------------------------------
# Static Files
# -------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------------------------------------------------------
# Internationalization
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SITE_ID = 1

# -------------------------------------------------------------------
# Database & Caching
# -------------------------------------------------------------------
if IS_TESTING:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            # Changed LOCATION to a valid redis:// URL, but still use FakeStrictRedis
            "LOCATION": "redis://localhost:6379/1",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_CLASS": "fakeredis.FakeStrictRedis", # Ensure fakeredis is used
                "IGNORE_EXCEPTIONS": True,
            },
        }
    }

else:
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://postgres:postgres@localhost:5432/postgres",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": config(
                "REDIS_URL", default="redis://localhost:6379/1"
            ),  # <-- fallback
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
                "PASSWORD": config("REDIS_PASSWORD", default=""),  # fallback: no auth
            },
        }
    }


# -------------------------------------------------------------------
# Authentication
# -------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# -------------------------------------------------------------------
# CORS Settings
# -------------------------------------------------------------------
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_EXPOSE_HEADERS = [
    "Content-Type",
    "authorization",
    "X-CSRFToken",
    "Access-Control-Allow-Origin: *",
]
CORS_ALLOW_HEADERS = default_headers + (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]

# These settings are now handled by the IS_TESTING block above for test mode
# and will use decouple.config for non-test environments.
if not IS_TESTING:
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default="")
    CORS_ORIGIN_WHITELIST = config("CORS_ORIGIN_WHITELIST", cast=Csv(), default="")
    CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", cast=Csv(), default="")
else:
    # These are already set in the main IS_TESTING block at the top
    pass


# -------------------------------------------------------------------
# Django REST Framework & JWT
# -------------------------------------------------------------------
DEFAULT_RENDERER_CLASSES = ("rest_framework.renderers.JSONRenderer",)
if DEBUG:
    DEFAULT_RENDERER_CLASSES += ("rest_framework.renderers.BrowsableAPIRenderer",)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERER_CLASSES,
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "1000/day",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS512",
}

# -------------------------------------------------------------------
# Admin & URLs
# -------------------------------------------------------------------
if not IS_TESTING:
    ADMIN_URL = config("ADMIN_URL", default="admin/")
    LOGIN_URL = config("LOGIN_URL", default="/auth/login/")
    # REMOVED: CALLBACK_URL = config("CALLBACK_URL", default="/auth/callback/") # This line is removed
else:
    # These are already set in the main IS_TESTING block at the top
    ADMIN_URL = "admin/"
    LOGIN_URL = "/auth/login/"
    # CALLBACK_URL is already defined at the top IS_TESTING block


ADMINS = [("FM-CORE API", "arnelimperial.com")]
MANAGERS = ADMINS

# -------------------------------------------------------------------
# Django-Allauth, Djoser, Anymail
# -------------------------------------------------------------------
ACCOUNT_SIGNUP_FIELDS = ["username*", "email*", "password1*", "password2"]
ACCOUNT_LOGIN_METHODS = ["email", "username"]
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
# This now uses the CALLBACK_URL defined at the top of the IS_TESTING block
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = CALLBACK_URL

# This entire block needs to be conditional OR its internal config() calls need defaults
if not IS_TESTING:
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": ["email", "profile", "openid"],
            "AUTH_PARAMS": {"access_type": "offline"},
            "OAUTH_PKCE_ENABLED": True,
            "APP": {
                "client_id": config("GOOGLE_CLIENT_ID"),
                "secret": config("GOOGLE_CLIENT_SECRET"),
            },
        }
    }
else:
    # Provide a dummy SOCIALACCOUNT_PROVIDERS structure for testing
    # The values for client_id and secret are already set in the top IS_TESTING block
    SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": ["email", "profile", "openid"],
            "AUTH_PARAMS": {"access_type": "offline"},
            "OAUTH_PKCE_ENABLED": True,
            "APP": {
                "client_id": GOOGLE_CLIENT_ID, # Use the dummy value defined at the top
                "secret": GOOGLE_CLIENT_SECRET, # Use the dummy value defined at the top
            },
        }
    }


REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "_auth",
    "JWT_AUTH_REFRESH_COOKIE": "_refresh",
    "JWT_AUTH_HTTPONLY": False,
    "USER_DETAILS_SERIALIZER": "users.serializers.CustomUserDetailsSerializer",
}

DJOSER = {
    "LOGIN_FIELD": "email",
    "USERNAME_RESET_CONFIRM_URL": "auth/username/reset/confirm/{uid}/{token}",
    "PASSWORD_RESET_CONFIRM_URL": "auth/password/reset/confirm/{uid}/{token}",
    # This line was causing an issue because it was always calling config()
    # Now it uses the variable defined in the IS_TESTING block, or config() for non-testing.
    "ACTIVATION_URL": (
        ACTIVATION_URL if IS_TESTING else config(
            "ACTIVATION_URL", default="auth/users/activate/{uid}/{token}"
        )
    ),
    "HIDE_USERS": False,
    "SOCIAL_AUTH_TOKEN_STRATEGY": "djoser.social.token.jwt.TokenStrategy",
    # This line was causing an issue because it was always calling config()
    # Now it uses the variable defined in the IS_TESTING block, or config() for non-testing.
    "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS": (
        SOCIAL_AUTH_ALLOWED_REDIRECT_URIS if IS_TESTING else config(
            "SOCIAL_AUTH_ALLOWED_REDIRECT_URIS", cast=Csv(), default=""
        )
    ),
    "SERIALIZERS": {
        "user": "djoser.serializers.UserSerializer",
        "current_user": "djoser.serializers.UserSerializer",
        "user_delete": "djoser.serializers.UserSerializer",
    },
}

# -------------------------------------------------------------------
# Mail & Express
# -------------------------------------------------------------------
if not IS_TESTING:
    ANYMAIL = {
        "MAILGUN_API_KEY": config("MAILGUN_API_KEY"),
        "MAILGUN_SENDER_DOMAIN": config("MAILGUN_SENDER_DOMAIN"),
        "MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
    }
    EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
    DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")
    SERVER_EMAIL = config("SERVER_EMAIL")
    EXPRESS_SERVICE_URL = config("EXPRESS_SERVICE_URL")
else:
    # Provide dummy values for ANYMAIL and email settings when testing
    ANYMAIL = {
        "MAILGUN_API_KEY": MAILGUN_API_KEY, # Use dummy from top IS_TESTING block
        "MAILGUN_SENDER_DOMAIN": MAILGUN_SENDER_DOMAIN, # Use dummy from top IS_TESTING block
        "MAILGUN_API_URL": "https://api.eu.mailgun.net/v3",
    }
    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend" # Use in-memory email backend for tests
    DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL # Use dummy from top IS_TESTING block
    SERVER_EMAIL = SERVER_EMAIL # Use dummy from top IS_TESTING block
    EXPRESS_SERVICE_URL = EXPRESS_SERVICE_URL # Use dummy from top IS_TESTING block


# -------------------------------------------------------------------
# Security
# -------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

if not DEBUG: # This condition relies on the DEBUG variable, which is set by IS_TESTING
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
    SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
    CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
    SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config(
        "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True, cast=bool
    )
    SECURE_HSTS_PRELOAD = config("SECURE_HSTS_PRELOAD", default=True, cast=bool)
    SECURE_CONTENT_TYPE_NOSNIFF = config(
        "SECURE_CONTENT_TYPE_NOSNIFF", default=True, cast=bool
    )

# -------------------------------------------------------------------
# Spectacular API Docs
# -------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "FinMark API",
    "DESCRIPTION": "API documentation for FinMark by Imperionite",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
