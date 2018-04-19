from .models import *
from django.shortcuts import get_object_or_404

from deeva.settings import *

from tempfile import NamedTemporaryFile
import shutil
import csv
import os

def check_content_filename(filename, generation):
    """Checks if the uploaded content file is valid for this generation and experiment (i.e. if the id and the content name match)
    filename -- just the filename of the uploaded file
    generation -- generation the file corresponds to
    """

    print("filename", filename)

    try:
        number, text = filename.split("-", maxsplit=1)
    except ValueError as e:
        message = "(FA04) The string could not be split into id and category name. Is there a hyphen (-) missing? Error message was: {}".format(str(e))
        return False, message

    try:
        number = int(number)
    except ValueError as e:
        message = "(FA01) The string before the first hyphen (-) could not be interpreted as id. Error message was: {}".format(str(e))
        return False, message

    print(1.5, number)    
    print(2, generation.individuals.filter(id=number))

    if not generation.individuals.filter(id=number):
        message = "(FA02)The given id is not attributed to an individual in this generation."
        return False, message

    if not text in generation.experiment.content_list():
        message = "(FA03)The text after the hyphen doesn't match any of the defined content names of this experiment."
        return False, message

    return True, None #filename is valid, no error message


def check_content_availability_generation(generation):
    """Checks if the individuals in this generation have all content files available.
    generation -- generation to check
    """
    c_ready = 0 #count individuals with all files
    c_missing = 0 #c. i. w. missing files

    c_gain = 0 #c. i. that now have all files
    c_lost = 0 #c. i. that somehow lost files

    for i in generation.individuals.all():
        ready, change = check_content_availability_individual(generation, i)
        print("ind", i.id, ready, change)
        if ready:
            c_ready += 1
        else:
            c_missing += 1
        if change > 0:
            c_gain += 1
        elif change < 0:
            c_lost += 1

    all_ready = (c_missing == 0)

    message = "{} individuals have all their content files, {} are missing at least some, {} got their content files during this check, and {} somehow lost content files.".format(c_ready, c_missing, c_gain, c_lost)

    return all_ready, message

def check_content_availability_individual(generation, individual):
    """Checks if the individual has all content files in the specified generation available.
    generation -- generation, individual is in, to check
    individual -- individual to check
    """
    all_available = True #variable to store if individual has all files

    upload_path = os.path.join(MEDIA_ROOT, MEDIA_CONTENT_FILES)

    before = individual.has_content_files

    for name in generation.experiment.content_list():
        filepath = os.path.join(upload_path, str(individual.id) + "-" + name)
        if not os.path.isfile(filepath):
            all_available = False

    after = all_available

    individual.has_content_files = after
    individual.save()

    #detect if a change happended in which direction
    if before == after:
        change = 0
    elif after == True:
        change = 1
    else:
        change = -1

    return after, change 



