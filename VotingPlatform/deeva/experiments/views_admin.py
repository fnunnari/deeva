import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from questions.models import Answer
from .functions import *
from .functions_admin import *
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .forms_admin import UploadForm
from .forms_admin import IndividualsGenerationForm
from deeva.settings import *


#
# Create your views here.

@staff_member_required
def download_variables_header(request, variable_set_id):
    """Return a csv that contains the attributes for the selected variables and the according ranges"""
        
    #get Varibale set and create filename
    vs = get_object_or_404(VariableSet, id=variable_set_id)
    filename = 'VS-{id}-{name}'.format(id=vs.id, name=vs.name)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

    writer = csv.writer(response)

    writer.writerow(['id', 'name', 'type', 'min', 'max', 'labels'])

    for vr in vs.variablerange_set.all():
        v = vr.variable
        
        if v.variable_type == "nc" or v.variable_type == "nd":
            writer.writerow([v.id, v.name, v.variable_type, vr.min_value, vr.max_value, 'N/A'])
        else:
            writer.writerow([v.id, v.name, v.variable_type, 'N/A', 'N/A', vr.labels.replace(',', ';')])

    return response


@staff_member_required
def download_individuals_data(request, generation_id):
    """Return a csv that contains the individual variable value for all individuals in the selected generation"""
        
    #get generation and variables set and create filename
    g = get_object_or_404(Generation, id=generation_id)
    filename = 'GEN-{id}-{name}'.format(id=g.id, name=g.nickname)

    vs = g.experiment.independent_variables

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

    fieldnames = ['id', 'creation_type', 'has_content_files']
    variables = [] #used variables

    for vr in vs.variablerange_set.all():
        #print (vr.variable.id, vr.variable.name)
        variables.append(vr.variable)
        fieldnames.append(vr.variable.id)

    print(fieldnames)
    print(variables)

    #write header
    writer = csv.DictWriter(response, fieldnames=fieldnames)

    writer.writeheader()

    #write rows
    for i in g.individuals.all():
        print (i.id)
        d = {}
        d['id'] = i.id
        d['creation_type'] = i.creation_type
        d['has_content_files'] = i.has_content_files
        for v in variables:
            ivv = IndividualVariableValue.objects.get(individual=i, variable=v)
            if v.variable_type == 'nd': #int
                d[v.id] = ivv.int_value
            elif vr.variable.variable_type == 'nc': #float
                d[v.id] = ivv.float_value
            else: #ct or od -> text
                d[v.id] = ivv.text_value

        writer.writerow(d)

    #send cvs
    return response


@staff_member_required
def upload_individuals_status(request, generation_id, task_id):
    generation = get_object_or_404(Generation, pk=generation_id) 
    return render(request, 'experiments/admin/admin_upload_individuals_status.html', {'generation':generation, 'task_id':task_id})


@staff_member_required
def upload_individuals_status_progress(request, generation_id, task_id):
    generation = get_object_or_404(Generation, pk=generation_id) 
    import random
    n = random.uniform(0.1, 0.9)
    return JsonResponse({'value': n})


@staff_member_required
def upload_content(request, generation_id, json=False):
    """Provide and handle a form to upload content files for individuals"""
    generation = get_object_or_404(Generation, pk=generation_id) 

    form = UploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            import os

            #find images folder, create if it not exists
            upload_path = os.path.join(MEDIA_ROOT, MEDIA_CONTENT_FILES)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            #get uploaded file
            uploadfile = request.FILES['file']

            #check if the filename is correct for this generation
            result, message = check_content_filename(uploadfile.name, generation)

            if result:
                #save it to hard disk
                new_filename = uploadfile.name.lstrip("0") #remove prefix zeroes

                uploadfile_fullname = os.path.join(upload_path, new_filename)
                print(uploadfile_fullname)
                with open(uploadfile_fullname, 'wb+') as destination:
                    for chunk in uploadfile.chunks():
                        destination.write(chunk)
                text = "The file '{}' was successfully uploaded and stored.".format(new_filename)
                if json:
                    message = {'type' : 'success', 'text' : text}
                else:    
                    messages.success(request, text)
            else:
                #display error message
                text = "There was an error with the file '{}' The file was not saved. Error was: {}".format(uploadfile.name, message)
                if json:
                    message = {'type' : 'danger', 'text' : text}
                else:    
                    messages.error(request, text)
                


            print("json", json)
            print("result1", result, message)

        else:
            pass #redisplay form

    if json: #form post with jquery
        return JsonResponse(message)


    else: #normal get request

        context = {
            'form': form,
            'generation':generation,
        }

        template = 'experiments/admin/admin_upload_content.html'

        return render(request, template, context)


@staff_member_required
def generate_individuals(request, generation_id):
    """Provide and handle a form to generate new individuals"""
    generation = get_object_or_404(Generation, pk=generation_id)

    if request.method == 'POST':
        # handle form
        form = IndividualsGenerationForm(request.POST)

        if form.is_valid():
            import os

            num_individuals = form.cleaned_data['num_individuals']
            num_randomization_segments = form.cleaned_data['num_randomization_segments']

            handle_generate_individuals(num_individuals=num_individuals,
                                        random_segments=num_randomization_segments,
                                        generation=generation)

            # Redirect user to form page
            return redirect('experiments_admin:generate_individuals', generation_id=generation.id)

        else:
            # form filled out incorrect, redisplay
            return render(request, 'experiments/admin/admin_generate_individuals.html',
                          {'form': form, 'generation': generation})

    else:  # GET, display form
        form = IndividualsGenerationForm()
    return render(request, 'experiments/admin/admin_generate_individuals.html', {'form': form, 'generation': generation})


