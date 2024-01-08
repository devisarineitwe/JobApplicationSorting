from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse

from Lyamu.forms import JobForm
from Lyamu.models import Job, Candidate, Selection, Application


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
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('dashboard')  # Redirect to the dashboard or any desired page
    else:
        form = JobForm()

    return render(request, 'Lyamu/job_opening.html', {'form': form})