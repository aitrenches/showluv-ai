"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see:
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os
from corsheaders.defaults import default_headers

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

import environ, getpass

env = environ.Env()
environ.Env.read_env()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY")
API_KEY = env("API_KEY")
OPENAI_API_KEY = env("OPENAI_API_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = env("DEBUG")
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ['djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com', 'localhost', '0.0.0.0', '127.0.0.1',]
CSRF_TRUSTED_ORIGINS = ['https://localhost','https://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com', 'http://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com','https://127.0.0.1', 'http://localhost:8501']
CORS_ALLOWED_ORIGINS = ['https://localhost',
'https://youtube-to-twitter-generator.vercel.app',
'http://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com',
'https://djangoapp.vveeq17939eno.us-east-2.cs.amazonlightsail.com',
'https://127.0.0.1', 'http://localhost:3000', 'http://localhost:8501']

# CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-API-Key',
]

CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'accounts',
    'rest_framework',
    'youtube_to_twitter',
    'drf_yasg',
    'corsheaders',
    'image_gen',
    'test2',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {  
    'default': {  
        'ENGINE': 'django.db.backends.postgresql',  
        'NAME': env('DB_NAME'),  
        'USER': env('DB_USER'),  
        'PASSWORD': env('DB_PASSWORD'),  
        'HOST': env('DB_HOST'),  
        'PORT': '5432',  
    }  
}  



# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

########################################
#File storage settings
# STORAGES = {
#     # ...
#     "staticfiles": {
#         "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
#     },
# }
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
########################################

AWS_ACCESS_KEY_ID = env('S3_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = env('S3_SECRET_KEY')
AWS_STORAGE_BUCKET_NAME = env('S3_AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE= False
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = 'public-read'

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# if DEBUG:
#     # Local development settings
#     STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
# else:
#     # Production settings (using S3)
#     # s3 static settings
#     STATIC_LOCATION = 'static'
#     STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}/{STATIC_LOCATION}/'
#     STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

########################################
if DEBUG:
    # Local development settings
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    STATIC_URL = '/static/'
else:
    # Production settings (using S3)
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{STATIC_LOCATION}/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Media files (User uploads)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/'

    # Production settings (using S3 and WhiteNoise)
    # STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

########################################

# Common settings for both environments
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

REST_FRAMEWORK = {
    # 'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'core.urls.swagger_info',
    'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'delete', 'patch'],
    'SECURITY_DEFINITIONS': {
        'Api-Key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}
