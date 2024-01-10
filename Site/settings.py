from pathlib import Path
from configparser import ConfigParser
from minio import Minio

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_ROOT = 'media/'
SOFT_LOADERS_ROOT = MEDIA_ROOT + 'soft_files/'
PHOTOS_ROOT = MEDIA_ROOT + 'soft_images/'
STATIC_ROOT = './static/'

CONFIG = ConfigParser()
CONFIG.read(BASE_DIR / 'config.cfg')

SECRET_KEY = CONFIG.get('Django', 'secret_key')
WEB_SERVICE_SEKRET_KEY = CONFIG.get('GO', 'key')

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
DEBUG = True

STATIC_URL = 'static/'
MEDIA_URL = 'media/'
ROOT_URLCONF = 'Site.urls'
WSGI_APPLICATION = 'Site.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CORS_ALLOW_CREDENTIALS = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'storages',
    'rest_framework',
    'SoftLoading',
    'Profiles',
    'drf_yasg'
]

# Minio settings:
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_S3_ENDPOINT_URL = str(CONFIG.get('Minio', 'url'))

AWS_ACCESS_KEY_ID       = CONFIG.get('Minio', 'key_id')
AWS_SECRET_ACCESS_KEY   = CONFIG.get('Minio', 'access_key')
AWS_STORAGE_BUCKET_NAME = CONFIG.get('Minio', 'bucket_name')
AWS_QUERYSTRING_AUTH = False
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
LAMBDA_BUCKET_NAME = CONFIG.get('Minio', 'bucket_name')

MINIO = Minio(
    CONFIG.get('Minio', 'host'),
    access_key=AWS_ACCESS_KEY_ID,
    secret_key=AWS_SECRET_ACCESS_KEY,
    secure=False
)
# minio server ./

# Reddis settings:
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": CONFIG.get('Redis', 'url'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Database:
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     CONFIG.get('Postgres DB', 'name'),
        'USER':     CONFIG.get('Postgres DB', 'user'),
        'PASSWORD': CONFIG.get('Postgres DB', 'password'),
        'HOST':     CONFIG.get('Postgres DB', 'host'),
        'PORT':     CONFIG.get('Postgres DB', 'port')
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Should be first!
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

