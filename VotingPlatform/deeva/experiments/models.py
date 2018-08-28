# EXPERIMENTS models

from __future__ import unicode_literals

from django.db import models
from django.forms import widgets

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe





"""" Basic Experiment Model """

#Experiment with all settings
class Experiment(models.Model):

    #basic settings
    name = models.CharField(max_length = 128)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    
    #varibale set from which the individuals are created
    independent_variables = models.ForeignKey('VariableSet', related_name='experiment_independant_variables', on_delete=models.PROTECT,
        help_text=mark_safe('The independent variables represent inputs or causes, i.e., potential reasons for variation or, in the experimental setting, the variable controlled by the experimenter. <b>This setting cannot be changed after creating a generation!</b>'))
    
    #used variable set the user votes on
    dependent_variables = models.ForeignKey('VariableSet', related_name='experiment_dependant_variables', on_delete=models.PROTECT,
        help_text=mark_safe('The dependent variables represent the output or outcome whose variation is being studied. <b>This setting cannot be changed after creating a generation!</b>'))
    
    #definition of the content needed for this experiment
    content_names = models.TextField(help_text="Type the filenames (comma seperated) including the extension of the content files the system has to look for (e.g. 'name1.ext1,name2.ext2'). The system will append the provided names to the individual's id with a hyphen inbetween (e.g. 123-name1.ext1). <b>This setting cannot be changed after creating a generation!</b>")

    def __str__(self):
        return "{}".format(self.name)

    #content names as a python list
    def content_list(self):
        return [x.strip() for x in self.content_names.split(',')]




""" Voting Wizard """

#Defines a wizard for a specific generation
class VotingWizard(models.Model):
    from django import forms
    name = models.CharField(max_length = 128, null=True, blank=True, default="", help_text="A nickname, so the wizard can be identified more easily.")
    generation = models.ForeignKey('Generation', on_delete=models.PROTECT)

    #HTML replacement texts
    welcome_html = models.TextField(null=True, blank=True, 
        help_text='Use {% extends "experiments/wizard_welcome.html" %} and the following blocks: titletext, noscript_warning, text, input, fakebutton_text (shown if js is disabled), button_text, scripts')
    disclaimer_html = models.TextField(null=True, blank=True,
        help_text='Use {% extends "experiments/wizard_disclaimer.html" %} and the following blocks: titletext, text, input, checkbox_text, button_text, scripts')
    example_html = models.TextField(null=True, blank=True,
        help_text='Use {% extends "experiments/wizard_example.html" %} and the following blocks: titletext, introduction, rate_example, comp_example, nomode_example, input, button_text, scripts')
    personalinfos_html = models.TextField(null=True, blank=True,
        help_text='Use {% extends "experiments/wizard_personalinfos.html" %} and the following blocks: titletext, text, questions, input, button_cnt, button_save, button_load, scripts')
    exit_html = models.TextField(null=True, blank=True,
        help_text='Use {% extends "experiments/wizard_exit.html" %} and the following blocks: titletext, text, scripts')

    #Enable or disable differnet voting modes
    enable_rating_mode = models.BooleanField(default=False, help_text='Enable rating mode for this wizard.')
    enable_compare_mode = models.BooleanField(default=False, help_text='TODO Enable paired comparison mode for this wizard.')
    enable_anonymous_mode = models.BooleanField(default=False, help_text='Allow not registeres (anonymous) user to vote.')

    #number of required votes
    number_of_votes = models.IntegerField(default=10, help_text='Number of votes a user has to submit.')

    #select if wizard is shown on the overview page
    shown_on_overview_page = models.BooleanField(default=False, help_text='Determines if the wizard is advertised publically on the page.')

    #questions to be answered by the user
    from questions.models import QuestionSet
    questions = models.ForeignKey(QuestionSet, default=None, null=True, blank=True, on_delete=models.PROTECT, help_text='Question set the user will be required to fill out.')

    def __str__(self):
        if self.name:
            return "{0} ({1})".format(self.name, self.generation)
        else:
            return "Wizard for {0}".format(self.generation)






""" Generations """

