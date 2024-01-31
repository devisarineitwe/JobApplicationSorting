from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import JobForm, EducationForm
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

@login_required
def job_details(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    user = request.user

    try:
        candidate = Candidate.objects.get(user=user)
    except Candidate.DoesNotExist:
        # Redirect user to profile update page if they are not a candidate
        return redirect('update_profile')

    # Check if the user has already applied for the job
    has_applied = Application.objects.filter(job=job, candidate=candidate).exists()

    return render(request, 'Lyamu/job_details.html', {'job': job, 'candidate': candidate, 'has_applied': has_applied})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    user = request.user

    try:
        candidate = Candidate.objects.get(user=user)
    except Candidate.DoesNotExist:
        # Redirect user to profile update page if they are not a candidate
        return redirect('update_profile')

    # Check if the user has already applied for the job
    has_applied = Application.objects.filter(job=job, candidate=candidate).exists()

    if not has_applied:
        # Only allow applying if the user has not applied before
        if request.method == 'POST':
            # Process the application form submission here
            Application.objects.create(job=job, candidate=candidate, is_qualified=False)
            send_email_view('devisarineitwe2000@gmail.com', f"you have successfully applied for the {job.title} Kindly stay alert for more details")
            return redirect('application_status', job_id=job.id)

    return redirect('application_status', job_id=job.id)
@login_required
def withdraw_application(request, job_id):
    context = {}
    try:
        # Print statements for debugging
        print(f"Request user: {request.user}")
        candidate = Candidate.objects.get(user=request.user)
        print(f"Candidate user: {candidate.user}")

        job = Job.objects.get(id=job_id)
        print(f"Request job_id: {job_id}, Retrieved job_id: {job.id}")

        application = Application.objects.filter(job=job, candidate=candidate).first()

        if application:
            application.delete()
            context = {'withdrawn': True, 'job_title': job.title, 'user': request.user,
                       'candidate_user': candidate.user, 'job_id': job_id, 'retrieved_job_id': job.id}
            send_email_view('devisarineitwe2000@gmail.com',
                            f"Your application for {job.title} has been successfully withdrawn")
        else:
            context = {'withdrawn': False}
    except Candidate.DoesNotExist or Job.DoesNotExist as e:
        # Print the exception for debugging
        print(f"Exception: {e}")
        context = {'withdrawn': False}

    return render(request, "Lyamu/withdraw_application.html", context)


@login_required
def update_profile(request):
    user = request.user

    try:
        candidate = Candidate.objects.get(user=user)
    except Candidate.DoesNotExist:
        candidate = None

    if request.method == 'POST':
        # Process Candidate Form
        resume = request.FILES.get('resume')
        years_of_experience = request.POST.get('years_of_experience')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')

        if candidate:
            # Update existing candidate
            candidate.resume = resume
            candidate.years_of_experience = years_of_experience
            candidate.date_of_birth = date_of_birth
            candidate.gender = gender
            candidate.address = address
            candidate.contact_number = contact_number
            candidate.email = email
            candidate.save()
        else:
            # Create a new candidate if none exists
            Candidate.objects.create(
                user=user,
                resume=resume,
                years_of_experience=years_of_experience,
                date_of_birth=date_of_birth,
                gender=gender,
                address=address,
                contact_number=contact_number,
                email=email
            )

        # Process Education Forms
        education_form_prefix = 'education_form'
        education_form_count = int(request.POST.get(f'{education_form_prefix}-TOTAL_FORMS', 0))

        for i in range(education_form_count):
            year = request.POST.get(f'{education_form_prefix}-{i}-year')
            institution = request.POST.get(f'{education_form_prefix}-{i}-institution')
            qualification = request.POST.get(f'{education_form_prefix}-{i}-qualification')

            # Check if the education record already exists
            if candidate:
                education, created = Education.objects.get_or_create(candidate=candidate, year=year,
                                                                     institution=institution)
                education.qualification = qualification
                if year and institution and qualification:
                    # Save the education record if all fields are filled
                    education.save()
                else:
                    # Delete the education record if any field is empty
                    education.delete()
            else:
                # Create a new candidate and then save the education record
                new_candidate = Candidate.objects.create(
                    user=user,
                    resume=None,  # You may need to update this based on your requirements
                    years_of_experience=None,
                    date_of_birth=None,
                    gender=None,
                    address=None,
                    contact_number=None,
                    email=None
                )
                Education.objects.create(candidate=new_candidate, year=year, institution=institution,
                                         qualification=qualification)

        return redirect('view_profile')  # Redirect to a success page or profile view

    else:
        # Render the Candidate and Education Forms
        education_forms = Education.objects.filter(candidate=candidate)
        return render(request, 'Lyamu/update_profile.html',
                      {'candidate': candidate, 'education_forms': education_forms})



@login_required
def view_profile(request):
    user = request.user

    try:
        candidate = Candidate.objects.get(user=user)
        education_forms = Education.objects.filter(candidate=candidate)
    except Candidate.DoesNotExist:
        candidate = None
        education_forms = None

    return render(request, 'Lyamu/view_profile.html', {'user': user, 'candidate': candidate, 'education_forms': education_forms})


@login_required
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


def send_email_view(email, message):
    # Get the email address and the message from the request
    email = email
    message = message

    # Send the email using the send_mail function
    send_mail(
        subject='Notification from Lyamu',
        message=message,
        from_email=None, # Use the default from email
        recipient_list=[email], # Send to the email address
    )

    # Return a success message or redirect to another page
    return True