def handle_import_individuals_file(filename, generation_id):
    """Read the uploaded file and create or update the individuals accordingly
    filename -- complete filename of the uploaded file
    generation -- generation id of the generation the file corresponds to
    """

    messages = []
    message_id = 0

    generation = Generation.objects.get(pk=generation_id)

    variableranges = generation.experiment.independent_variables.variablerange_set.all()

    with open(filename) as csvfile:
        content_reader = csv.DictReader(csvfile)
        rows = list(content_reader)
        for row in rows:
            individual = None
            new_individual = False
            print(row)

            #retrieve given individual by id or create new one
            if row['id']:
                print('got id, try to load existing individual')
                try:
                    individual = Individual.objects.get(pk=row['id'])
                except Individual.DoesNotExist as e:
                    message = {'mid': message_id,
                                'type':'warning',
                                'text':"Tried to alter an individual which doesn't exist. Given id was {id}. Skipped line.".format(id=row['id'])}
                    messages.append(message)
                    message_id += 1
            else:
                print('got NO id, create new individual')
                new_individual = True
                individual = Individual()
                individual.save() #save to get id


            if individual is not None:
                ivvs = []
                try:
                    for vr in variableranges:
                        #get or create IndividualVariableValue object 
                        try:
                            ivv = IndividualVariableValue.objects.get(individual=individual, variable=vr.variable)
                        except IndividualVariableValue.DoesNotExist as e:
                            ivv = IndividualVariableValue()
                        
                        # check range and enter new value depending on type, but not save yet
                        ivv.individual = individual
                        ivv.variable = vr.variable
                        if vr.variable.variable_type == 'nd':
                            int_value = int(row[str(vr.variable.id)])

                            if (vr.min_value is not None)  and not (vr.min_value <= int_value):
                                raise ValueError('Given value {v} was not in range {min}-{max}.'.format(v=int_value, min=vr.min_value, max=vr.max_value))
                            if (vr.max_value is not None) and not (int_value <= vr.max_value):
                                raise ValueError('Given value {v} was not in range {min}-{max}.'.format(v=int_value, min=vr.min_value, max=vr.max_value))
                                     
                            ivv.int_value = int_value

                        elif vr.variable.variable_type == 'nc':
                            float_value = float(row[str(vr.variable.id)])

                            if (vr.min_value is not None) and not(vr.min_value <= float_value):
                                raise ValueError('Given value {v} was not in range {min}-{max}.'.format(v=float_value, min=vr.min_value, max=vr.max_value))
                            if (vr.max_value is not None) and not(float_value <= vr.max_value):
                                raise ValueError('Given value {v} was not in range {min}-{max}.'.format(v=float_value, min=vr.min_value, max=vr.max_value))
                            
                            ivv.float_value = float_value

                        else: #vr.variable.variable_type == 'ct' or vr.variable.variable_type == 'od':
                            text_value = row[str(vr.variable.id)]

                            if text_value.strip(',') not in vr.labels_list():
                                raise ValueError('Given value "{v}" was not in range "{r}".'.format(v=text_value, r=vr.labels))
                            
                            ivv.text_value = text_value

                        ivvs.append(ivv)

                    #if all ivvs were changed or created without problems, save them
                    for ivv in ivvs:
                        ivv.save()

                    #add individual to generation
                    generation.individuals.add(individual)
                        
                    message = {'mid': message_id,
                                'type':'success',
                                'text': "Created or updated individual with id '{}' without issues.".format(individual.id)}
                    messages.append(message)
                    message_id += 1
                    

                    
                except ValueError as e:
                    #There was an error while creating the ivvs. Ivvs for this individual get not saved. Display error message to user.
                    text = str(e)

                    if new_individual:
                        #This individual now doesn't have any ivvs, so delete it.
                        individual.delete()
                        text += " Also, this was a newly created individual, so we deleted it as it hasn't a complete set of values for variables."
                    else:
                        text += " This was an existing individual. Due to the error we didn't change any variable value on it."

                    message = {'mid': message_id,
                                'type':'danger',
                                'text':text}
                    messages.append(message)
                    message_id += 1

                    
                    


    return messages

def check_import_file_header(filename, generation):
    """Checks if the header contains the ids correspondingto the experiment's independant variables and rewites the first row if necessary (removing the hyphen )
    filename -- complete filename of the uploaded file
    generation -- generation the file corresponds to
    """
    tempfile = NamedTemporaryFile(mode="w", delete=False)

    with open(filename) as csvfile, tempfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        writer = csv.writer(tempfile, delimiter=',', quotechar='"')

        #read first row with ids
        list_trait_ids = next(reader)[1:]

        #convert strings to int and remove hman readable text and hyphen
        list_trait_ids = list(map(lambda x:int(x.split('-')[0]), list_trait_ids))


        #convert new header back to string
        list_trait_ids_str = list(str(x) for x in list(list_trait_ids))

        #build new header
        first_row = ["id",]
        first_row.extend(list(list_trait_ids_str))

        #write new first row
        writer.writerow(first_row)

        #write rest of the file
        for row in reader:
            writer.writerow(row)

        #check if header is correct for this generation
        variables = generation.experiment.independent_variables.variablerange_set.all().values_list('variable__id', flat=True)

        #all neded variables must be in the header we ignore other fields
        if set(variables).issubset(set(list_trait_ids)):
            result = True
        else:
            result = False

        print(list(variables), " is subset of ",  list_trait_ids, "=>", result)

    #replace old file with new file
    shutil.move(tempfile.name, filename)

    return result

def handle_import_variables_file(filename):
    """Read the uploaded file and create or update the variables accordingly
    filename -- complete filename of the uploaded file
    """

    messages = []
    message_id = 0

    with open(filename) as csvfile:
        content_reader = csv.DictReader(csvfile)
        rows = list(content_reader)
        for row in rows:
            print(row)
            #get or create IndividualVariableValue object 
            try:
                v = Variable.objects.get(name=row['name'])
            except Variable.DoesNotExist as e:
                v = Variable(name=row['name'])

            #TODO check conflicts with ranges

            #change stuff
            v.variable_type = row['type']

            if 'left' in row:
                v.left = row['left']

            if 'left_desc' in row:
                v.left_description = row['left_desc']

            if 'right' in row:
                v.right = row['right']

            if 'right_desc' in row:
                v.right_description = row['right_desc']

            #save changes
            v.save()

    print(messages)