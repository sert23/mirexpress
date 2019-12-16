from django.shortcuts import render, redirect
from django.views.generic import FormView, DetailView
import string
import random
import os
from miRQC.settings import MEDIA_ROOT, MEDIA_URL, SUB_SITE, MEDIA_URL, MAIN_SITE
from django.http import JsonResponse
from .forms import FileForm,SpeciesForm
import shutil
from .models import Species
import subprocess
from django.urls import reverse_lazy

# Create your views here.

def m():
    return Species.objects.all().order_by('sp_class', 'specie')


def make_config(req_obj):

    param_dict = req_obj.GET
    config_lines = []
    #input parameters
    sra_string = param_dict.get("sra_input")
    jobID = param_dict.get("jobId")
    print(jobID)
    print("test_config")
    dest_file = os.path.join(MEDIA_ROOT, jobID, "config.txt")
    upload_folder = os.path.join(MEDIA_ROOT, jobID, "uploaded")
    if os.path.exists(upload_folder):
        files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]
        for f in files:
            line = "input=" + f
            config_lines.append(line)
    if sra_string:
        sra_list = sra_string.split(",")
        for sra in sra_list:
            line = "input="+sra
            config_lines.append(line)
    #advanced parameters
    protocol = param_dict.get("protocol")
    species = param_dict.get("species")
    if protocol:
        line = "protocol=" + protocol
        config_lines.append(line)
    if species:
        short, assembly = species.split(",")
        config_lines.append("species="+assembly)
        config_lines.append("microRNA="+short)

    #output folder
    results_folder = os.path.join(MEDIA_ROOT, jobID, "query")
    config_lines.append("output=" + results_folder)
    config_lines.append("p=6")
    file_content = "\n".join(config_lines)
    with open(dest_file,"w") as cf:
        cf.write(file_content)

    return jobID



# def startNew(request):
#
#     context = {}
#
#     return render(request, 'index.html', {'description': "z"})

def handle_uploaded_file(f, dest):
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def generate_uniq_id(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def new_rand_folder():
    is_new = True
    while is_new:
        new_id = generate_uniq_id()
        new_folder = os.path.join(MEDIA_ROOT,new_id)
        if not os.path.exists(new_folder):
            os.mkdir(new_folder)
            os.mkdir(os.path.join(new_folder,"uploaded"))
            os.mkdir(os.path.join(new_folder,"query"))
            return new_id


class testMulti(FormView):

    def get(self, request):
        context = {}
        # return render(self.request, 'test_table.html', context)
        return render(self.request, 'test_multiQC2.html', context)


class launchJob(FormView):

    def get(self, request):
        jobID = make_config(request)
        config = os.path.join(MEDIA_ROOT, jobID, "config.txt")

        if not os.path.exists(os.path.join(MEDIA_ROOT, jobID,"query")):
            os.mkdir(os.path.join(MEDIA_ROOT, jobID,"query"))
        # os.system("touch " + os.path.join(MEDIA_ROOT, jobID,"query", "summaryqc.log"))
        launch_line = "java -classpath /opt/mirnaqcDB/java:/opt/mirnaqcDB/java/mariadb-java-client-1.1.7.jar miRNAdb.SummaryQC " + config
        print(launch_line)
        subprocess.Popen(launch_line.split(" "))
        context = {}
        # context["test"] = test
        context["redirection_url"] = reverse_lazy("check_status") + "/" + jobID
        # ?name1=value1
        return render(self.request, 'launch.html', context)

def parse_web_log(log_path):

    finished = False
    tagged = ""
    if os.path.exists(log_path):
        with open(log_path,"r") as log_file:
            for line in log_file.readlines():
                if "SUCCESS:" in line:
                    rem,keep = line.rstrip().split("SUCCESS:")
                    tagged = tagged + keep +"<br>"
                elif "ERROR:" in line:
                    tagged = tagged + line + "<br>"
                if "SUCCESS: Analysis finished" in line:
                    finished = True

        return tagged,finished
    else:
        return None,finished

class checkStatus(FormView):

    def get(self, request):
        context = {}
        path = request.path
        # get folder from path
        finished = False
        folder = path.split("/")[-1]
        context["jobID"] = folder
        context["result_url"] = reverse_lazy("check_status") + "/" + folder
        context["absolute_url"] = MAIN_SITE
        logfile = os.path.join(MEDIA_ROOT,folder,"query","summaryqc.log")
        if os.path.exists(logfile):
            launched = True
        else:
            launched = False

        if launched:
            message, finished = parse_web_log(logfile)
            context["message"] = message
            if finished:
                # print("pos")
                return redirect(reverse_lazy("result_page") + "/" + folder)
            else:
                return render(self.request, 'status.html', context)
        else:
            context["message"] = "Your Job is in queue"
            return render(self.request, 'status.html', context)


class startNew(FormView):

    def get(self, request):
    # def get(self, request,**kwargs):
        context = {}
        jobID = new_rand_folder()
        context["jobID"] = jobID
        context["request_path"] = os.path.join("upload",jobID)
        context["submit_path"] = os.path.join("",jobID)
        context["form"] = SpeciesForm
        # species = list(Species.objects.all().filter(sp_class__in=['plant','animal', 'fungi' ]).values_list("scientific",flat=True))
        species = list(Species.objects.all().filter(sp_class__in=['plant','animal' ]).values_list("scientific",flat=True))
        assemblies = list(Species.objects.all().filter(sp_class__in=['plant','animal' ]).values_list("db_ver",flat=True))
        commons = list(Species.objects.all().filter(sp_class__in=['plant','animal']).values_list("specie",flat=True))
        shorts = list(Species.objects.all().filter(sp_class__in=['plant','animal']).values_list("shortName",flat=True))
        species_dict = dict(zip(species, assemblies))
        commons_list = list(zip(species,assemblies,shorts, commons))

        commons_list.sort()
        context["species_list"] = species
        context["species_dict"] = species_dict
        context["commons_list"] = commons_list

        # print(species_dict)
        # return render(self.request, 'multiupload.html', {'file_list': onlyfiles, "request_path":path, "form": MultiURLForm })
        return render(self.request, 'index.html', context)

    def post(self, request):
        path = request.path
        folder = path.split("/")[-1]
        print("POST received " + folder)

        if "file" in self.request.FILES:
            form = FileForm(request.POST, request.FILES)
            print("file in POST " + folder)
            if form.is_valid():
                print("valid form " + folder)
                ufile = form.save()
                upload_folder = os.path.join(MEDIA_ROOT, folder, "uploaded")
                if not os.path.exists(upload_folder):
                    os.mkdir(upload_folder)

                is_new = True
                name = ufile.file.name.split("/")[-1]
                temp_path = ufile.file.name
                dest_path = os.path.join(upload_folder, name)
                if os.path.exists(dest_path):
                    is_new = False
                url = dest_path.replace(MEDIA_ROOT,MEDIA_URL)
                print(name)
                shutil.move(os.path.join(MEDIA_ROOT, ufile.file.name), dest_path)
                print(MEDIA_URL)
                data = {'is_valid': is_new, 'name': name, 'url': url}
                print(folder)
                return JsonResponse(data)
            else:
                data = {}
                data["alert"] = True
                return JsonResponse(data)