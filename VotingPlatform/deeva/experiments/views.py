from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib import messages
from django.forms import modelformset_factory
from deeva.settings import *

from .models import VotingWizard, CompareVote, RateVote

from sendfile import sendfile

# Create your views here.

def index(request):
    """return the index/home/welcome page"""
    from news.functions import getNews
    newss = getNews(limit=3, short=True)
    return render(request, 'experiments/welcome.html', {'newss':newss})

def allExperiments(request):
    """return all experiments (for the user, in reality wizards) on one page"""
    from .models import VotingWizard
    wizards = VotingWizard.objects.all()
    return render(request, 'experiments/allexperiments.html', {'wizards':wizards})

def oneExperiment(request, wizard_id):
    """return one specific experiment view"""
    from .models import VotingWizard
    from .functions import getOneWizard
    try:
        wizard = getOneWizard(wizard_id)
    except VotingWizard.DoesNotExist as e:
        from django.contrib import messages
        messages.error(request, "Sorry. The requested experiment was not found.")
        return allExperiments(request)
    
    return render(request, 'experiments/oneexperiment.html', {'wizard':wizard})

def wizard_start(request, wizard_id):
    return wizard_welcome(request, wizard_id)

def wizard_welcome(request, wizard_id):
    from django.template import Context, Template, loader
    #check if wizard exists
    try:
        wizard = VotingWizard.objects.get(pk=wizard_id)
    except VotingWizard.DoesNotExist:
        messages.error(request, 'The requested experiment does not exist. You were redirected to the homepage.')
        return redirect('experiments:index')  

    #check if any mode is enabled
    if not wizard.enable_rating_mode and not wizard.enable_compare_mode:
        messages.error(request, "This experiment is currently disabled. You will not be able to complete this experiment! Sorry for the inconvenience caused.")


    #write context
    context = {'wizard': wizard, 'currentpage': 1, 'totalpages': wizard.number_of_votes + 5}

    #check if alternative website is present
    if wizard.welcome_html == "":
        template = loader.get_template('experiments/wizard_welcome.html')
    else:
        template = Template(wizard.welcome_html)
        context = Context(context)
    
    #return page
    return HttpResponse(template.render(context))

def wizard_disclaimer(request, wizard_id):
    from django.template import Context, Template, loader
    #check if wizard exists
    try:
        wizard = VotingWizard.objects.get(pk=wizard_id)
    except VotingWizard.DoesNotExist:
        messages.error(request, 'The requested experiment does not exist. You were redirected to the homepage.')
        return redirect('experiments:index')

    #check if any mode is enabled
    if not wizard.enable_rating_mode and not wizard.enable_compare_mode:
        messages.error(request, "This experiment is currently disabled. You will not be able to complete this experiment! Sorry for the inconvenience caused.")  

    #write context
    context = {'wizard': wizard, 'currentpage': 2, 'totalpages': wizard.number_of_votes + 5}

    #check if alternative website is present
    if wizard.disclaimer_html == "":
        template = loader.get_template('experiments/wizard_disclaimer.html')
    else:
        template = Template(wizard.disclaimer_html)
        context = Context(context)
    
    #return page
    return HttpResponse(template.render(context))

def wizard_example(request, wizard_id):
    from django.template import Context, Template, loader
    #check if wizard exists
    try:
        wizard = VotingWizard.objects.get(pk=wizard_id)
    except VotingWizard.DoesNotExist:
        messages.error(request, 'The requested experiment does not exist. You were redirected to the homepage.')
        return redirect('experiments:index')


    #get session key and create an anonymous user
    user = request.user

    session_id = request.session._get_or_create_session_key()
    #anonuser, created = AnonymousUser.objects.get_or_create(session_id=session_id)

    #check available modes and roll dice to see which mode is presented to the user
    if wizard.enable_rating_mode:
        request.session['wizard_mode'] = 'rate'

    #elif wizard.enable_compare_mode:
    #    request.session['wizard_mode'] = 'comp'

    else:
        messages.error(request, "This experiment is currently disabled. You will not be able to complete this experiment! Sorry for the inconvenience caused.")
        request.session['wizard_mode'] = 'error'

    #reset vote counter and voted ids
    #request.session['wizard_counter'] = 0
    #request.session['wizard_vote_ids'] = ""

    #write context
    context = {'mode': request.session.get('wizard_mode', 'error'), 'wizard': wizard, 'currentpage': 3, 'totalpages': wizard.number_of_votes + 5}

    #check if alternative website is present
    if wizard.example_html == "":
        template = loader.get_template('experiments/wizard_example.html')
    else:
        template = Template(wizard.example_html)
        context = Context(context)
    
    #return page
    return HttpResponse(template.render(context))

