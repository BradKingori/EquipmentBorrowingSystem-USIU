"""
URL configuration for equipment_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
import equipment.views as ev
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', ev.signup, name='signup'),
    path("student/",ev.student_dashboard, name="student_dashboard" ),
    path("lecturer/",ev.lecturer_dashboard, name= "lecturer_dashboard"),
    path("hod/",ev.hod_dashboard, name= "hod_dashboard"),
    path("technician/", ev.technician_dashboard, name="technician_dashboard"),
    path('dashboard/', ev.redirect_dashboard, name='redirect_dashboard'),
    path('signup/', ev.signup, name='signup'),
    path('login/', ev.login_view, name='login'),
    #path('accounts/', include("django.contrib.auth.urls")),
    path('logout/', ev.signout, name='signout'), 
    #path('activate/<uidb64>/<token>', ev.activate, name='activate'),
]

#what is a lambda request??
