from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, "index.html", {"message": "Welcome to Dino!"})


def healthCheck(request):
    return HttpResponse("Heath Check: OK")
