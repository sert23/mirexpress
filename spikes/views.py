from django.shortcuts import render, redirect
from django.views.generic import FormView, DetailView
import string
import random
import os
from miRQC.settings import MEDIA_ROOT, MEDIA_URL, SUB_SITE, MEDIA_URL, MAIN_SITE, SPIKE_EXAMPLE, PROFILER_PATH
from django.http import JsonResponse
from newJob.forms import FileForm
import shutil
from newJob.models import Species
import subprocess
from django.urls import reverse_lazy
from datetime import datetime, timedelta
# Create your views here.


def make_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)


def make_config(req_obj):

    param_dict = req_obj.GET
    config_lines = []
    #input parameters
    study_string = param_dict.get("sra_study")
    folder = param_dict.get("jobId")
    print(folder)
    output = os.path.join(MEDIA_ROOT,folder)
    make_folder(output)
    upload_folder = os.path.join(MEDIA_ROOT, "uploaded_files", folder)
    config_lines.append("mode=spike")
    config_lines.append("output=" + output)
    if os.path.exists(upload_folder):
        files = [os.path.join(upload_folder, f) for f in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, f))]
    line = "spikeFile=" + files[0]
    config_lines.append(line)
    if study_string:
        line = "studies=" + study_string
        config_lines.append(line)
    dest_file = os.path.join(output, "config.txt")
    file_content = "\n".join(config_lines)
    with open(dest_file,"w") as cf:
        cf.write(file_content)

    return dest_file




def generate_uniq_id(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def new_rand_folder():
    is_new = True
    while is_new:
        new_id = generate_uniq_id()
        new_folder = os.path.join(MEDIA_ROOT,new_id)
        if not os.path.exists(new_folder):
            # os.mkdir(new_folder)
            # os.mkdir(os.path.join(new_folder,"uploaded"))
            # os.mkdir(os.path.join(new_folder,"query"))
            return new_id





def copy_example(request):
    path = request.path
    folder = request.GET.get('id', None)
    print(folder)
    upload_folder = os.path.join(MEDIA_ROOT, "uploaded_files", folder)
    make_folder(upload_folder)
    try:
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
    except:
        print("error")

    shutil.copy(SPIKE_EXAMPLE, os.path.join(upload_folder,"spikes.fa"))
    data = {}
    data["ok"] = "ok"
    return JsonResponse(data)


    ##############

class startNew(FormView):

    def get(self, request):
        # print(request.path[-1])
    # def get(self, request,**kwargs):
        context = {}
        jobID = new_rand_folder()
        context["jobID"] = jobID
        context["request_path"] = os.path.join(SUB_SITE,"spikes", "upload",jobID)
        context["submit_path"] = os.path.join("",jobID)
        return render(self.request, 'spikes/launch.html', context)

    def post(self, request):
        path = request.path
        folder = path.split("/")[-1]
        upload_folder = os.path.join(MEDIA_ROOT,"uploaded_files",folder)
        try:
            for filename in os.listdir(upload_folder):
                file_path = os.path.join(upload_folder, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
        except:
            print("error")
        if "file" in self.request.FILES:
            form = FileForm(request.POST, request.FILES)
            print("file in POST " + folder)
            if form.is_valid():
                print("valid form " + folder)
                ufile = form.save()
                # upload_folder = os.path.join(MEDIA_ROOT, folder, "uploaded")
                if not os.path.exists(upload_folder):
                    os.mkdir(upload_folder)

                is_new = True
                name = ufile.file.name.split("/")[-1]
                temp_path = ufile.file.name
                print(temp_path)
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

class checkStatus(FormView):

    def get(self, request):


        #first if we need to generate the config
        folder = request.GET.get('jobId', None)
        # print(request.GET)
        if not os.path.exists(os.path.join(MEDIA_ROOT,folder)):
            config_path = make_config(request)
            launch_line = "java -classpath " +PROFILER_PATH + " " + config_path
            subprocess.Popen(launch_line.split(" "))
        #     java -classpath
        # /dbs/mirexpress/java2020:/dbs/mirexpress/java2020/mariadb-java-client-1.1.7.jar miRepo.Profiler
        #  /shared/mirexpress/upload/OTIHYXFVIR0AS2C/config.txt

        context = {}
        # get folder from path
        finished = False
        context["jobID"] = folder

        return render(self.request, 'status.html', context)

        # context["result_url"] = reverse_lazy("check_status") + "/" + folder
        # context["absolute_url"] = MAIN_SITE
        # logfile = os.path.join(MEDIA_ROOT, folder, "query", "comparisons", "summaryqc.log")
        # if os.path.exists(logfile):
        #     launched = True
        # else:
        #     launched = False
        #
        # if launched:
        #     message, finished = parse_web_log(logfile)
        #     context["message"] = message
        #     if finished:
        #         # print("pos")
        #         return redirect(reverse_lazy("result_page") + "/" + folder)
        #     elif "WEB" in message:
        #         e_message = parse_error_log(logfile)
        #         context["message"] = e_message.replace("WEB: ","")
        #         return render(self.request, 'error_page.html', context)
        #
        #     else:
        #         context["last_update"] = get_last_time(logfile)
        #         # if last_update:
        #         #     context["last_upda"] = True
        #         # else:
        #         #     context["last_upda"] = False
        #         return render(self.request, 'status.html', context)
        # else:
        #     context["message"] = "Your Job is in queue"
        #     return render(self.request, 'status.html', context)
