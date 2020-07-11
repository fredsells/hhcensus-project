"""
Django settings for hhcensus project.

Generated by 'django-admin startproject' using Django 2.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
#import platform
#import socket
#print (socket.getfqdn() )  #use this to get server name if needed
from .private import hharweb2
from .private import development
from .private import production
from .private import common

HHARWEB2_CONNECTION_STRING = hharweb2.CONNECTION_STRING

EMAIL_HOST = 'smtp.hebrewhome.org'
SERVER_EMAIL = 'django.error@hebrewhome.org'


DATE_INPUT_FORMATS = ['%Y-%m-%d'] #'%d-%m-%Y', '%m/%d/%Y', 

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

SECRET_KEY = common.SECRET_KEY

ALLOWED_HOSTS = ['*'] #todo restrict to RiverSpring domain.

#NOTE: django simple email sender takes a text string while more complex Python email modules takes a list.
# all distro lists are defined as list and converted in sending module if necessary.
# The django module is not capable of handling attachments, which are needed for Sagely

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False  #True=errors show up on web page; False errors emailed to ADMINS
PRODUCTION_EMAIL = False
PRODUCTION = False

if PRODUCTION:
    BED_STATUS_LOCK_HOUR = 8  #becomes 8:00 am
    DATABASES = production.DATABASES
else:
    BED_STATUS_LOCK_HOUR = 16  #becomes 4:00 pm for testing
    DATABASES = development.DATABASES

TEST_EMAIL_RECIPIENTS =  [  'frederick.sells@RiverSpringHealth.org', 
                            'jonathan.clark@RiverSpringHealth.org',
                            'antonique.martin@RiverSpringHealth.org']

ADMINS =   [ ('DjangoAdmin', 'ADMINS@RiverSpringHealth.org'), ]


if PRODUCTION_EMAIL:   #use this flag when testing production system before going live
    EMAIL_SUBJECT_PREFIX = ''  # default='[Django] '
    CENSUS_RECIPIENTS = ['censusnotification@hebrewhome.org']   
    FROM_EMAIL_ADDRESS = 'no-reply@hebrewhome.org'
    SAGELY2_DISTRIBUTION_LIST = ['Sagely2@hebrewhome.org']
    CENSUS_UPDATE_REPORT_RECIPIENTS = ['CensusUpdateReport@hebrewhome.org']
else:
    SAGELY2_DISTRIBUTION_LIST = TEST_EMAIL_RECIPIENTS
    CENSUS_RECIPIENTS = TEST_EMAIL_RECIPIENTS
    FROM_EMAIL_ADDRESS = 'no-reply@hebrewhome.org'
    EMAIL_SUBJECT_PREFIX = '***TESTING*** '
    CENSUS_UPDATE_REPORT_RECIPIENTS = TEST_EMAIL_RECIPIENTS
 
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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

USE_L10N = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static") #used by collectstatic in production

