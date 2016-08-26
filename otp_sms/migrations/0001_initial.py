# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields
import otp_sms.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SMSDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', phonenumber_field.modelfields.PhoneNumberField(help_text=b'The mobile number to deliver tokens to.', max_length=128)),
                ('key', models.CharField(default=otp_sms.models.default_key, help_text=b'A random key used to generate tokens (hex-encoded).', max_length=40, validators=[otp_sms.models.key_validator])),
                ('last_t', models.BigIntegerField(default=-1, help_text=b'The t value of the latest verified token. The next token must be at a higher time step.')),
            ],
            options={
                'verbose_name': 'SMS Device',
            },
        ),
    ]
