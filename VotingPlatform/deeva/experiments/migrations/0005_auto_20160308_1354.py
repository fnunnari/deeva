# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-08 13:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0004_auto_20160225_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individual',
            name='content_type',
            field=models.CharField(choices=[('cm', 'custom code'), ('im', 'image'), ('vi', 'video')], default='im', help_text='Select the type of content, so it will be rendered accordingly. Choose cutom code if you want to inject your own html code.', max_length=2),
        ),
    ]
