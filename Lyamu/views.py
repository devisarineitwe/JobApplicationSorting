from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from Lyamu.forms import JobForm, ApplicationForm
from Lyamu.models import Job, Candidate, Selection, Application, Employer


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


def apply_job(request, job_id):
    job = Job.objects.get(pk=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            # Assuming the user is authenticated, you can access the user from the request
            user = request.user
            candidate, created = Candidate.objects.get_or_create(user=user)

            # Save the application
            application = Application.objects.create(
                job=job,
                candidate=candidate,
                # You can save additional fields from the form
            )

            # Additional logic like sending email notification to the employer can be added here

            return redirect('job_details', job_id=job_id)
    else:
        form = ApplicationForm()

    return render(request, 'Lyamu/apply_job.html', {'form': form, 'job': job})

def candidates(request):
    total_candidates = Candidate.objects.count()
    return render(request, 'Lyamu/candidates_page.html', {'total_candidates': total_candidates})


def applications(request):
    total_applications = Application.objects.count()
    return render(request, 'Lyamu/applications_page.html', {'total_applications': total_applications})


def selections(request):
    total_selections = Selection.objects.count()
    return render(request, 'Lyamu/selections_page.html', {'total_selections': total_selections})