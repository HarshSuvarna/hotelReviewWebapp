from django.urls import path
from . import views

urlpatterns = [path("harsh/", views.index, name="index")]
