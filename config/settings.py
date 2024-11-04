"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
# https://docs.djangoproject.com/en/5.1/ref/settings/#secret-key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if DEBUG and not SECRET_KEY:
    if DEBUG:
        django_secret_key_file = ".django_secret_key"
        if os.path.isfile(django_secret_key_file):
            with open(django_secret_key_file) as f:
                SECRET_KEY = f.read().strip()
        else:
            SECRET_KEY = get_random_secret_key()
            with open(django_secret_key_file, "w") as f:
                f.write(SECRET_KEY)
            print(f"Generated new SECRET_KEY and saved to {django_secret_key_file}")
    else:
        raise ValueError("The SECRET_KEY environment variable is not set and DEBUG is False.")

# https://docs.djangoproject.com/en/5.1/ref/settings/#std-setting-SECRET_KEY_FALLBACKS
SECRET_KEY_FALLBACKS = []

# SECURITY WARNING: keep the encryption key used in production secret!
ENCRYPTION_KEY = os.getenv("DJANGO_ENCRYPTION_KEY")
if DEBUG and not ENCRYPTION_KEY:
    if DEBUG:
        django_encryption_key_file = ".django_encryption_key"
        if os.path.isfile(django_encryption_key_file):
            with open(django_encryption_key_file, "rb") as f:
                ENCRYPTION_KEY = f.read()
        else:
            from cryptography.fernet import Fernet
            ENCRYPTION_KEY = Fernet.generate_key()
            with open(django_encryption_key_file, "wb") as f:
                f.write(ENCRYPTION_KEY)
            print(f"Generated new ENCRYPTION_KEY and saved to {django_encryption_key_file}")
    else:
        raise ValueError("The ENCRYPTION_KEY environment variable is not set and DEBUG is False.")

ENCRYPTION_KEY_FALLBACKS = []

# https://docs.djangoproject.com/en/5.1/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "encryption.apps.EncryptionConfig",
    "webhooks.apps.WebhooksConfig",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Logging
# https://docs.djangoproject.com/en/5.1/topics/logging/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'project': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'filters': {},
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)-8s %(name)-30s : %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"