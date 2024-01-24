from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('create_job_opening/', views.create_job_opening, name='create_job_opening'),
    path('total_jobs_page/', views.jobs, name='jobs_page'),
    path('total_candidates_page/', views.candidates, name='candidates_page'),
    path('total_applications_page/', views.applications, name='applications_page'),
    path('total_selections_page/', views.selections, name='selections_page'),
    path('job/<int:job_id>/', views.job_details, name='job_details'),
    path('apply_job/<int:job_id>/', views.apply_job, name='apply_job'),
    path('application_status/<int:job_id>/', views.application_status, name="application_status")

]