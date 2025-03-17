from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import views
from .views import signup as signup_view  # Rename correctly -> what is this??


urlpatterns = [
    path("student/",views.student_dashboard, name="student_dashboard" ),
    path("lecturer/",views.lecturer_dashboard, name= "lecturer_dashboard"),
    path("hod/",views.hod_dashboard, name= "hod_dashboard"),
    path("technician/", views.technician_dashboard, name="technician_dashboard"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.redirect_dashboard, name='redirect_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student-dashboard'),
    path('technician-dashboard/', views.technician_dashboard, name='technician-dashboard'),
    path('lecturer-dashboard/', views.lecturer_dashboard, name='lecturer-dashboard'),
    path('signup/', signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('approve_request', views.approve_request, name="approve_request")

]
