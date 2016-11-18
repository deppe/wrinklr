# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 02:26
from __future__ import unicode_literals

from django.db import migrations, models
import wrinklr_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('wrinklr_app', '0002_auto_20160926_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='birth_date',
            field=models.CharField(default='', max_length=20, validators=[wrinklr_app.models.validate_birth_date]),
        ),
    ]
