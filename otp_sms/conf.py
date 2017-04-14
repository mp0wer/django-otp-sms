# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from datetime import timedelta
from django.conf import settings
from appconf import AppConf


class OTPSmsConf(AppConf):
    SESSION_KEY_DEVICE_ID = 'OTP-DEVICE-ID'
    SESSION_KEY_LAST_ATTEMPT_TIME = 'OTP-LAST-TIME'
    SESSION_KEY_ATTEMPT = 'OTP-ATTEMPT'
    COUNT_ATTEMPTS = 3
    LATENCY_ATTEMPTS = timedelta(minutes=5)
    AUTH = None
    FROM = None
    TOKEN_TEMPLATE = '{token}'
    TOKEN_VALIDITY = 300
    TEST_NUMBER = '+79000000000'
    ADAPTER = 'otp_sms.adapters.ConsoleAdapter'
    NOTIFY_ADMINS_ADAPTER_ERROR = True
    TEST_MODE = False

    class Meta:
        prefix = 'OTP_SMS'
