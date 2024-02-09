from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("health-check/", views.healthCheck, name="healthCheck"),
]
