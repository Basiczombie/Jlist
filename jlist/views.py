import datetime
import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.encoding import smart_str
from django.views.generic import ListView, CreateView, View

from .models import Jfile
from .forms import JfileForm
from wsgiref.util import FileWrapper

# Create your views here.
class JsonListView(ListView):
    model = Jfile
    template_name = 'jsonlist.html'

    def get_queryset(self):
        if not self.request.user.groups.filter(name__in=['JLIST_ADMIN']):
            return Jfile.objects.exclude(privacy='PRIVATE')
        return Jfile.objects.all()

class JsonFileUploadView(CreateView):
    model = Jfile
    form_class = JfileForm
    template_name = 'jfile_form.html'
    success_url = reverse_lazy('jlist:home')

    def form_valid(self, form):
        jfile = form.save(commit=False)
        if self.request.user.username:
            jfile.user = self.request.user.username
        else:
            jfile.user = 'anonymous'
        jfile.upload_date = datetime.datetime.now()
        jfile.save()
        return super().form_valid(form)

class JsonFileView(View):
    def get(self, request, pk):
        file_obj = Jfile.objects.filter(pk=pk).first()
        file_name = file_obj.jfile.name.split('/')[1]
        file_path = '{}/{}'.format(settings.MEDIA_ROOT, file_obj.jfile.name)
        file_wrapper = FileWrapper(open(file_path,'rb'))
        file_mimetypes = mimetypes.guess_type(file_path)

        response = HttpResponse(file_wrapper, content_type=file_mimetypes)
        response['X-Sendfile'] = file_path
        response['Content-Length'] = os.stat(file_path).st_size
        response['Content-Disposition'] = 'attachment; filename={}/'.format(smart_str(file_name))
        return response