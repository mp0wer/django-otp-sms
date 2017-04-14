# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.dispatch import Signal

user_logged_in = Signal(providing_args=["request", "user", "phone"])
user_created = Signal(providing_args=["request", "user", "phone"])
