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
    url='https://bitbucket.org/mPower/django-otp-sms',
    author='Mpower',
    author_email='mpower.public@yandex.ru',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.7',
        'django-otp',
        'django-phonenumber-field',
        'django-formtools'
    ]
)