from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.http import JsonResponse
from django.contrib import messages
from django.forms import modelformset_factory
from deeva.settings import *

from .models import VotingWizard, CompareVote, RateVote
from .functions import *
from questions.models import Answer
from django.contrib.auth.models import User

from sendfile import sendfile

from questions.countries import COUNTRIES

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


def wizard_checkuser(request, wizard_id):
    if request.method == 'POST':
        print('a')
        if request.POST.get("flush_button")=="flush_button":
            print('b')
            request.session.flush()
            return HttpResponseRedirect("")

    #check if wizard exists
    try:
        wizard = VotingWizard.objects.get(pk=wizard_id)
    except VotingWizard.DoesNotExist:
        messages.error(request, 'The requested experiment does not exist. You were redirected to the homepage.')
        return redirect('experiments:index') 

    #check that user is not logged in
    if not request.user.is_authenticated:

        #check, if the user has session_keys or create them
        if hasattr(request, 'session') and not request.session.session_key:
            session_id_created = True
            request.session.save()
            request.session.modified = True
        else:
            session_id_created = False

        session_id = request.session.session_key
        #check, if the user already exists in the db and create a new one if needed
        users = User.objects.filter(username=session_id)
        if users:
            user = users[0]
        else:
            user = User.objects.create_user(username=session_id, password=None, email=None)
            user.save()

        #check number of votes for this wizard and generation
        dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all().count()
        rate_votes = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=user).count()/dependent_variables
        comp_votes = CompareVote.objects.filter(generation=wizard.generation, wizard=wizard, user=user).count()/dependent_variables



    else:
        session_id_created = None
        user = request.user
        rate_votes = 0
        comp_votes = 0


    template = 'experiments/wizard_checkuser.html'

    context = {
        'wizard':wizard,
        'session_id_created': session_id_created,
        'vote_user': user,
        'rate_votes': rate_votes,
        'comp_votes': comp_votes,

    }

    return render(request, template, context)
    

def wizard_welcome(request, wizard_id):
    from django.template import Context, Template, loader
    #check if wizard exists
    try:
        wizard = VotingWizard.objects.get(pk=wizard_id)
    except VotingWizard.DoesNotExist:
        messages.error(request, 'The requested experiment does not exist. You were redirected to the homepage.')
        return redirect('experiments:index') 

    #check that user is not logged in
    if request.user.is_authenticated: 
        messages.error(request, "(VE01) The current user is logged in and was not eligible to vote and therefore was redirected to this page.")
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #check, if user has a valid session
    if hasattr(request, 'session') and not request.session.session_key:
        messages.error(request, "(VE02) This user didn't have a valid session and was not eligible to vote and therefore was redirected to this page.")
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    session_id = request.session.session_key
    
    #check, if the user exists in the db
    users = User.objects.filter(username=session_id)
    if users:
        vote_user = users[0]
    else:
        messages.error(request, "(VE03) This session didn't have a valid user account and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #check number of votes for this wizard and generation
    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all().count()
    rate_votes = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=vote_user).count()/dependent_variables
    comp_votes = CompareVote.objects.filter(generation=wizard.generation, wizard=wizard, user=vote_user).count()/dependent_variables

    if rate_votes > 0 or comp_votes > 0:
        messages.info(request, "(VE10) This user already has votes and therefore was redirected to this page. Please check on how to continue.")
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)


    mode = request.session.get('wizard_mode', 'error')

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
    if wizard.enable_rating_mode and wizard.enable_compare_mode:
        from random import randint
        if randint(0,1) == 0:
            request.session['wizard_mode'] = 'rate'
        else:
            request.session['wizard_mode'] = 'comp'

    if wizard.enable_rating_mode:
        request.session['wizard_mode'] = 'rate'

    elif wizard.enable_compare_mode:
        request.session['wizard_mode'] = 'comp'

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

def wizard_break(request, wizard_id):
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
    if wizard.break_html == "":
        template = loader.get_template('experiments/wizard_break.html')
    else:

        from django.template import engines
        django_engine = engines['django']
        template = django_engine.from_string(wizard.break_html)

    #return page
    return HttpResponse(template.render(context, request))

