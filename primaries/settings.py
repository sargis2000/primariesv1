"""
Django settings for primaries project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


project_folder = os.path.expanduser("~/primaries")
load_dotenv(os.path.join(project_folder, ".env"))
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
if str(os.environ["DEPLOYMENT_MODE"]) == "True":
    DEBUG = False
    ALLOWED_HOSTS = ["*"]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["*"]
SECRET_KEY = str(os.environ["SECRET_KEY"])
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third-party apps
    "rest_framework",
    "rest_framework.authtoken",
    "rest_auth",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.facebook",
    "phonenumber_field",
    "corsheaders",
    "ckeditor",
    "ckeditor_uploader",
    "primaries_app.apps.PrimariesAppConfig",
    "accounts",
    "drf_yasg",
    "cloudinary_storage",
    "cloudinary",
    "Idram",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = [
    "https://primaries-back.herokuapp.com",
    "https://primaries-front.herokuapp.com",
    "https://app.primaries.am",
    "http://127.0.0.1:4040",
    "http://127.0.0.1:8000",
    "http://localhost:4040",
    "http://localhost:8000",
    "https://api.primaries.am",
    "https://app-primaries.vercel.app",
]
CORS_ALLOWED_ORIGINS = [
    "https://app.primaries.am",
    "http://localhost:8000",
    "https://primaries-front.herokuapp.com",
    "https://primaries-back.herokuapp.com",
    "http://localhost:4040",
    "http://127.0.0.1:8000",
    "https://api.primaries.am",
    "https://app-primaries.vercel.app",
]
ROOT_URLCONF = "primaries.urls"
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
            ],
        },
    },
]

WSGI_APPLICATION = "primaries.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = os.environ.get("DATABASE_URL")
db_from_env = dj_database_url.config(
    default=DATABASE_URL, conn_max_age=500, ssl_require=True
)
DATABASES["default"].update(db_from_env)

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "accounts.utils.custom_exception_handler",
}
# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "hy"

TIME_ZONE = "UTC"

USE_I18N = True
DATE_INPUT_FORMATS = ["%d/%m/%Y"]

USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATIC_URL = "static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"
CKEDITOR_UPLOAD_PATH = "ck-editor/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": "dessjvuyq",
    "API_KEY": "394724571544662",
    "API_SECRET": "lMei4a54Iu1OStqym9rFjezK1Jo",
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
AUTH_USER_MODEL = "accounts.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = "/"
VOTER_PROFILE_ACTIVATION_URL = "https://api.primaries.am/confirm/voter/"
CANDIDATE_PROFILE_ACTIVATION_URL = "https://api.primaries.am/confirm/candidate/"

# email settings
EMAIL_HOST_PASSWORD = str(os.getenv("MAILGUN_KEY"))
EMAIL_FROM = str(os.getenv("EMAIL_FROM"))
ADMIN_EMAIL = str(os.getenv("ADMIN_EMAIL"))

SITE_ID = 1
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
