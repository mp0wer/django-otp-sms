# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.test import TestCase, RequestFactory
from django.test.utils import override_settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth import get_user_model
from .models import SMSDevice
from .conf import settings
from .views import SMSAuthenticationWizardView


class SMSDeviceTestCase(TestCase):
    device = None

    def setUp(self):
        self.device = SMSDevice.objects.create(number=settings.OTP_SMS_TEST_NUMBER)

    def test_generate_token(self):
        token = self.device.generate_token(deliver=False)
        self.assertTrue(self.device.verify_token(token))


@override_settings(
    OTP_SMS_TEST_MODE=True
)
class SMSAuthViewTestCase(TestCase):
    user_phone = settings.OTP_SMS_TEST_NUMBER

    def setUp(self):
        self.request_factory = RequestFactory()
        self.user_model = get_user_model()

    def processWizardView(self, view):
        session_middleware = SessionMiddleware()
        auth_middleware = AuthenticationMiddleware()

        request = self.request_factory.get('/signup')
        session_middleware.process_request(request)
        response = view(request)
        session_middleware.process_response(request, response)
        self.request_factory.cookies[settings.SESSION_COOKIE_NAME] = request.session.session_key
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)
        self.assertTrue('wizard' in response.context_data)
        self.assertTrue('management_form' in response.context_data['wizard'])

        form = response.context_data['form']
        self.assertEqual(form.errors, {})
        management_form = response.context_data['wizard']['management_form']
        self.assertEqual(management_form.initial['current_step'], SMSAuthenticationWizardView.SMS_FORM_KEY)

        request = self.request_factory.post('/signup', {
            management_form.add_prefix('current_step'): management_form.initial['current_step'],
            '{0}-number'.format(management_form.initial['current_step']): settings.OTP_SMS_TEST_NUMBER
        })
        session_middleware.process_request(request)
        response = view(request)
        session_middleware.process_response(request, response)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context_data)
        self.assertTrue('wizard' in response.context_data)
        self.assertTrue('management_form' in response.context_data['wizard'])

        form = response.context_data['form']
        self.assertEqual(form.errors, {})
        management_form = response.context_data['wizard']['management_form']
        self.assertEqual(management_form.initial['current_step'], SMSAuthenticationWizardView.AUTH_FORM_KEY)

        request = self.request_factory.post('/signup', {
            management_form.add_prefix('current_step'): management_form.initial['current_step'],
            '{0}-username'.format(management_form.initial['current_step']): form.initial['username'],
            '{0}-password'.format(management_form.initial['current_step']): 000000
        })
        session_middleware.process_request(request)
        response = view(request)
        session_middleware.process_response(request, response)
        auth_middleware.process_request(request)
        return request, response

    def test_otp_sms_login(self):
        user = self.user_model.objects.create_user(self.user_phone)
        request, response = self.processWizardView(SMSAuthenticationWizardView.as_view())
        self.assertEqual(response.status_code, 302)
        self.assertTrue(request.user.is_authenticated)
        self.assertEqual(request.user, user)

    def test_otp_sms_signup(self):
        request, response = self.processWizardView(SMSAuthenticationWizardView.as_view(create_user_if_not_exists=True))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(request.user.is_authenticated)
        self.assertEqual(request.user.username, self.user_phone)


