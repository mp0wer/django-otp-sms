# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

DEBUG = True

SECRET_KEY = 'fake-key'

USE_TZ = True

DATABASES = dict(
    default=dict(
        ENGINE='django.db.backends.sqlite3',
        NAME=':memory:',
    ),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'formtools',
    'otp_sms',
    'tests'
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'otp_sms.backends.SMSBackend',
)

ROOT_URLCONF = 'tests.urls'

ADMINS = (('Admin', 'admin@test.com'),)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