def vote(request, wizard_id):
    return rate_vote(request, wizard_id)


def comp_vote(request, wizard_id):
    wizard = get_object_or_404(VotingWizard, pk=wizard_id)
    individual1 = wizard.generation.individuals.all().order_by('?').first() #TODO replace by special selection function
    individual2 = wizard.generation.individuals.all().order_by('?').first() #TODO replace by special selection function

    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all()

    #prefill form with information relevant for storing in database
    initial = []
    for variable in dependent_variables:
        initial.append({
            'individual1':individual1,
            'individual2':individual2,
            'variable':variable,
        })

    #formset of seperate CompareVote forms
    CompareVoteFormSet = modelformset_factory(CompareVote, fields=(
        'individual1', 'individual2', 'vote', 'variable'), extra=len(initial))

    #create or retrieve formset
    formset = CompareVoteFormSet(
        request.POST or None,
        initial = initial,
        queryset = CompareVote.objects.none() #we don't want to display database entries
    )

    

    if request.method == 'POST':
        if formset.is_valid():
            c_votes = formset.save(commit=False) #do not commit as we need to add to fields

            for c_vote in c_votes:
                c_vote.user = request.user
                c_vote.generation = wizard.generation
                c_vote.save()

            return HttpResponse('supi') #TODO replace by json/http
        else:
            messages.error(request, 'not valid') #TODO replace by json/http



    template = 'experiments/comp_vote.html'

    context = {
        'formset':formset,

        'wizard':wizard,
        'individual1':individual1,
        'individual2':individual2,

        'dependent_variables':dependent_variables,
    }

    return render(request, template, context)


def rate_vote(request, wizard_id):
    wizard = get_object_or_404(VotingWizard, pk=wizard_id)
    individual = wizard.generation.individuals.all().order_by('?').first() #TODO replace by special selection function
    
    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all()

    dependent_variables_ranges = wizard.generation.experiment.dependent_variables.variablerange_set.all()

    #prefill form with information relevant for storing in database
    initial = []
    for variable in dependent_variables:
        initial.append({
            'individual':individual,
            'variable':variable,
        })

    #formset of seperate RateVote forms
    RateVoteFormSet = modelformset_factory(RateVote, fields=(
        'individual', 'text_value', 'int_value', 'float_value', 'variable'), extra=len(initial))

    #create or retrieve formset
    formset = RateVoteFormSet(
        request.POST or None,
        initial = initial,
        queryset = RateVote.objects.none() #we don't want to display database entries
    )

    

    if request.method == 'POST':
        if formset.is_valid():
            r_votes = formset.save(commit=False) #do not commit as we need to add to fields

            for r_vote in r_votes:
                r_vote.user = request.user
                r_vote.generation = wizard.generation
                r_vote.save()

            return HttpResponse('supi') #TODO replace by json/http
        else:
            messages.error(request, 'not valid') #TODO replace by json/http


    #create datastructure with information about variable ranges and ids to build fake-form table
    dependent_variables_table = []

    last_labels = ""

    current_group = {}

    for vr in dependent_variables_ranges:
        print("last: ", last_labels, "   current: ", vr.labels_list())
        if vr.labels_list() == last_labels:
            current_group['vrs'].append(vr)
        else:
            if current_group:
                dependent_variables_table.append(current_group)
            current_group = {}
            current_group['header'] = vr.labels_list()
            current_group['vrs'] = [vr]
        last_labels = vr.labels_list()
    dependent_variables_table.append(current_group)


    template = 'experiments/rate_vote.html'

    context = {
        'formset':formset,

        'wizard':wizard,
        'individual':individual,

        'dependent_variables':dependent_variables,

        'dependent_variables_ranges': dependent_variables_ranges,

        'dependent_variables_table': dependent_variables_table,
    }

    return render(request, template, context)


def send_individual_content(request, individual_id, content_name):
    import os
    #find images folder, create if it not exists
    upload_path = os.path.join(MEDIA_ROOT, MEDIA_CONTENT_FILES)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)

    #get specific file
    filename = f"{individual_id}-{content_name}"
    fullpath = os.path.join(upload_path, filename)


    return sendfile(request, fullpath, attachment=False)

