from django import forms
from django.forms import  formset_factory

from Lyamu.models import Job, Education, Candidate


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'importance_level', 'application_deadline', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize form widgets or add additional fields here
        pass

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['resume', 'years_of_experience', 'date_of_birth', 'gender', 'address', 'contact_number', 'email']
        labels = {
            'resume': 'Upload your resume',
            'years_of_experience': 'How many years of experience do you have?',
            'date_of_birth': 'Enter your date of birth (YYYY-MM-DD)',
            'gender': 'Select your gender',
            'address': 'Enter your address',
            'contact_number': 'Enter your contact number',
            'email': 'Enter your email address',
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['year', 'institution', 'qualification']
        labels = {
            'year': 'Enter the year of completion',
            'institution': 'Enter the name of the institution',
            'qualification': 'Enter the qualification obtained',
        }

class EducationFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_delete = False # prevent deleting existing educations
        self.extra = 1 # allow adding one more education at a time