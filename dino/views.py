from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    return render(request, "index.html", {"message": "Welcome to Dino!"})

def home(request):
    return render(request, 'home.html')
def healthCheck(request):
    return HttpResponse("Heath Check: OK")

def signup(request):
    return render(request, 'signup.html')

def user_profile(request):
    return render(request, 'user_profile.html')
def giving_review(request):
    return render(request, 'giving_review.html')

def hotel_detail(request):
    return render(request, 'hotel.html')
def login(request):
    return render(request, 'login.html')