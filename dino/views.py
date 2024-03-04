from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import firebase_admin
from firebase_admin import firestore, credentials
from django.contrib import messages
import firebase_admin.auth


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
            # Store user ID in session
            request.session['uid'] = user['localId']
            # Redirect user to home page after successful login
            return redirect("home")
        except Exception as e:
            error_message = "Invalid email or password"
            # Pass error message in context when rendering login page
            return render(request, "login.html", {"error_message": error_message})

    # If it's a GET request, render the login page
    return render(request, "login.html", {"error_message": ""})

def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        profile_pic = request.FILES.get("profile_pic")

        # Validate password length
        if len(password) < 6:
            return render(
                request,
                "signup.html",
                {"error": "Password should be at least 6 characters"},
            )

        try:
            # Creating a user with the given email and password
            user = auth.create_user_with_email_and_password(email, password)

            # Send email verification
            auth.send_email_verification(user["idToken"])

            # Get the user ID
            uid = user["localId"]

            # Store additional user data in Cloud Firestore
            user_data = {
                "username": username,
                "email": email,
                "uid": uid,  # Use Firebase-generated UID
            }
            db.collection("users").document(uid).set(user_data)

            # Upload profile picture to Firebase Storage
            if profile_pic:
                storage = firebase.storage()
                filename = f"profile_pics/{uid}/profile_picture.jpg"
                storage_url = "gs://hotel-review-app-5ade4.appspot.com"  # Your storage URL
                storage.child(filename).put(profile_pic)

                # Get the profile picture URL
                profile_pic_url = storage.child(filename).get_url(None)

                # Add profile picture URL to user data
                user_data["profile_pic_url"] = profile_pic_url
                db.collection("users").document(uid).set(user_data, merge=True)
            else:
                print('nooooo')

            # Show message that verification email has been sent
            return render(request, "signup.html", {"verification_email_sent": True})

        except Exception as e:
            print(e)
            return render(request, "signup.html", {"error": ""})

    return render(request, "signup.html")




def logout(request):
    # Clear the session
    request.session.clear()
    # Redirect to the login page
    return redirect('home')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            auth.send_password_reset_email(email)
            messages.success(request, 'Password reset link has been sent to your email.')
            return redirect('login')
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again later.')
            return redirect('forgot_password')
    else:
        return render(request, 'forgot_password.html')


def home(request):
    # Retrieve UID from session
    uid = request.session.get('uid')
    if uid:
        # Get user data from Firestore
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get().to_dict()
        if user_data:
            username = user_data.get('username')
            # Pass username to template context
            return render(request, "home.html", {"username": username})

    # If user is not logged in or user data is not available, redirect to login page
    return redirect("login")


def healthCheck(request):
    return HttpResponse("Heath Check: OK")


# def user_profile(request):
#     return render(request, "user_profile.html")


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


def hotel_info(request, hotelID):
    hotel_doc = db.collection("hotel").document(hotelID).get()
    reviews_ref = db.collection("review").where("hotelID", "==", hotelID)
    reviews_docs = reviews_ref.stream()

    reviews = []

    for review_doc in reviews_docs:
        review = review_doc.to_dict()
        user_doc = db.collection("users").document(review["uid"]).get().to_dict()
        if user_doc:
            review["userInfo"] = user_doc
        reviews.append(review)
    if hotel_doc.exists:
        hotel_data = hotel_doc.to_dict()
        return render(
            request,
            "hotel_info.html",
            {"hotel": hotel_data, "reviews": reviews},
        )

    return render(request, "hotel_info.html", {"error": "Hotel not found"})

def user_profile(request):
    uid = request.session.get('uid')
    if uid:
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get().to_dict()
        profile_picture_url = user_data.get('profilePicture', None)

        if user_data:
            context = {
                "users": {
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                },
                "profile_picture": profile_picture_url,
            }
            return render(request, "user_profile.html", context)
        else:
            return render(request, "user_profile.html", {"error": "User profile not found."})
    else:
        return redirect("login")


