from .models import VotingWizard, Individual, RateVote, CompareVote

from .PairGenerator import PairGenerator
import random



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
    """returns various counts of votes in rate mode for this user in this wizards generation and if break or consistency check are needed

    wizard -- wizard to search votes in
    user -- user for which count should be generated
    """
    
    rvs = RateVote.objects.filter(generation=wizard.generation, wizard=wizard, user=user)

    rvcr = RateVoteCountResult()

    rvcr.all_var_count = rvs.count()

    rvcr.normal_count = rvs.values('individual').distinct().count()

    rvcr.consistency_count = rvs.filter(consistency=True).values('individual').distinct().count()

    rvcr.all_distinct_count = rvcr.normal_count + rvcr.consistency_count

    #print("COUNT:", rvcr.all_var_count, rvcr.normal_count, rvcr.consistency_count, rvcr.all_distinct_count)

    #print("wiz cc", wizard.consistency_check)
    #print("wiz nc", rvcr.normal_count )

    if wizard.consistency_check > 0 and rvcr.normal_count > 0:
        #print("B")
        last_vote = rvs.last()
        if not last_vote.consistency:       
            rvcr.cc_needed = (rvcr.normal_count % wizard.consistency_check) == 0 
        #print(rvcr.cc_needed)

    if wizard.forced_break > 0 and rvcr.all_distinct_count > 0:
        #print("A")
        rvcr.break_needed = (rvcr.all_distinct_count % wizard.forced_break) == 0
        #print(rvcr.break_needed)
                
    return rvcr


class CompareVoteCountResult():
    all_var_count = None
    normal_count = None
    consistency_count = None
    all_distinct_count = None

    cc_needed = None
    break_needed = None


def getCompareVoteCountForUser(wizard, user):
    """returns various counts of votes in comparison mode for this user in this wizards generation and if break or consistency check are needed

    wizard -- wizard to search votes in
    user -- user for which count should be generated
    """
    
    cvs = CompareVote.objects.filter(generation=wizard.generation, wizard=wizard, user=user)

    cvcr = CompareVoteCountResult()

    cvcr.all_var_count = cvs.count()

    cvcr.normal_count = cvs.values('individual1','individual2').distinct().count()

    cvcr.consistency_count = cvs.filter(consistency=True).values('individual1','individual2').distinct().count()

    cvcr.all_distinct_count = cvcr.normal_count + cvcr.consistency_count

    print("COUNT:", cvcr.all_var_count, cvcr.normal_count, cvcr.consistency_count, cvcr.all_distinct_count)

    print("wiz cc", wizard.consistency_check)
    print("wiz nc", cvcr.normal_count )

    if wizard.consistency_check > 0 and cvcr.normal_count > 0:
        print("B")
        last_vote = cvs.last()
        if not last_vote.consistency:       
            cvcr.cc_needed = (cvcr.normal_count % wizard.consistency_check) == 0 
        print(cvcr.cc_needed)

    if wizard.forced_break > 0 and cvcr.all_distinct_count > 0:
        print("A")
        cvcr.break_needed = (cvcr.all_distinct_count % wizard.forced_break) == 0
        print(cvcr.break_needed)
                
    return cvcr

def getConsistencyCheckIndividualsForUser(wizard, user):
    """returns an already voted pair to vote on in comp mode or a message why there is none

    wizard -- wizard to search individuals in
    user -- user for which pair is to be picked
    """

    cvs = CompareVote.objects.filter(user=user, wizard=wizard, generation=wizard.generation).order_by('-date_time') #distinct together with order_by not possible
    
    number_of_vars = cvs.values('variable').distinct().count()

    if cvs.count() <= wizard.consistency_check:
        message = '(FE.CCC.01) There are no individuals left to be voted for this user. This is a state that should not be reachable.'
        return None, None, message

    #rvs = list(rvs)
    cc_rv = cvs[(wizard.consistency_check-1)*number_of_vars]

    individual1 = cc_rv.individual1
    individual2 = cc_rv.individual2

    return individual1, individual2, None  # empty message