def vote(request, wizard_id, had_break=False):
    wizard = get_object_or_404(VotingWizard, pk=wizard_id)

    #check, if user has a valid session
    if hasattr(request, 'session') and not request.session.session_key:
        messages.error(request, "(VE04) This user didn't have a valid session and was not eligible to vote and therefore was redirected to this page.")
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)
    
    session_id = request.session.session_key

    #check, if the user exists in the db
    users = User.objects.filter(username=session_id)
    if users:
        vote_user = users[0]
    else:
        messages.error(request, "(VE05) This session didn't have a valid user account and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    mode = request.session.get('wizard_mode', 'error')
   
    if mode == 'rate':
        rvcr = getRateVoteCountForUser(wizard, vote_user)
        #check number of votes for this wizard and generation
        dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all().count()
        rate_votes = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=vote_user).count()/dependent_variables

        print('number', rate_votes)

        #redirect to break page if needed
        if rvcr.break_needed and not had_break:
            #don't redirect to break page if there is no vote last
            if rvcr.normal_count < wizard.number_of_votes:
                return redirect('experiments:wizard_break', wizard_id=wizard.id)

        #redirect to consistency check
        if rvcr.cc_needed:
            return redirect('experiments:rate_vote', wizard_id=wizard.id)

        #redirect to vote page or personalinfos if finished
        if rvcr.normal_count < wizard.number_of_votes:
            return redirect('experiments:rate_vote', wizard_id=wizard.id)
        else:
            return redirect('experiments:wizard_personalinfos', wizard_id=wizard.id)   

    elif mode == 'comp':

        cvcr = getCompareVoteCountForUser(wizard, vote_user)
        #check number of votes for this wizard and generation
        
        #dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all().count()
        #rate_votes = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=vote_user).count()/dependent_variables

        #print('number', rate_votes)

        #redirect to break page if needed
        if cvcr.break_needed and not had_break:
            #don't redirect to break page if there is no vote last
            if cvcr.normal_count < wizard.number_of_votes:
                return redirect('experiments:wizard_break', wizard_id=wizard.id)

        #redirect to consistency check
        if cvcr.cc_needed:
            return redirect('experiments:comp_vote', wizard_id=wizard.id)

        #redirect to vote page or personalinfos if finished
        if cvcr.normal_count < wizard.number_of_votes:
            return redirect('experiments:comp_vote', wizard_id=wizard.id)
        else:
            return redirect('experiments:wizard_personalinfos', wizard_id=wizard.id)   

    else:
        pass

    


def comp_vote(request, wizard_id):
    wizard = get_object_or_404(VotingWizard, pk=wizard_id)

    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all()

    #check, if user has a valid session
    if hasattr(request, 'session') and not request.session.session_key:
        messages.error(request, "(VE06) This user didn't have a valid session and was not eligible to vote and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)
    
    session_id = request.session.session_key

    #check, if the user exists in the db
    users = User.objects.filter(username=session_id)
    if users:
        vote_user = users[0]
    else:
        messages.error(request, "(VE07) This session didn't have a valid user account and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #get individuals to vote on
    cvcr = getCompareVoteCountForUser(wizard, vote_user)

    if cvcr.cc_needed:
        print("CONSISTENCY CHECK!")
        individual1, individual2, message = getConsistencyCheckIndividualsForUser(wizard, vote_user)
    else:
        individual1, individual2, message = getRandomPairForUser(wizard, vote_user)

    if not individual1 or not individual2:
        messages.error(request, message)
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #prefill form with information relevant for storing in database
    initial = []
    for variable in dependent_variables:
        initial.append({
            'individual1':individual1,
            'individual2':individual2,
            'variable':variable,
            'consistency':cvcr.cc_needed,
        })

    #formset of seperate CompareVote forms
    CompareVoteFormSet = modelformset_factory(CompareVote, fields=(
        'individual1', 'individual2', 'vote', 'variable', 'consistency'), extra=len(initial))

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
                c_vote.user = vote_user
                c_vote.generation = wizard.generation
                c_vote.wizard = wizard
                c_vote.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})



    template = 'experiments/comp_vote.html'

    context = {
        'formset':formset,

        'wizard':wizard,
        'individual1':individual1,
        'individual2':individual2,

        'dependent_variables':dependent_variables,
    }

    return render(request, template, context)


