from .models import VotingWizard, Individual, RateVote

def getOneWizard(id):
    """Returns one specific wizard object

    id -- id of the wizard to be returned
    """

    #get wizard
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

	#0 Annotate each individual with number of distinct votes (a.k.a. do not count consistency votes)
	from django.db.models import Q
	from django.db import models
	from random import randint
	individuals = (
	    Individual.objects
	    .filter(id__in=wizard.generation.individuals.all()) #only individuals in this wizard's generation
	    #.values()   #to get dict
	    .annotate(cnt=models.Count("ratevote__id", distinct=True)) #number of total votes (i.e. every variable for every vote by every user) #for testing
	    .annotate(ucnt=models.Count("ratevote__user", distinct=True)) #number of users per individual #this is the wanted relevant annotation!
	    .annotate(vcnt=models.Count("ratevote__variable", distinct=True)) #number of voted variables  #for testing
	)

	print('#0, count=', individuals.count())

	for i in individuals:
		print(i)

	#print(individuals.query)

	if individuals.count() <= 0:
		message = '(FE.GR.01) There are no individuals in this generation.'
		return None, message

	#1 Filter by individuals not voted by current user
	already_voted_by_user = RateVote.objects.filter(user=user).values('individual')
	individuals = individuals.exclude(id__in=already_voted_by_user)

	print('#1, count=', individuals.count())
	for i in individuals:
		print(i)

	#print(qs.query)

	if individuals.count() <= 0:
		message = '(FE.GR.02) There are no individuals left to be voted for this user.'
		return None, message


	#2 filter to lowest (distinct) vote count number
	minimum_number = individuals.order_by('ucnt')[0].ucnt
	individuals = individuals.filter(ucnt=minimum_number)


	print('#1, min_number=',minimum_number ,',count=', individuals.count())
	for i in individuals:
		print(i)

	if individuals.count() <= 0:
		message = '(FE.GR.03) There are no individuals left to be voted for this user. This is state that should not be reachable.'
		return None, message

	#3 select one random
	count_of_records = individuals.count()
	random_number = randint(0, count_of_records-1)

	individual = individuals[random_number]


	print('#3')
	print(individual)


	return individual, None #empty message








