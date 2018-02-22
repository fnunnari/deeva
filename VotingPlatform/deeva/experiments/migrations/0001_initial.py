# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-23 14:41
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompareVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(validators=[django.core.validators.MinValueValidator(-1), django.core.validators.MaxValueValidator(1)])),
                ('date_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Generation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nickname', models.CharField(help_text='A user-friendly, memorable name for the generation.', max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('enable_rate_retrieve', models.BooleanField(default=False, help_text='Enable search for characters based on the votes from the rating mode.')),
                ('enable_comp_retrieve', models.BooleanField(default=False, help_text='Enable search for characters based on the votes from the comparison mode.')),
                ('enable_anon_retrieve', models.BooleanField(default=False, help_text='Enable search for not registered (anonymous) users.')),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('picture', models.BooleanField(default=False)),
                ('creation_type', models.CharField(choices=[('rm', 'Random'), ('cr', 'Crossover'), ('mt', 'Mutation'), ('hm', 'Handmade')], default='rm', help_text="Change to 'Handmade' if individual is edited manually", max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='IndividualVariableValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Individual')),
            ],
            options={
                'verbose_name': 'Individual Varibale Value',
                'verbose_name_plural': 'Individual Varibale Values',
            },
        ),
        migrations.CreateModel(
            name='RateVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.TextField()),
                ('date_time', models.DateTimeField(auto_now_add=True)),
                ('generation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Generation')),
                ('individual', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Individual')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(max_length=40)),
                ('last_access', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('variable_type', models.CharField(choices=[('nd', 'numerical-discrete'), ('nc', 'numerical-continous'), ('ct', 'categorical'), ('od', 'ordinal')], default='nd', help_text='Select the type of the variable.', max_length=2)),
                ('left', models.CharField(blank=True, max_length=64)),
                ('left_description', models.TextField(blank=True)),
                ('right', models.CharField(blank=True, max_length=64)),
                ('right_description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='VariableRange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_value', models.FloatField(blank=True)),
                ('max_value', models.FloatField(blank=True)),
                ('degreecategories', models.TextField(blank=True, help_text='For ordinal type: Degrees to be shown seperated by commas. For categorical type: categories to be used seperated by commas.')),
                ('variable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Variable')),
            ],
        ),
        migrations.CreateModel(
            name='VariableSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(blank=True, help_text='A small description that describes the intention behind the set.')),
                ('attributes', models.ManyToManyField(through='experiments.VariableRange', to='experiments.Variable')),
            ],
        ),
        migrations.CreateModel(
            name='VotingWizard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', help_text='A nickname, so the wizard can be identified more easily.', max_length=128, null=True)),
                ('welcome_html', models.TextField(blank=True, null=True)),
                ('disclaimer_html', models.TextField(blank=True, null=True)),
                ('example_html', models.TextField(blank=True, null=True)),
                ('personalinfos_html', models.TextField(blank=True, null=True)),
                ('exit_html', models.TextField(blank=True, null=True)),
                ('enable_rating_mode', models.BooleanField(default=False)),
                ('enable_compare_mode', models.BooleanField(default=False)),
                ('enable_anonymous_mode', models.BooleanField(default=False, help_text='Allow not registeres (anonymous) user to vote.')),
                ('number_of_votes', models.IntegerField(default=10)),
                ('shown_on_overview_page', models.BooleanField(default=False, help_text='Determines if the wizard is advertised publically on the page.')),
                ('generation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Generation')),
            ],
        ),
        migrations.AddField(
            model_name='variablerange',
            name='variable_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.VariableSet'),
        ),
        migrations.AddField(
            model_name='ratevote',
            name='trait',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Variable'),
        ),
        migrations.AddField(
            model_name='ratevote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='individualvariablevalue',
            name='variable',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Variable'),
        ),
        migrations.AddField(
            model_name='individual',
            name='attributes',
            field=models.ManyToManyField(through='experiments.IndividualVariableValue', to='experiments.Variable'),
        ),
        migrations.AddField(
            model_name='generation',
            name='individuals',
            field=models.ManyToManyField(related_name='in_generations', to='experiments.Individual'),
        ),
        migrations.AddField(
            model_name='generation',
            name='parent',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to='experiments.Generation'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='dependant_variables',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_dependant_variables', to='experiments.VariableSet'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='independant_variables',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiment_independant_variables', to='experiments.VariableSet'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='questions',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='questions.QuestionSet'),
        ),
        migrations.AddField(
            model_name='comparevote',
            name='generation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Generation'),
        ),
        migrations.AddField(
            model_name='comparevote',
            name='individual1',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ind1', to='experiments.Individual'),
        ),
        migrations.AddField(
            model_name='comparevote',
            name='individual2',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ind2', to='experiments.Individual'),
        ),
        migrations.AddField(
            model_name='comparevote',
            name='trait',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiments.Variable'),
        ),
        migrations.AddField(
            model_name='comparevote',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
