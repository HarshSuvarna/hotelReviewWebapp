"""
URL configuration for hotelReviewWebapp project.

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
from django.urls import path
from dino import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("home/", views.home, name="home"),
    path("health-check/", views.healthCheck, name="health-check"),
    path("user-profile/", views.user_profile, name="user-profile"),
    path("giving-review/", views.giving_review, name="giving-review"),
    path("hotel-detail/", views.hotel_detail, name="hotel-detail"),
    path("hotel-info/<hotelID>", views.hotel_info, name="hotel-info"),
    path('forgot_password/', views.forgot_password, name="forgot_password"),
    path('logout/', views.logout, name='logout'),
]
