# Generated by Django 2.0.2 on 2018-08-09 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0003_question_internal_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionset',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
