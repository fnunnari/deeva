import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from .functions import *
from .functions_admin import *
from django.contrib.admin.views.decorators import staff_member_required
from .forms_admin import UploadForm
from deeva.settings import *



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
def upload_individuals(request, generation_id):
    """Provide and handle a form to upload new or updated individuals"""
    generation = get_object_or_404(Generation, pk=generation_id) 

    if request.method == 'POST':
            #handle form
            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():
                import os

                #find uplaod folder, create if it not exists
                upload_path = os.path.join(MEDIA_ROOT, 'uploads')
                if not os.path.exists(upload_path):
                    os.makedirs(upload_path)

                #get uploaded file
                uploadfile = request.FILES['file']

                #save it to hard disk
                uploadfile_fullname = os.path.join(upload_path, uploadfile.name)
                with open(uploadfile_fullname, 'wb+') as destination:
                    for chunk in uploadfile.chunks():
                        destination.write(chunk)

                #handle uploaded file TODO task
                check_import_file_header(uploadfile_fullname, generation)
                handle_import_individuals_file(uploadfile_fullname, generation.id)

                #redirect user to progress bar
                return redirect('experiments_admin:upload_individuals_status', generation_id=generation.id, task_id=111)

            else:
                #form filled out incorrect (file missing), redisplay
                return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

    else: #GET, display form
        form = UploadForm()
    return render(request, 'experiments/admin/admin_upload_individuals.html', {'form':form, 'generation':generation})

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
def import_variables(request):
    """Provide and handle a form to import new variables from a file"""

    if request.method == 'POST':
            #handle form
            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():
                import os

                #find uplaod folder, create if it not exists
                upload_path = os.path.join(MEDIA_ROOT, 'uploads')
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