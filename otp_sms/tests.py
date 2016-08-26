# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from .models import SMSDevice
from .conf import settings


class SMSDeviceTestCase(TestCase):
    device = None

    def setUp(self):
        self.device = SMSDevice.objects.create(number=settings.OTP_SMS_TEST_NUMBER)

    def test_generate_challenge(self):
        self.device.generate_challenge()