# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2018-11-03 01:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='HardwareType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('image', models.FileField(upload_to='hw_images/')),
                ('description', models.CharField(max_length=200)),
                ('total_count', models.IntegerField(verbose_name='Items available')),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pickup_time', models.DateTimeField(blank=True, null=True)),
                ('return_time', models.DateTimeField(blank=True, null=True)),
                ('borrowed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hardware_admin_borrowing', to=settings.AUTH_USER_MODEL)),
                ('requestor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('returned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='hardware_admin_return', to=settings.AUTH_USER_MODEL)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='hardware.HardwareType')),
            ],
        ),
    ]
