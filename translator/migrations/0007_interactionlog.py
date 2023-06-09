# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-27 19:37
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('translator', '0006_auto_20171217_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='InteractionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.CharField(choices=[('video', 'Video'), ('audio', 'Audio'), ('image', 'Imagen'), ('text', 'Texto'), ('videocall', 'Videollamada')], max_length=6)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('fromUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_logs', to=settings.AUTH_USER_MODEL)),
                ('through', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='translator.SocialNetwork')),
                ('toUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_logs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
