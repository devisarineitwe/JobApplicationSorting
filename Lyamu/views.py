from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from .forms import JobForm, CandidateForm, EducationForm, EducationFormSet
from Lyamu.models import Job, Candidate, Selection, Application, Employer, Education


# Create your views here.
def index(request):
    return render(request, "Lyamu/index.html")


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after registration
            return redirect('dashboard')  # Redirect to your home or profile page after registration
    else:
        form = UserCreationForm()

    return render(request, 'Lyamu/register.html', {'form': form})


@login_required
def dashboard(request):
    # Fetch data for the dashboard
    total_jobs = Job.objects.count()
    total_candidates = Candidate.objects.count()
    total_applications = Application.objects.count()
    total_selections = Selection.objects.count()

    context = {
        'total_jobs': total_jobs,
        'total_candidates': total_candidates,
        'total_applications': total_applications,
        'total_selections': total_selections,
    }

    return render(request, 'Lyamu/dashboard.html', context)


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('dashboard')  # Redirect to the dashboard or any desired page
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'Lyamu/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('index')  # Redirect to the index page or any desired page after logout


@login_required
def create_job_opening(request):
    try:
        employer_instance = request.user.employer
    except Employer.DoesNotExist:
        # If the logged-in user is not an employer, create an Employer instance for them
        employer_instance = Employer.objects.create(user=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)

            # Set the employer field to the logged-in user's employer
            job.employer = employer_instance

            # Save the job
            job.save()

            return redirect('dashboard')  # Redirect to the dashboard or any desired page
    else:
        form = JobForm()

    return render(request, 'Lyamu/job_opening.html', {'form': form})

@login_required
def jobs(request):
    # Retrieve the total number of jobs
    total_jobs = Job.objects.count()

    # Retrieve the list of jobs
    jobs_list = Job.objects.all()

    # Check if the user is a superuser
    is_superuser = request.user.is_superuser

    context = {
        'total_jobs': total_jobs,
        'jobs_list': jobs_list,
        'user': request.user,
        'is_superuser': is_superuser,
    }

    return render(request, 'Lyamu/jobs_page.html', context)

def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    return render(request, 'Lyamu/job_details.html', {'job': job})

def calculate_age(date_of_birth):
    today = datetime.now()
    birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

@login_required
def apply_job(request, job_id):
    # get the job object from the database
    job = Job.objects.get(id=job_id)
    # check if the user is logged in
    if request.user.is_authenticated:
        # get or create the candidate object for the user
        candidate, created = Candidate.objects.get_or_create(user=request.user)
        # if a new candidate object was created, you can set some default values for the fields
        if created:
            candidate.years_of_experience = 0
            candidate.date_of_birth = None
            candidate.gender = None
            candidate.address = None
            candidate.contact_number = None
            candidate.email = request.user.email
            candidate.save()

        # check if the candidate has already applied for the job
        if Application.objects.filter(job=job, candidate=candidate).exists():
            # redirect to a page that shows the application status
            return redirect('application_status', job_id=job_id)

        # create a candidate form instance with the candidate data
        candidate_form = CandidateForm(instance=candidate)

        # create an education formset class using the inlineformset_factory function
        EducationFormSet = inlineformset_factory(Candidate, Education, form=EducationForm, formset=EducationFormSet,
                                                 extra=1)
        # check if the candidate object is not None
        if candidate is not None:
            # create an education formset instance with the candidate's educations
            education_formset = EducationFormSet(instance=candidate)
        else:
            # create an empty education formset instance
            education_formset = EducationFormSet()

        # check if the request method is POST
        if request.method == 'POST':
            # update the candidate form and education formset with the submitted data
            candidate_form = CandidateForm(request.POST, request.FILES, instance=candidate)
            education_formset = EducationFormSet(request.POST, instance=candidate)

            # check if the forms are valid
            if candidate_form.is_valid() and education_formset.is_valid():
                # save the candidate form and education formset
                candidate_form.save()
                education_formset.save()

                # create a new application object for the job and the candidate
                application = Application(job=job, candidate=candidate)
                application.save()

                # redirect to a page that shows the application success
                return redirect('application_success', job_id=job_id)

    # render the template with the forms and the job
    return render(request, 'apply_job.html',
                  {'candidate_form': candidate_form, 'education_formset': education_formset, 'job': job})




def application_status(request, job_id):
    # get the job object from the database
    job = Job.objects.get(id=job_id)

    # check if the user is logged in and is a candidate
    if request.user.is_authenticated and hasattr(request.user, 'candidate'):
        # get the candidate object from the database
        candidate = request.user.candidate

        # check if the candidate has applied for the job
        if Application.objects.filter(job=job, candidate=candidate).exists():
            # get the application object from the database
            application = Application.objects.get(job=job, candidate=candidate)

            # check if the candidate has been selected for the job
            if Selection.objects.filter(job=job, candidate=candidate).exists():
                # get the selection object from the database
                selection = Selection.objects.get(job=job, candidate=candidate)

                # render the template with the job, application, and selection details
                return render(request, 'Lyamu/application_status.html', {'job': job, 'application': application, 'selection': selection})

            # if the candidate has not been selected, render the template with the job and application details
            else:
                return render(request, 'Lyamu/application_status.html', {'job': job, 'application': application})

        # if the candidate has not applied for the job, redirect to the apply job page
        else:
            return redirect('apply_job', job_id=job_id)

    # if the user is not logged in or is not a candidate, redirect to the login page
    else:
        return redirect('login')

def applications(request):
    total_applications = Application.objects.count()
    return render(request, 'Lyamu/applications_page.html', {'total_applications': total_applications})


def selections(request):
    total_selections = Selection.objects.count()
    return render(request, 'Lyamu/selections_page.html', {'total_selections': total_selections})

def candidates(request):
    total_candidates = Candidate.objects.count()
    return render(request, "Lyamu/candidates_page.html", {'total_candidates': total_candidates})