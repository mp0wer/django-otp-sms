# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
import os
from setuptools import setup, find_packages
import otp_sms

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-otp-sms',
    version=otp_sms.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Django приложение для аутентификации через sms',
    long_description=README,
    url='https://github.com/mp0wer/django-otp-sms',
    author='Mpower',
    author_email='mpower.public@yandex.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.11',
        'django-appconf>=1.0.2',
        'django-otp>=0.5',
        'django-phonenumber-field>=2.0,<3.0',
        'django-formtools>=2.2',
        'phonenumbers',
    ],
    test_suite='runtests.runtests'
)
