# yourapp/models.py

from django.db import models
from django.contrib.auth.models import User


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any other employer-related fields as needed.

    def __str__(self):
        return self.user.username


class Job(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    importance_level = models.IntegerField()
    application_deadline = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    # Add any other job-related fields as needed.

    def __str__(self):
        return self.title


class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    applied_jobs = models.ManyToManyField(Job, through='Application')
    # Add any other candidate-related fields as needed.

    def __str__(self):
        return self.user.username


class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    is_qualified = models.BooleanField(default=False)
    # Add any other application-related fields as needed.

    def __str__(self):
        return f"{self.candidate.user.username} applied for {self.job.title}"


class Selection(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    selection_order = models.IntegerField()
    # Add any other selection-related fields as needed.

    def __str__(self):
        return f"{self.candidate.user.username} selected for {self.job.title} (Order: {self.selection_order})"

class Notification(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    # Add any other notification-related fields as needed.

    def __str__(self):
        return f"Notification for {self.candidate.user.username}"