#A generation contains indiviuals
class Generation(models.Model):
    nickname = models.CharField(max_length = 64, help_text="A user-friendly, memorable name for the generation.")
    parent = models.ForeignKey('Generation', default=None, null=True, blank=True, on_delete=models.SET_NULL)
    experiment = models.ForeignKey('Experiment', on_delete=models.CASCADE)
    individuals = models.ManyToManyField('Individual', related_name="in_generations", blank=True)
    created = models.DateTimeField(auto_now_add=True)

    enable_rate_retrieve = models.BooleanField(default=False, help_text='Enable search for characters based on the votes from the rating mode.')
    enable_comp_retrieve = models.BooleanField(default=False, help_text='Enable search for characters based on the votes from the comparison mode.')
    enable_anon_retrieve = models.BooleanField(default=False, help_text='Enable search for not registered (anonymous) users.')

    #Return own index according to order of appearance in experiment
    def get_index(self):
        orderedlist = list(self.experiment.generation_set.order_by('id'))
        return orderedlist.index(self)

    #Get all votes in this generation
    def get_votes(self):
        votes = Vote.objects.filter(individual__in=self.individuals.all())
        return votes

    def __str__(self):
        size = self.individuals.all().count()
        if self.parent != None:
            child_of = ", child of {0}".format(self.parent.get_index())
        else:
            child_of = ""
        if self.nickname != "":
            nick = "{0} ".format(self.nickname)
        else:
            nick = ""
        
        text = "{2}(Gen {0}{1})".format(self.get_index(), child_of, nick)
        return text 
      



""" Votes """

#Votes casted in Rating mode
class RateVote(models.Model):

    #user that voted and voted individual
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    individual = models.ForeignKey('Individual', on_delete=models.PROTECT)

    #voted value and variable
    text_value = models.TextField(blank=True, null=True)
    int_value = models.IntegerField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)

    variable = models.ForeignKey('Variable', on_delete=models.PROTECT)

    #other information
    date_time = models.DateTimeField(auto_now_add=True)
    generation = models.ForeignKey('Generation', on_delete=models.PROTECT)
    wizard = models.ForeignKey('VotingWizard', on_delete=models.PROTECT)


    def clean(self):
        from django.core.exceptions import ValidationError
        if (not self.text_value) and (not self.int_value) and (not self.float_value):
            raise ValidationError("There must be at least one non-empty value!")



#Votes casted in Comparison mode
class CompareVote(models.Model):

    #user that voted and voted individuals
    from django.contrib.auth.models import User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    individual1 = models.ForeignKey('Individual', related_name='ind1', on_delete=models.PROTECT)
    individual2 = models.ForeignKey('Individual', related_name='ind2', on_delete=models.PROTECT)

    #vote and voted trait
    from django.core.validators import MinValueValidator, MaxValueValidator
    vote = models.IntegerField(validators= [MinValueValidator(-1), MaxValueValidator(1)])
    variable = models.ForeignKey('Variable', on_delete=models.PROTECT)
    
    date_time = models.DateTimeField(auto_now_add=True)
    generation = models.ForeignKey('Generation', on_delete=models.PROTECT)
    wizard = models.ForeignKey('VotingWizard', on_delete=models.PROTECT)



""" Individuals with configuration """

#An individual with a specific set of variables
class Individual(models.Model):
    #possible creation types for an individual
    RANDOM = "rm"
    CROSS = "cr"
    MUTANT = "mt"
    HANDMADE = "hm"
    CREATION_TYPE_CHOICES = ((RANDOM, "Random"), (CROSS, "Crossover"), (MUTANT, "Mutation"), (HANDMADE, "Handmade"),)

    CUSTOM = "cm"
    IMAGE = "im"
    VIDEO = "vi"
    NONE = "no"
    CONTENT_TYPE_CHOICES = ((CUSTOM, "custom code"), (IMAGE, "image"), (VIDEO, "video"), (NONE, "none"))

    variables = models.ManyToManyField('Variable', through='IndividualVariableValue')
    creation_type = models.CharField(max_length=2, choices=CREATION_TYPE_CHOICES, default=RANDOM, help_text="Change to 'Handmade' if individual is edited manually")

    #content_type = models.CharField(max_length=2, choices=CONTENT_TYPE_CHOICES, default=NONE, help_text="Select the type of content, so it will be rendered accordingly. Choose cutom code if you want to inject your own html code.")
    #categories = models.TextField(help_text="Type the names (comma seperated) of the content files the system has to look for. The system will append the provided names to the individual's id with a hyphen inbetween (e.g. 123-name).")
    #extensions = models.TextField(help_text="Type the fiel extensions (comma seperated) for the content files the system has to look for. The system will append the extensions to the name generated from the categories field (e.g. 123-name.ext).")
    has_content_files = models.BooleanField(default=False, help_text="The needed content files were stored on the server.")
    
   

    def __str__(self):
        return "Individual {0}".format(self.id)


    class Meta:
        ordering = ['id']


