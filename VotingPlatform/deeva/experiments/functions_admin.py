from .models import *
from django.shortcuts import get_object_or_404

from tempfile import NamedTemporaryFile
import shutil
import csv

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
            print(row)
            #get given individual or create new one
            if row['id']:
                print('hab id')
                try:
                    individual = Individual.objects.get(pk=row['id'])
                except Individual.DoesNotExist as e:
                    message = {'mid': message_id,
                                'type':'warning',
                                'text':"Tried to alter an individual which doesn't exist. Given id was {id}. Skipped line.".format(id=row['id'])}
                    messages.append(message)
                    message_id += 1
            else:
                print('hab keine id')
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
                        
                        #check range and enter new value
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

                    for ivv in ivvs:
                        ivv.save()
                        
                    message = {'mid': message_id,
                                'type':'success',
                                'text': "Created or updated individual with id '{}' without issues.".format(individual.id)}
                    messages.append(message)
                    message_id += 1
                    #TODO check for missing IVVs!

                    
                except ValueError as e:
                    message = {'mid': message_id,
                                'type':'danger',
                                'text':str(e)}
                    messages.append(message)
                    message_id += 1
                    


                



            #TODO don't forget to save

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
        variables = generation.experiment.independent_variables.variablerange_set.all().values_list('id', flat=True)
        
        if set(list_trait_ids).issubset(variables):
            result = True
        else:
            result = False

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