def getProgressBarForUser(wizard, user):
    """returns a dict to pass through to the website to display the current progress as bar

    wizard -- wizard to search votes in
    user -- user for which progress should be generated
    """

    import math

    rvcr = getRateVoteCountForUser(wizard, user)

    space_for_beginning = 0.02
    space_for_end = 0.02
    space_for_break = 0.01

    number_normal_votes = wizard.number_of_votes
    number_cc_votes = math.floor(number_normal_votes/wizard.consistency_check)
 
    number_all_votes = number_normal_votes + number_cc_votes

    number_breaks = math.floor(number_all_votes/wizard.forced_break)

    static_percentage = space_for_beginning + space_for_end + (space_for_break*number_breaks)
    variable_percentage = 1-static_percentage


    pbd = []

    #beginning
    bar = {
        'color': 'success',
        'size': space_for_beginning,
    }
    pbd.append(bar)

    all_votes_count = number_all_votes
    done_votes_count = rvcr.all_distinct_count
    breaks_count = number_breaks

    missing_break = False

    while all_votes_count > 0:
        #print('all_votes_count', all_votes_count)
        #print('done_votes_count', done_votes_count)
        #voting
        bar = {}
        print("avc1", all_votes_count)

        all_votes_count -= wizard.forced_break
        done_votes_count -= wizard.forced_break

        if done_votes_count > 0:
            bar = {
                'color': 'info',
                'size': (wizard.forced_break/number_all_votes)*variable_percentage,
                'count': wizard.forced_break,
                'reason': 'voted full',
            }
            pbd.append(bar)
        else:
            if (wizard.forced_break+done_votes_count) > 0:
                bar = {
                    'color': 'info',
                    'size': ((wizard.forced_break+done_votes_count)/number_all_votes)*variable_percentage,
                    'count': wizard.forced_break+done_votes_count,
                    'reason': 'voted partial',
                }
                pbd.append(bar)

            print("avc", all_votes_count)
            if all_votes_count >= 0:
                remaining = abs(done_votes_count)
            else:
                remaining = wizard.forced_break-abs(all_votes_count)-(wizard.forced_break+done_votes_count)
            
            bar = {
                'color': 'danger',
                'size': (remaining/number_all_votes)*variable_percentage,
                'count': remaining,
                'reason': 'remaining',
            }
            pbd.append(bar)
            done_votes_count = 0

        #breaks
        if all_votes_count > 1:
            if done_votes_count == 0:
                color = 'warning'
            else:
                color = 'success'
            bar = {
                'color': color,
                'size': space_for_break,
            }
            pbd.append(bar)
            breaks_count -= 1
        elif all_votes_count > 0:
            missing_break = True




    #end
    bar = {
        'color': 'warning',
        'size': space_for_end,
        
    }
    pbd.append(bar)

    if missing_break:
        bar = {
            'color': 'warning',
            'size': space_for_break/2,
        }
        pbd.append(bar)
        bar = {
            'color': 'success',
            'size': space_for_break/2,
        }
        pbd.insert(0, bar)




    
    print(pbd)
    return pbd



def getRandomPairForUser(wizard, user):
    """returns a pair to vote on in comp mode or a message why there is none

    wizard -- wizard to search pair in
    user -- user for which pair is to be picked
    """
    generation = wizard.generation

    #get maximum number of possible pairs
    pg = PairGenerator(generation.individuals.count())
    max_num_pairs = pg.getNumOfPairs()

    #annote pairs with number of votes and order them ascending (oc = occurences)
    from django.db.models import Count
    pairs_with_number = CompareVote.objects.filter(generation=generation, consistency=False).values('individual1','individual2').annotate(oc=Count('individual1')).order_by('oc')
    pairs_flat = list(CompareVote.objects.filter(generation=generation, consistency=False).values('individual1','individual2').distinct().values_list('individual1','individual2'))

    #get count of already voted pairs
    count_voted_pairs = pairs_with_number.count()

    if count_voted_pairs < max_num_pairs:
        #We're missing pairs in the database. Find a pair that is not yet voted

        #create a cached list of all individuals ordered by their pair generator number for the next step
        all_individuals_list = []

        ordered_individuals = generation.individuals.order_by('id')
        for i in ordered_individuals:
            all_individuals_list.append(i.id)

        #create a dict of all possible pairs {i1:[i2, i2, i2], i1:[i2, i2], ...}
        all_pair_list = {}

        for i in range(max_num_pairs):
            i1, i2 = pg.indexToPair(i)

            ind1 = all_individuals_list[i1]
            ind2 = all_individuals_list[i2]

            if ind1 in all_pair_list:
                all_pair_list[ind1].add(ind2)
            else:
                all_pair_list[ind1] = set([ind2])

        #remove all pairs from that dict that are already voted on
        for individual1, individual2 in pairs_flat:
            all_pair_list[individual1].remove(individual2)

        remaining_pair_list = dict((ind1, ind2) for ind1, ind2 in all_pair_list.items() if ind2)

        #get a raondom pair from the dict translate the ids into individuals and return it
        ind1 = random.sample(list(remaining_pair_list), 1)[0]
        ind2 = remaining_pair_list[ind1].pop()

        individual1 = Individual.objects.get(pk=ind1)
        individual2 = Individual.objects.get(pk=ind2)

        return individual1, individual2, None

        
    else:
        #we're not missing pairs. select the first one from the least voted and check if user already voted them
        #get lowest number of pair votes 
        number = pairs_with_number[0]['oc']

        #search for pairs with that oc until the search space runs empty
        while pairs_with_number.filter(oc=number).count() > 0:

            #get number of voted pairs with that number
            number_pairs_count = pairs_with_number.filter(oc=number).count()

            for i in range(number_pairs_count):
                test_pair = pairs_with_number[i]

                (ind1, ind2) = (test_pair['individual1'], test_pair['individual2'])

                #check if the user already voted on that pair
                votes = CompareVote.objects.filter(user=user, generation=generation,
                                            individual1__in=[ind1, ind2],
                                            individual2__in=[ind1, ind2])

                if not votes:
                    #they did not, use that pair
                    ind1 = generation.individuals.get(id=ind1)
                    ind2 = generation.individuals.get(id=ind2)

                    return ind1, ind2, None

            #search in next oc space for not voted pairs by that user
            number += 1

        #There is no pair left for that user
        message = '(FE.GRPFU.01) There are no individuals left to be voted for this user, as they already voted on all pairs.'
        return None, None, message