#Connecting model between an individual and a variable with the value the variable has for the individual
class IndividualVariableValue(models.Model):
    individual = models.ForeignKey('Individual', on_delete=models.CASCADE)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)

    text_value = models.TextField(blank=True, null=True)
    int_value = models.IntegerField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if (not self.text_value) and (not self.int_value) and (not self.float_value):
            raise ValidationError("There must be at least one non-empty value!")

    def __str__(self):
        return ""

    class Meta:
        verbose_name = "Individual Varibale Value"
        verbose_name_plural = "Individual Varibale Values"

        unique_together = ('individual', 'variable')




""" In- or Dependant Variable Sets """

#Reusable Variable Set (or 'Profile') of Variables to be used as independent or dependent varibales for experiments
class VariableSet(models.Model):
    name = models.CharField(max_length = 128)
    description = description = models.TextField(blank=True, help_text="A small description that describes the intention behind the set." )
    attributes = models.ManyToManyField('Variable', through='VariableRange')

    def __str__(self):
        return "{name}".format(name=self.name, variables=self.attributes)

#Connecting model between the variable set and the varibales with allowed min and max values or possible categories or degrees
class VariableRange(models.Model):
    from django.core.validators import MinValueValidator, MaxValueValidator
    variable_set = models.ForeignKey('VariableSet', on_delete=models.CASCADE)
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE)

    #min and max value for ordinal mode and also numerical types if used in rate mode
    min_value = models.FloatField(blank=True, null=True)
    max_value = models.FloatField(blank=True, null=True)

    #categories for categorical mode, also degrees for ordinal in rate mode
    labels = models.TextField(help_text='For ordinal type: Degrees to be shown seperated by commas. For categorical type: categories to be used seperated by commas.', blank=True)

    #labels as a python list
    def labels_list(self):
        return [x.strip() for x in self.labels.split(',')]
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if (self.min_value and self.max_value) and (self.min_value > self.max_value):
            raise ValidationError("The minimum value must be equal or less than the maximum value.")
        if len(self.labels_list()) > 0:
            if not len(self.labels_list()) == len(set(self.labels_list())):
                raise ValidationError("Having duplicates in labels/categories is not allowed.")

    def save(self, *args, **kwargs):
        self.labels = ", ".join(self.labels_list()) #get rid of whitespace for consistent look
        super().save(*args, **kwargs) 
          
    def __str__(self):
        return "{vs} - {v}".format(vs=self.variable_set, v=self.variable)


# Possible (in- or dependent) variables with their type, and left and right text, if applicable
class Variable(models.Model):
    NMDISC = "nd"
    NMCONT = "nc"
    CATEGORY = "ct"
    ORDINAL = "od"
    VARIABLE_TYPE_CHOICES = ((NMDISC, "numerical-discrete"), (NMCONT, "numerical-continous"), (CATEGORY, "categorical"),
                             (ORDINAL, "ordinal"),)

    name = models.CharField(max_length=128, unique=True)
    variable_type = models.CharField(max_length=2, choices=VARIABLE_TYPE_CHOICES, default=NMDISC,
                                     help_text="Select the type of the variable.")

    left = models.CharField(max_length=64, blank=True)
    left_description = models.TextField(blank=True)
    right = models.CharField(max_length=64, blank=True)
    right_description = models.TextField(blank=True)

    def __str__(self):
        return self.name


#
# User Profile
#


# class UserProfile(models.Model):
#     """User Profile to save additional information about a user
#     """

#     user = models.OneToOneField(User, on_delete=models.CASCADE)

#     # last anonymous session id
#     session_id = models.CharField(max_length=40, unique=True)
    
#     # last time the system was used
#     # TODO update
#     last_access = models.DateTimeField(auto_now_add=True)


# # automatically create a profile if a new user is created
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.userprofile.save()


#
# Global settings
#


class PromotedWizard(models.Model):
    """This table contains a list of Wizards which are promoted for visualization on the main page of the site.
    """
    wizard = models.ForeignKey('VotingWizard', on_delete=models.CASCADE, null=False)
