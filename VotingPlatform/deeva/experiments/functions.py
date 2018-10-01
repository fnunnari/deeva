from .models import VotingWizard, Individual, RateVote


def getOneWizard(id):
    """Returns one specific wizard object

    id -- id of the wizard to be returned
    """

    # get wizard
    try:
        wizard = VotingWizard.objects.get(id=id)
    except VotingWizard.DoesNotExist as e:
        raise e

    return wizard


def getRandomIndividualForUser(wizard, user):
    """returns a individual to vote on in rate mode or a message why there is none

    wizard -- wizard to search individuals in
    user -- user for which individual is to be picked
    """

    # 0 Annotate each individual with number of distinct votes (a.k.a. do not count consistency votes)
    from django.db.models import Q
    from django.db import models
    from random import randint
    individuals = (
        Individual.objects
            .filter(id__in=wizard.generation.individuals.all())  # only individuals in this wizard's generation
            # .values()   #to get dict
            .annotate(cnt=models.Count("ratevote__id",
                                       distinct=True))  # number of total votes (i.e. every variable for every vote by every user) #for testing
            .annotate(ucnt=models.Count("ratevote__user",
                                        distinct=True))  # number of users per individual #this is the wanted relevant annotation!
            .annotate(vcnt=models.Count("ratevote__variable", distinct=True))  # number of voted variables  #for testing
    )

    #print('#0, count=', individuals.count())

    # for i in individuals:
    #     print(i)

    # print(individuals.query)

    if individuals.count() <= 0:
        message = '(FE.GR.01) There are no individuals in this generation.'
        return None, message

    # 1 Filter by individuals not voted by current user
    already_voted_by_user = RateVote.objects.filter(user=user).values('individual')
    individuals = individuals.exclude(id__in=already_voted_by_user)

    #print('#1, count=', individuals.count())
    # for i in individuals:
    #     print(i)

    # print(qs.query)

    if individuals.count() <= 0:
        message = '(FE.GR.02) There are no individuals left to be voted for this user.'
        return None, message

    # 2 filter to lowest (distinct) vote count number
    minimum_number = individuals.order_by('ucnt')[0].ucnt
    individuals = individuals.filter(ucnt=minimum_number)

    #print('#1, min_number=', minimum_number, ',count=', individuals.count())
    # for i in individuals:
    #     print(i)

    if individuals.count() <= 0:
        message = '(FE.GR.03) There are no individuals left to be voted for this user. This is state that should not be reachable.'
        return None, message

    # 3 select one random
    count_of_records = individuals.count()
    random_number = randint(0, count_of_records - 1)

    individual = individuals[random_number]

    #print('#3')
    #print(individual)

    return individual, None  # empty message

def getConsistencyCheckIndividualForUser(wizard, user):
    """returns an already voted individual to vote on in rate mode or a message why there is none

    wizard -- wizard to search individuals in
    user -- user for which individual is to be picked
    """

    rvs = RateVote.objects.filter(user=user, wizard=wizard, generation=wizard.generation).order_by('-date_time') #distinct together with order_by not possible
    
    number_of_vars = rvs.values('variable').distinct().count()

    if rvs.count() <= wizard.consistency_check:
        message = '(FE.GR.03) There are no individuals left to be voted for this user. This is state that should not be reachable.'
        return None, message

    #rvs = list(rvs)
    cc_rv = rvs[(wizard.consistency_check-1)*number_of_vars]

    individual = cc_rv.individual

    return individual, None  # empty message

class RateVoteCountResult():
    all_var_count = None
    normal_count = None
    consistency_count = None
    all_distinct_count = None

    cc_needed = None
    break_needed = None


def getRateVoteCountForUser(wizard, user):
    """returns various counts of votes for this user in this wizards generation and if break or consistency check are needed

    wizard -- wizard to search votes in
    user -- user for which count should be generated
    """
    
    rvs = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=user)

    rvcr = RateVoteCountResult()

    rvcr.all_var_count = rvs.count()

    rvcr.normal_count = rvs.values('individual').distinct().count()

    rvcr.consistency_count = rvs.filter(consistency=True).values('individual').distinct().count()

    rvcr.all_distinct_count = rvcr.normal_count + rvcr.consistency_count

    print("COUNT:", rvcr.all_var_count, rvcr.normal_count, rvcr.consistency_count, rvcr.all_distinct_count)

    print("wiz cc", wizard.consistency_check)
    print("wiz nc", rvcr.normal_count )

    if wizard.consistency_check > 0 and rvcr.normal_count > 0:
        print("B")
        last_vote = rvs.last()
        if not last_vote.consistency:       
            rvcr.cc_needed = (rvcr.normal_count % wizard.consistency_check) == 0 
        print(rvcr.cc_needed)

    if wizard.forced_break > 0 and rvcr.all_distinct_count > 0:
        print("A")
        rvcr.break_needed = (rvcr.all_distinct_count % wizard.forced_break) == 0
        print(rvcr.break_needed)
                
    return rvcr

