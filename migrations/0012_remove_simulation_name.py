# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-12 12:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stemp', '0011_auto_20180312_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='simulation',
            name='name',
        ),
    ]
