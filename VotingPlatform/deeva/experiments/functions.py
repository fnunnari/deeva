from .models import VotingWizard

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

def importIndividualsfromFile(filename):
	pass