def rate_vote(request, wizard_id, consistency=False):
    wizard = get_object_or_404(VotingWizard, pk=wizard_id)
    #old individual = wizard.generation.individuals.all().order_by('?').first() #TODO replace by special selection function
    
    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all()

    dependent_variables_ranges = wizard.generation.experiment.dependent_variables.variablerange_set.all()

    #check, if user has a valid session
    if hasattr(request, 'session') and not request.session.session_key:
        messages.error(request, "(VE06) This user didn't have a valid session and was not eligible to vote and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)
    
    session_id = request.session.session_key

    #check, if the user exists in the db
    users = User.objects.filter(username=session_id)
    if users:
        vote_user = users[0]
    else:
        messages.error(request, "(VE07) This session didn't have a valid user account and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #get individual to vote on
    rvcr = getRateVoteCountForUser(wizard, vote_user)

    if rvcr.cc_needed:
        print("CONSISTENCY CHECK!")
        individual, message = getConsistencyCheckIndividualForUser(wizard, vote_user)
    else:
        individual, message = getRandomIndividualForUser(wizard, vote_user)

    if not individual:
        messages.error(request, message)
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)


    #prefill form with information relevant for storing in database
    initial = []
    for variable in dependent_variables:
        initial.append({
            'individual':individual,
            'variable':variable,
            'consistency':rvcr.cc_needed,
        })

    #formset of seperate RateVote forms
    RateVoteFormSet = modelformset_factory(RateVote, fields=(
        'individual', 'text_value', 'int_value', 'float_value', 'variable', 'consistency'), extra=len(initial))

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
                r_vote.user = vote_user
                r_vote.generation = wizard.generation
                r_vote.wizard = wizard
                r_vote.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

            


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

    #get progress
    dependent_variables = wizard.generation.experiment.dependent_variables.attributes.all().count()
    rate_votes = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=vote_user).count()/dependent_variables



    #template = 'experiments/rate_vote.html'

    import math
    total_number = wizard.number_of_votes + math.floor(wizard.number_of_votes/wizard.consistency_check)


    percentage = int(rate_votes)*100/total_number


    progressbars = getProgressBarForUser(wizard, vote_user)

    context = {
        'formset':formset,

        'wizard':wizard,
        'individual':individual,

        'dependent_variables':dependent_variables,
        'dependent_variables_ranges': dependent_variables_ranges,
        'dependent_variables_table': dependent_variables_table,

        'current_vote': int(rate_votes+1),
        'percentage': f'{percentage:.1f}',
        'progressbars': progressbars,
        'total_votes': total_number,
    }

    print("INDIVIDUAL:",individual.id)


    #return render(request, template, context)


    from django.template import Context, Template, loader
    #check if alternative website is present
    if wizard.rate_vote_html == "":
        template = loader.get_template('experiments/rate_vote.html')
    else:

        from django.template import engines
        django_engine = engines['django']
        template = django_engine.from_string(wizard.rate_vote_html)

    #return page
    return HttpResponse(template.render(context, request))


def wizard_personalinfos(request, wizard_id):
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

    #check, if user has a valid session
    if hasattr(request, 'session') and not request.session.session_key:
        messages.error(request, "(VE08) This user didn't have a valid session and was not eligible to vote and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)
    
    session_id = request.session.session_key

    #check, if the user exists in the db
    users = User.objects.filter(username=session_id)
    if users:
        vote_user = users[0]
    else:
        messages.error(request, "(VE09) This session didn't have a valid user account and therefore was redirected to this page.") 
        return redirect('experiments:wizard_checkuser', wizard_id=wizard.id)

    #prefill form with information relevant for storing in database
    initial = []
    for question in wizard.questions.questions.all():
        initial.append({
            'question':question,
        })

    print('ini', initial)

    #formset of seperate RateVote forms
    AnswerFormSet = modelformset_factory(Answer, fields=(
        'question', 'answer',), extra=len(initial))

    print('fs', AnswerFormSet)

    #create or retrieve formset
    formset = AnswerFormSet(
        request.POST or None,
        initial = initial,
        queryset = Answer.objects.none() #Answer.objects.none() #we don't want to display database entries
    )

    if request.method == 'POST':
        if formset.is_valid():
            answers = formset.save(commit=False) #do not commit as we need to add to fields

            for answer in answers:
                answer.user = vote_user
                answer.save()

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    

    #write context
    context = {
        'wizard': wizard, 
        'currentpage': 1, 'totalpages': wizard.number_of_votes + 5,
        'formset': formset,
        'sethasquestions': wizard.questions.sethasquestion_set.all(),
        'countries' : COUNTRIES,
    }

    #check if alternative website is present
    if wizard.personalinfos_html == "":
        template = loader.get_template('experiments/wizard_personalinfos.html')
    else:

        from django.template import engines
        django_engine = engines['django']
        template = django_engine.from_string(wizard.personalinfos_html)

    #return page
    return HttpResponse(template.render(context, request))



def wizard_exit(request, wizard_id):
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
    if wizard.exit_html == "":
        template = loader.get_template('experiments/wizard_exit.html')
    else:
        template = Template(wizard.exit_html)
        context = Context(context)
    
    #return page
    return HttpResponse(template.render(context))


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

