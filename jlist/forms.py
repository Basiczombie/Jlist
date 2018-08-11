import io
import magic
import mimetypes

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Jfile

class JfileForm(forms.ModelForm):
    
    class Meta:
        model = Jfile
        fields = ('jfile','privacy')
    
    def file_mime(self, jfile):
        ext = jfile.name.split('.')[1]
        mime = magic.from_buffer(jfile.read(), mime=True)
        if mime == 'text/plain' and ext == 'json':
            return True
        return False
    
    def clean(self):
        cleaned_data = super().clean()
        jfile = cleaned_data.get('jfile')

        if jfile.size > (2**20) or not self.file_mime(jfile):
            raise forms.ValidationError(_('The File is either larger than 1mb or is not JSON format.'), code='invalid')

        return cleaned_data    