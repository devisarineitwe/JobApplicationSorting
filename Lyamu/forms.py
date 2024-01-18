from django import forms

from Lyamu.models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'importance_level', 'application_deadline', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can customize form widgets or add additional fields here
        pass


class ApplicationForm(forms.Form):
    resume = forms.FileField(label='Upload Resume', required=True)
    cover_letter = forms.CharField(
        label='Cover Letter',
        widget=forms.Textarea(attrs={'rows': 4}),
        required=False
    )
    # Add any other fields you want to include in the application form