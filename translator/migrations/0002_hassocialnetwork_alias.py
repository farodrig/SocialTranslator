# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-20 13:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translator', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hassocialnetwork',
            name='alias',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
