# Generated by Django 2.0.2 on 2018-08-01 10:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiments', '0013_auto_20180322_1423'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='individual',
            options={'ordering': ['id']},
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='disclaimer_html',
            field=models.TextField(blank=True, help_text='Use {% extends "experiments/wizard_disclaimer.html" %} and the following blocks: titletext, text, input, scripts', null=True),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='enable_compare_mode',
            field=models.BooleanField(default=False, help_text='Enable paired comparison mode for this wizard.'),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='enable_rating_mode',
            field=models.BooleanField(default=False, help_text='Enable rating mode for this wizard.'),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='example_html',
            field=models.TextField(blank=True, help_text='Use {% extends "experiments/wizard_example.html" %} and the following blocks: titletext, introduction, rate_example, comp_example, nomode_example, input, scripts', null=True),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='number_of_votes',
            field=models.IntegerField(default=10, help_text='Number of votes a user has to submit.'),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='questions',
            field=models.ForeignKey(blank=True, default=None, help_text='Question set the user will be required to fill out.', null=True, on_delete=django.db.models.deletion.PROTECT, to='questions.QuestionSet'),
        ),
        migrations.AlterField(
            model_name='votingwizard',
            name='welcome_html',
            field=models.TextField(blank=True, help_text='Use {% extends "experiments/wizard_welcome.html" %} and the following blocks: titletext, noscript_warning, text, input, scripts', null=True),
        ),
    ]
