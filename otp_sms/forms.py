# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import time
from datetime import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from phonenumber_field.formfields import PhoneNumberField
from .models import SMSDevice
from .conf import settings
from .adapters import AdapterError


class SMSAuthenticationFormMixin(object):
    def clean_otp(self):
        now = datetime.now()
        attempt = self.request.session.get(settings.OTP_SMS_SESSION_KEY_ATTEMPT, 0)
        last_attempt_time = self.request.session.get(settings.OTP_SMS_SESSION_KEY_LAST_ATTEMPT_TIME)
        if last_attempt_time:
            try:
                last_attempt_time = datetime.fromtimestamp(last_attempt_time)
            except Exception:
                last_attempt_time = None

        if attempt:
            try:
                attempt = int(attempt)
            except ValueError:
                attempt = 0

        if settings.OTP_SMS_COUNT_ATTEMPTS and attempt >= settings.OTP_SMS_COUNT_ATTEMPTS:
            if settings.OTP_SMS_LATENCY_ATTEMPTS is not None and last_attempt_time \
                    and now - last_attempt_time < settings.OTP_SMS_LATENCY_ATTEMPTS:
                raise forms.ValidationError(
                    _('You have exceeded the limit SMS, try after %(minutes)d minutes'),
                    params={'minutes': settings.OTP_SMS_LATENCY_ATTEMPTS.total_seconds() / 60}
                )
            else:
                attempt = 0

        self.request.session[settings.OTP_SMS_SESSION_KEY_LAST_ATTEMPT_TIME] = time.mktime(datetime.now().timetuple())
        self.request.session[settings.OTP_SMS_SESSION_KEY_ATTEMPT] = attempt + 1

    def generate_token(self, device):
        self.request.session[settings.OTP_SMS_SESSION_KEY_DEVICE_ID] = device.pk

        try:
            device.generate_token()
        except AdapterError as e:
            if settings.DEBUG:
                raise e
            raise forms.ValidationError(_('Error sending sms'))


class SMSAuthenticationForm(AuthenticationForm):
    username = PhoneNumberField(label=_('Phone number'))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(number=username, token=password, request=self.request)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class SMSSendForm(SMSAuthenticationFormMixin, forms.ModelForm):
    class Meta:
        model = SMSDevice
        fields = ('number',)

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(SMSSendForm, self).__init__(*args, **kwargs)

    def clean(self):
        self.clean_otp()
        return self.cleaned_data

    def save(self, *args, **kwargs):
        instance = super(SMSSendForm, self).save(*args, **kwargs)

        try:
            self.generate_token(instance)
        except forms.ValidationError as e:
            self.add_error(None, e)
            return None

        return instance