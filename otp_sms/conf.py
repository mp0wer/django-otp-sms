# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from datetime import timedelta
from django.conf import settings as django_settings


class Settings(object):
    _defaults = {
        'OTP_SMS_SESSION_KEY_DEVICE_ID': 'OTP-DEVICE-ID',
        'OTP_SMS_SESSION_KEY_LAST_ATTEMPT_TIME': 'OTP-LAST-TIME',
        'OTP_SMS_SESSION_KEY_ATTEMPT': 'OTP-ATTEMPT',
        'OTP_SMS_COUNT_ATTEMPTS': 3,
        'OTP_SMS_LATENCY_ATTEMPTS': timedelta(minutes=5),
        'OTP_SMS_AUTH': None,
        'OTP_SMS_FROM': None,
        'OTP_SMS_TOKEN_TEMPLATE': '{token}',
        'OTP_SMS_TOKEN_VALIDITY': 300,
        'OTP_SMS_TEST_NUMBER': '+79000000000',
        'OTP_SMS_ADAPTER': 'otp_sms.adapters.ConsoleAdapter',
        'OTP_SMS_NOTIFY_ADMINS_ADAPTER_ERROR': True
    }

    def __getattr__(self, name):
        if hasattr(django_settings, name):
            value = getattr(django_settings, name)
        elif name in self._defaults:
            value = self._defaults[name]
        else:
            raise AttributeError(name)

        return value


settings = Settings()