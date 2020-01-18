.. image:: https://img.shields.io/pypi/v/django-otp-sms?color=blue
   :target: https://pypi.org/project/django-otp-sms/
   :alt: PyPI
.. image:: https://travis-ci.org/mp0wer/django-otp-sms.svg?branch=master
    :target: https://travis-ci.org/mp0wer/django-otp-sms

==============
django-otp-sms
==============

Django приложение для аутентификации через SMS

Установка
---------

1. Добавить "otp_sms" в ваш INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'otp_sms',
    )

2. Выполнить миграцию::

    python manage.py migrate


3. Добавить бекенд otp_sms.backends.SMSBackend в ваш AUTHENTICATION_BACKENDS::

    AUTHENTICATION_BACKENDS = (
        ...
        'otp_sms.backends.SMSBackend',
    )

4. Использовать представление otp_sms.views.SMSAuthenticationWizardView для аутентификации пользователей::

    from otp_sms.views import SMSAuthenticationWizardView

    urlpatterns = patterns('',
        ...
        url(r'^login/', SMSAuthenticationWizardView.as_view(template_name='login.html'), name='login'),
        ...
    )

5. Указать в настройках адаптер для отправки SMS (на данный момент доступны: SMSRuAdapter и ProstorAdapter)::

    OTP_SMS_ADAPTER = 'otp_sms.adapters.SMSRuAdapter'

6. Указать учетные данные для выбранного адаптера::

    OTP_SMS_AUTH = {
        'KEY': <секретный ключ для sms.ru, например>
    }

Настройки
---------

**OTP_SMS_COUNT_ATTEMPTS**
    колличество попыток для отправки SMS

**OTP_SMS_LATENCY_ATTEMPTS**
    задержка (timedelta) после использования всех попыток отправить SMS, после истечения задержки снова доступна отправка SMS

**OTP_SMS_AUTH**
    учетные данные для выбранного адаптера

**OTP_SMS_TOKEN_TEMPLATE**
    шаблон SMS, к примеру "Ваш пароль {token}"

**OTP_SMS_NOTIFY_ADMINS_ADAPTER_ERROR**
    True или False, отправлять или нет администраторам ошибки при отправке смс

**OTP_SMS_TEST_MODE**
    Используется для тестирования, если True любое значение является валидным токеном
