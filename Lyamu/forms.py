from django import forms
from django.forms import formset_factory, inlineformset_factory

from Lyamu.models import Job, Education, Candidate, Application


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'importance_level', 'application_deadline', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize form widgets or add additional fields here
        pass

class EducationForm(forms.Form):
    year = forms.IntegerField(label='Year')
    institution = forms.CharField(max_length=255, label='Institution')
    qualification = forms.CharField(max_length=255, label='Qualification')