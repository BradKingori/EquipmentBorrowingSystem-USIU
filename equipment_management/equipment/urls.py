from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import views
from .views import signup as signup_view  # Rename correctly


urlpatterns = [
    path("student/",views.student_dashboard, name="student_dashboard" ),
    path("lecturer/",views.lecturer_dashboard, name= "lecturer_dashboard"),
    path("hod/",views.hod_dashboard, name= "hod_dashboard"),
    path("technician/", views.technician_dashboard, name="technician_dashboard"),
 #   path('signup/', views.signup, name='signup'),
 #   path('login/', auth_views.LoginView.as_view(template_name='equipment/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    #path('signup/', signup_view, name='signup'),
    #path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
  #  path('login/', login_view, name='login'),
    path('login/', views.login_view, name='login'),

]
