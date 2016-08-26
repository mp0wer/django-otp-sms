# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import SMSDevice


class SMSBackend(ModelBackend):
    def authenticate(self, number=None, token=None, request=None):
        UserModel = get_user_model()
        user = None

        if request:
            device = SMSDevice.get(request, number)
            if device and device.verify_token(token):
                try:
                    user = UserModel._default_manager.get_by_natural_key(device.number)
                except UserModel.DoesNotExist:
                    user = self.create_user(request, device)

        return user

    def create_user(self, request, device):
        return