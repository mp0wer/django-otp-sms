# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.contrib.auth.middleware import AuthenticationMiddleware
from otp_sms.conf import settings
from otp_sms.views import SMSAuthenticationWizardView


@override_settings(
    OTP_SMS_TEST_MODE=True
)
class SMSAuthViewTestCase(TestCase):
    login_url = reverse_lazy('otp_sms_login')
    signup_url = reverse_lazy('otp_sms_signup')
    user_phone = settings.OTP_SMS_TEST_NUMBER

    def setUp(self):
        self.user_model = get_user_model()
        self.auth_middleware = AuthenticationMiddleware()
        # for Django 1.8 + python 3
        self.login_url = force_str(self.login_url)
        self.signup_url = force_str(self.signup_url)

    def processView(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('wizard' in response.context_data)
        self.assertTrue('management_form' in response.context_data['wizard'])

        management_form = response.context_data['wizard']['management_form']
        self.assertEqual(management_form.initial['current_step'], SMSAuthenticationWizardView.SMS_FORM_KEY)

        response = self.client.post(url, {
            management_form.add_prefix('current_step'): management_form.initial['current_step'],
            '{0}-number'.format(management_form.initial['current_step']): self.user_phone
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)
        self.assertTrue('wizard' in response.context_data)
        self.assertTrue('management_form' in response.context_data['wizard'])

        form = response.context_data['form']
        self.assertEqual(form.errors, {})

        management_form = response.context_data['wizard']['management_form']
        self.assertEqual(management_form.initial['current_step'], SMSAuthenticationWizardView.AUTH_FORM_KEY)

        response = self.client.post(url, {
            management_form.add_prefix('current_step'): management_form.initial['current_step'],
            '{0}-username'.format(management_form.initial['current_step']): form.initial['username'],
            '{0}-password'.format(management_form.initial['current_step']): 000000
        })
        self.auth_middleware.process_request(self.client)
        self.assertTrue(hasattr(self.client, 'user'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.user.is_authenticated)

    def test_sms_signup(self):
        self.processView(self.signup_url)
        self.assertEqual(self.client.user.username, self.user_phone)

    def test_sms_login(self):
        user = self.user_model.objects.create_user(self.user_phone)
        self.processView(self.login_url)
        self.assertEqual(self.client.user, user)
