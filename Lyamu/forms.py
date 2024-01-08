from django import forms

from Lyamu.models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'importance_level', 'application_deadline']  # Add more fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize form widgets or add additional fields here
        pass