@staff_member_required
def upload_individuals(request, generation_id):
    """Provide and handle a form to upload new or updated individuals"""
    generation = get_object_or_404(Generation, pk=generation_id) 

    if request.method == 'POST':
        #handle form
        form = UploadForm(request.POST, request.FILES)

        if form.is_valid():
            import os

            #find uplaod folder, create if it not exists
            upload_path = os.path.join(MEDIA_ROOT, MEDIA_INDIVIDUALS_VARIABLES)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)

            #get uploaded file
            uploadfile = request.FILES['file']

            #save it to hard disk
            uploadfile_fullname = os.path.join(upload_path, uploadfile.name)
            with open(uploadfile_fullname, 'wb+') as destination:
                for chunk in uploadfile.chunks():
                    destination.write(chunk)

            #handle uploaded file
            try:
                valid = check_import_file_header(uploadfile_fullname, generation)
                if not valid: #header was not correct
                    messages.error(request, "(ERROR VA03) The header of the uploaded did not contain all variables needed for this experiment configuration. Please compare the header with the example table below.")
                    return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

            except Exception as e:
                messages.error(request, "(ERROR VA02) There was an error handling the uploaded file concerning the header. Error message was:\n\r {}".format(str(e)))
                return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

            try:
                results = handle_import_individuals_file(uploadfile_fullname, generation.id)
            except Exception as e:
                messages.error(request, "(ERROR VA01) There was an error handling the uploaded files content. Error message was:\n\r {}".format(str(e)))
                return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

            ##OLDredirect user to progress bar
            ##return redirect('experiments_admin:upload_individuals_status', generation_id=generation.id, task_id=111)

            #show results page
            return render(request, 'experiments/admin/admin_upload_individuals_finished.html', {'generation':generation, 'results':results})
            

        else:
            #form filled out incorrect (file missing), redisplay
            return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

    else: #GET, display form
        form = UploadForm()
    return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})
           

@staff_member_required
def import_variables(request):
    """Provide and handle a form to import new variables from a file"""

    if request.method == 'POST':
            #handle form
            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():
                import os

                #find uplaod folder, create if it not exists
                upload_path = os.path.join(MEDIA_ROOT, MEDIA_INDIVIDUALS_VARIABLES)
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                #get uploaded file
                uploadfile = request.FILES['file']

                #save it to hard disk
                uploadfile_fullname = os.path.join(upload_path, uploadfile.name)
                with open(uploadfile_fullname, 'wb+') as destination:
                    for chunk in uploadfile.chunks():
                        destination.write(chunk)

                #handle uploaded file
                #check_import_file_header(uploadfile_fullname, generation)
                handle_import_variables_file(uploadfile_fullname)

                #redirect user to admin site
                return redirect('admin:experiments_variable_changelist')

            else:
                #form filled out incorrect (file missing), redisplay
                return render(request, 'experiments/admin/admin_import_variables.html', {'form':form})

    else: #GET, display form
        form = UploadForm()
    return render(request, 'experiments/admin/admin_import_variables.html', {'form':form})



@staff_member_required
def check_content_availability(request, generation_id):
    """checks if the individuals in this generation have all their content files and updates the corresponding boolean"""

    g = get_object_or_404(Generation, pk=generation_id)

    result, message = check_content_availability_generation(g)

    if result:
        messages.success(request, message)
    else:
        messages.warning(request, message)

    #redirect user to admin site
    return redirect('admin:experiments_generation_change', generation_id)




@staff_member_required
def download_ratevotes(request, wizard_id):
    """Return a csv that contains the individual variable value for all individuals in the selected generation"""
        
    #get generation and variables set and create filename
    w = get_object_or_404(VotingWizard, id=wizard_id)
    filename = 'WIZ-{id}-{name}-RATEVOTES'.format(id=w.id, name=w.name)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

    fieldnames = ['id', 'user', 'individual', 'variable', 'text_value', 'int_value', 'float_value', 'generation', 'wizard', 'date_time']
   
    #write header
    writer = csv.DictWriter(response, fieldnames=fieldnames)

    writer.writeheader()

    #write rows
    for rv in RateVote.objects.filter(wizard=w, generation=w.generation):
        d = {}
        d['id'] = rv.id
        d['user'] = rv.user.username
        d['individual'] = rv.individual.id
        d['variable'] = rv.variable.id
        d['text_value'] = rv.text_value
        d['int_value'] = rv.int_value
        d['float_value'] = rv.float_value
        d['generation'] = rv.generation.id
        d['wizard'] = rv.wizard.id
        d['date_time'] = rv.date_time


        writer.writerow(d)

    #send cvs
    return response


@staff_member_required
def download_useranswers(request, wizard_id):
    """Return a csv that contains the answers of the personal questions from the users in the given wizard"""
        
    #get generation and variables set and create filename
    w = get_object_or_404(VotingWizard, id=wizard_id)
    filename = 'WIZ-{id}-{name}-USERANSWERS'.format(id=w.id, name=w.name)

    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

    fieldnames = ['user', 'question', 'answer', 'answered_on']
   
    #write header
    writer = csv.DictWriter(response, fieldnames=fieldnames)

    writer.writeheader()

    users = RateVote.objects.filter(wizard=w, generation=w.generation).values_list('user', flat=True)



    #write rows
    for a in Answer.objects.filter(user__in=users):
        d = {}
        d['user'] = a.user.username
        d['question'] = a.question.title
        d['answer'] = a.answer
        d['answered_on'] = a.answered_on

        writer.writerow(d)

    #send cvs
    return response

