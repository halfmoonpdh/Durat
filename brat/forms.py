from django import forms
from django.contrib.auth.forms import UserCreationForm
from betterforms.multiform import MultiModelForm
from .models import TagingData

from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['taging_count']

class UserCreationMultiForm(MultiModelForm):
    form_classes = {
        'user': UserCreationForm,
        'profile': ProfileForm,
    }

class TagingDataForm(forms.ModelForm):
    class Meta:
        model = TagingData
        fields = ('taging_data_title', 'taging_data_detail', 'taging_data_ann')

    def __init__(self, *args, **kwargs):
        super(TagingDataForm, self).__init__(*args, **kwargs)
        self.fields['taging_data_detail'].required = False
        self.fields['taging_data_ann'].required = False

class DocumentForm(forms.Form):
    datafile = forms.FileField(
        label="Select",
        help_text='max. 10 megabytes'
    )

