# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-05 14:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('translator', '0008_auto_20180113_2013'),
    ]

    operations = [
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=1)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver_priorities', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_priorities', to=settings.AUTH_USER_MODEL)),
                ('through', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='translator.SocialNetwork')),
            ],
        ),
        migrations.RemoveField(
            model_name='hassocialnetwork',
            name='priority',
        ),
        migrations.AlterUniqueTogether(
            name='preference',
            unique_together=set([('sender', 'receiver', 'through')]),
        ),
    ]