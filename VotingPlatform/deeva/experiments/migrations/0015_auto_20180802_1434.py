# Generated by Django 2.0.2 on 2018-08-02 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0014_auto_20180801_1028'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
