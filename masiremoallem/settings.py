"""
Django settings for masiremoallem project.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z3%#2=lyzfa*8ch4%)6qb=0^c6(ducxith=udq5y$=u@y$jl1x'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*'] # فعلا برای تست همه هاست‌ها رو باز می‌کنیم


# Application definition

INSTALLED_APPS = [
    'daphne',  # 👈 باید حتما اولین باشه
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # ...
    'channels', # 👈 اضافه کن
    'accounts',
    'dashboard',
    'exams',
    'forum',
    'competitions',
    'events',
    'rivalry',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'masiremoallem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # مسیر پوشه تمپلیت‌ها
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

WSGI_APPLICATION = 'masiremoallem.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


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


# Internationalization (تنظیمات زبان و زمان)
LANGUAGE_CODE = 'fa-ir' # تغییر به فارسی
TIME_ZONE = 'Asia/Tehran' # تغییر به منطقه زمانی تهران
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] # پوشه برای فایل‌های استاتیک پروژه

# Media files (عکس‌های آپلود شده مثل لوگو)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Email (برای تست ایمیل در کنسول)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ==========================================
# 👇 این خط مهمترین بخش است 👇
# ==========================================
# به جنگو می‌گوییم که مدل کاربری ما (CustomUser) جایگزین مدل پیش‌فرض شود
AUTH_USER_MODEL = 'accounts.CustomUser'

LOGIN_URL = '/accounts/login/'


ASGI_APPLICATION = 'masiremoallem.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # برای تست لوکال عالیه
    },
}