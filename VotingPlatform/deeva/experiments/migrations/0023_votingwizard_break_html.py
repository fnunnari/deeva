# Generated by Django 2.0.2 on 2018-10-01 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0022_auto_20180918_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='votingwizard',
            name='break_html',
            field=models.TextField(blank=True, help_text='Use {% extends "experiments/wizard_break.html" %} and the following blocks: titletext, text, input, scripts', null=True),
        ),
    ]
