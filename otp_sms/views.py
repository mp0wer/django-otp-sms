# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.utils.http import is_safe_url
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import (
    login as auth_login,
    REDIRECT_FIELD_NAME
)
from formtools.wizard.views import SessionWizardView
from .forms import SMSSendForm, SMSAuthenticationForm
from .signals import user_logged_in


class SMSAuthenticationWizardView(SessionWizardView):
    SMS_FORM_KEY = 'sms'
    AUTH_FORM_KEY = 'auth'
    redirect_field_name = REDIRECT_FIELD_NAME
    redirect_to = None
    form_list = [
        (SMS_FORM_KEY, SMSSendForm),
        (AUTH_FORM_KEY, SMSAuthenticationForm),
    ]
    create_user_if_not_exists = False

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        request.otp_sms_create_user = self.create_user_if_not_exists
        return super(SMSAuthenticationWizardView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self, step=None):
        kwargs = super(SMSAuthenticationWizardView, self).get_form_kwargs(step)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_initial_for_auth_form(self):
        sms_form_data = self.storage.get_step_data(self.SMS_FORM_KEY) or {}
        return {
            'username': sms_form_data.get('%s-number' % self.SMS_FORM_KEY)
        }

    def get_form_initial(self, step):
        initial = super(SMSAuthenticationWizardView, self).get_form_initial(step)
        if step == self.AUTH_FORM_KEY:
            initial.update(self.get_initial_for_auth_form())
        return initial

    def render_next_step(self, form, **kwargs):
        if self.steps.current == self.SMS_FORM_KEY:
            form.save()
            if form.errors:
                return self.render(form)
        return super(SMSAuthenticationWizardView, self).render_next_step(form, **kwargs)

    def render_done(self, form, **kwargs):
        user = form.get_user()
        phone = form.cleaned_data.get('username')
        auth_login(self.request, user)
        user_logged_in.send(sender=user.__class__, request=self.request, user=user, phone=phone)
        done_response = HttpResponseRedirect(self.get_redirect_to())
        self.storage.reset()
        return done_response

    def done(self, form_list, **kwargs):
        pass

    def get_redirect_to(self):
        if self.redirect_to:
            return self.redirect_to

        redirect_to = self.request.POST.get(self.redirect_field_name,
                                            self.request.GET.get(self.redirect_field_name, ''))

        if not is_safe_url(url=redirect_to, host=self.request.get_host()):
            redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

        return redirect_to