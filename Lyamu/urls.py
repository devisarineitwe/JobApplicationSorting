from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('register/', views.register_user, name='register_user'),
    path('login/', views.user_login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),  # Add the logout URL pattern
]