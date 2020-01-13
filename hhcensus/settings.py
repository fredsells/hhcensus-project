"""
Django settings for hhcensus project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'q2m59ym@%j4e94o5yj+a+h+s_x_^0atc=a-1gy%v9as8_!px=2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'webapp',
    'webapp.templatetags.app_filters',
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

ROOT_URLCONF = 'hhcensus.urls'

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

WSGI_APPLICATION = 'hhcensus.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
#  r'DRIVER={SQL Server Native Client 10.0};'
#         r'SERVER=.\SQLEXPRESS;'
#         r'DATABASE=HHBedCheck;'
#          r'Trusted_Connection=yes;'



LOCAL_SQLEXPRESS_DB = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': 'HHBedCheck',
        'HOST': r'.\SQLEXPRESS',
       # 'PORT':'1433',
        'USER': 'django',
        'PASSWORD': 'django',
        'OPTIONS': {
                 'driver': 'SQL Server Native Client 10.0',                
                 }
        },  
    }

HHARSWLSQLDEV01 = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'HOST': '.', # 'HHARSWLSQLDEV01.HHARSWLSQLDEV01',
        'PORT': '', #'1433',
        'NAME': 'HHdev',
        'Trusted_Connection': 'yes;',
        'OPTIONS': {
            'driver': 'ODBC Driver 13 for SQL Server',  #got from list of drivers via Admin Tools/ODBC
            'unicode_results': True,
        },
    },
}

LAPTOP = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'HOST': '.', # 'HHARSWLSQLDEV01.HHARSWLSQLDEV01',
        'PORT': '', #'1433',
        'NAME': 'FredTesting',
        'Trusted_Connection': 'yes;',
        'OPTIONS': {
            'driver': 'ODBC Driver 13 for SQL Server',  #got from list of drivers via Admin Tools/ODBC
            'unicode_results': True,
        },
    },
}

DATABASES = LAPTOP

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# LANGUAGE_CODE = 'en-us'
# 
# TIME_ZONE = 'UTC'
# 
# USE_I18N = True
# 
# USE_L10N = True
# 
# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
