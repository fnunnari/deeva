from django.shortcuts import render

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


def vote(request, wizard_id):
    from .forms import TestForm
    form = TestForm()
    return render(request, 'experiments/vote.html', {'form':form})

