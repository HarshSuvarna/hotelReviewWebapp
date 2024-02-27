from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import firebase_admin
from firebase_admin import firestore, credentials
from django.contrib import messages


### Firebase code ###########
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SERVICE_ACCOUNT_FILE = os.path.join(
    BASE_DIR,
    "firebase-credentials",
    "credentials(Do not delete).json",
)

# Initialize Firebase Admin SDK using service account key
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()


Config = {
    "apiKey": "AIzaSyDaM-jpkNxsAKf5t8ziJe9PhMgXwSCP4O8",
    "authDomain": "hotel-review-app-5ade4.firebaseapp.com",
    "projectId": "hotel-review-app-5ade4",
    "storageBucket": "hotel-review-app-5ade4.appspot.com",
    "messagingSenderId": "262584337957",
    "appId": "1:262584337957:web:39a31942360fad689721cc",
    "databaseURL": "https://dummy.firebaseio.com",
}


firebase = pyrebase.initialize_app(Config)
auth = firebase.auth()
database = firebase.database()


# HTML Rendering methods
def index(request):
    return render(request, "base.html", {"message": "Welcome to Dino!"})






def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            # Redirect user to home page after successful login
            return redirect("index")
        except Exception as e:
            error_message = "Invalid email or password"
            # Redirect user back to login page with error message
            return redirect("login", error_message=error_message)

    # If it's a GET request, render the login page
    return render(
        request, "login.html", {"error_message": request.GET.get("error_message", "")}
    )


def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")

        # Validate password length
        if len(password) < 6:
            return render(
                request,
                "signup.html",
                {"error": "Password should be at least 6 characters"},
            )

        try:
            # Get the last assigned UID
            last_uid_doc = db.collection("meta_data").document("last_uid")
            last_uid_data = last_uid_doc.get()
            if last_uid_data.exists:
                last_uid = last_uid_data.to_dict()["uid"]
            else:
                last_uid = 0  # If no last UID exists, start from 0

            # Increment the last UID to get the next UID
            next_uid = last_uid + 1

            # Creating a user with the given email and password
            user = auth.create_user_with_email_and_password(email, password)

            # Send email verification
            auth.send_email_verification(user['idToken'])

            # Get the user ID
            uid = user['localId']

            # Storing user's UID in session
            request.session["uid"] = uid

            # Store additional user data in Cloud Firestore
            user_data = {
                "username": username,
                "email": email,
                "uid": next_uid,  # Store the next UID
            }
            db.collection("users").document(str(next_uid)).set(user_data)

            # Update the last UID in the database
            last_uid_doc.set({"uid": next_uid})

            # Show message that verification email has been sent
            messages.info(request, "Verification email has been sent. Please check your inbox.")

            # Render the signup page again
            return render(request, "signup.html")
        except Exception as e:
            print(e)
            return render(request, "signup.html")

    return render(request, "signup.html")


def home(request):
    return render(request, "home.html")


def healthCheck(request):
    return HttpResponse("Heath Check: OK")


def user_profile(request):
    return render(request, "user_profile.html")


def giving_review(request):
    return render(
        request,
        "giving_review.html",
        context={"visitType": ["Business", "Couple", "Family", "Friends", "Solo"]},
    )


def hotel_detail(request):
    # Reference to the hotels collection
    hotels_ref = db.collection("hotel")

    # Query all documents in the hotels collection
    docs = hotels_ref.stream()

    # List to store hotel data
    hotels = []

    # Iterate over each document and append data to the hotels list
    for doc in docs:
        hotel_data = doc.to_dict()
        hotels.append(hotel_data)

    # Pass hotel data to the template
    return render(request, "hotel.html", {"hotels": hotels})

