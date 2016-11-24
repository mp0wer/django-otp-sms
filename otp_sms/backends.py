# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import SMSDevice
from .signals import user_created


class SMSBackend(ModelBackend):
    def __init__(self):
        super(SMSBackend, self).__init__()
        self.UserModel = get_user_model()

    def authenticate(self, number=None, token=None, request=None):
        user = None
        if request:
            device = SMSDevice.get(request, number)
            if device and device.verify_token(token):
                try:
                    user = self.UserModel._default_manager.get_by_natural_key(device.number)
                except self.UserModel.DoesNotExist:
                    user = self.create_user(request, device)

        return user

    def create_user(self, request, device):
        user = None
        if getattr(request, 'otp_sms_create_user', False):
            user = self.UserModel.objects.create_user(device.number)
            user_created.send(sender=user.__class__, request=request, user=user, phone=device.number)
        return user