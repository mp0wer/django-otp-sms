# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.conf.urls import url
from otp_sms import views

urlpatterns = [
    url(r'^login/$', views.SMSAuthenticationWizardView.as_view(), name='otp_sms_login'),
    url(r'^signup/$', views.SMSAuthenticationWizardView.as_view(create_user_if_not_exists=True), name='otp_sms_signup')
]
