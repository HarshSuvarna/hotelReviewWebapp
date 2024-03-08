from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
import firebase_admin
from firebase_admin import firestore, credentials
from django.contrib import messages
import firebase_admin.auth
from datetime import datetime


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
    return render(request, "base.html")


from django.shortcuts import render, redirect


# Your code to update the profile picture in Firebase storage
from django.shortcuts import redirect


def update_profile_pic(request):
    if request.method == "POST":
        pic_update = request.FILES.get("pic_update")
        uid = request.session.get("uid")
        if pic_update and uid:
            # Your code to update the profile picture in Firebase storage
            storage = firebase.storage()
            filename = f"profile_pics/{uid}/profile_picture.jpg"
            storage_url = "gs://hotel-review-app-5ade4.appspot.com"  # Your storage URL
            storage.child(filename).put(pic_update)

            # Redirect back to the user profile page after updating
            return redirect("user-profile")
        else:
            # Handle the case where either the image or the user ID is not available
            return redirect(
                "login"
            )  # Redirect to login page if user is not authenticated
    else:
        # Handle the case where the request method is not POST
        return redirect(
            "user-profile"
        )  # Redirect back to the user profile page if not a POST request


def reset_password(request):
    if request.method == "POST":
        # Get the user's email from the request
        email = request.POST.get("email")

        try:
            # Send password reset email using Firebase Authentication API
            auth.send_password_reset_email(email)
            render(request, "user_profile.html", {"reset_email_sent": True})
            request.session.clear()
            return redirect("login")
        except:
            return render(request, "user_profile.html", {"reset_failed": True})

        # Display alert message using JavaScript

    return render(request, "user_profile.html")


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user["localId"]

            # Retrieve profile picture URL from Firestore
            user_ref = db.collection("users").document(uid)
            user_data = user_ref.get().to_dict()
            profile_pic_url = user_data.get("profile_pic_url")
            print(profile_pic_url)

            # Store user ID and profile picture URL in session
            request.session["uid"] = uid
            request.session["profile_pic_url"] = profile_pic_url

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
                storage_url = (
                    "gs://hotel-review-app-5ade4.appspot.com"  # Your storage URL
                )
                storage.child(filename).put(profile_pic)

                # Get the profile picture URL
                profile_pic_url = storage.child(filename).get_url(None)

                # Add profile picture URL to user data
                user_data["profile_pic_url"] = profile_pic_url
                db.collection("users").document(uid).set(user_data, merge=True)
            else:
                print("nooooo")

            # Show message that verification email has been sent
            return render(request, "signup.html", {"verification_email_sent": True})

        except Exception as e:
            print(e)
            return render(request, "signup.html", {"error": ""})

    return render(request, "signup.html")


def test(request):
    return render(request, "test.html")


def update_profile(request):
    if request.method == "POST":
        # Get the updated username and email from the form
        username = request.POST.get("username")
        email = request.POST.get("email")
        # Update the user's data in Firebase
        uid = request.session.get("uid")
        if uid:
            user_ref = db.collection("users").document(uid)
            user_ref.update({"username": username, "email": email})

            render(request, "user_profile.html", {"profile_update_pass": True})

        else:
            render(request, "user_profile.html", {"profile_update_failed": True})

        # Redirect back to the user profile page after updating
        return redirect("user-profile")


def logout(request):
    # Clear the session
    request.session.clear()
    # Redirect to the login page
    return redirect("home")


def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            auth.send_password_reset_email(email)
            messages.success(
                request, "Password reset link has been sent to your email."
            )
            return redirect("login")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again later.")
            return redirect("forgot_password")
    else:
        return render(request, "forgot_password.html")


def home(request):
    return render(request, "home.html")



def healthCheck(request):
    return HttpResponse("Heath Check: OK")


# def user_profile(request):
#     return render(request, "user_profile.html")


def giving_review(request):
    uid = request.session.get("uid")
    if uid:
        return render(
            request,
            "giving_review.html",
            # context={"hotelID": hotelID},
        )
    else:
        return redirect("login")


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
    uid = request.session.get("uid")
    if uid:
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get().to_dict()
        profile_picture_url = user_data.get("profilePicture", None)

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
            return render(
                request, "user_profile.html ", {"error": "User profile not found."}
            )
    else:
        return redirect("login")


def add_review(request):
    uid = request.session.get("uid")
    if uid:
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get().to_dict()
        profile_picture_url = user_data.get("profilePicture", None)

    else:
        return redirect("login")


def post_user_hotel_data(request):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        visit_date = request.POST.get('visit_date')
        visit_type = request.POST.get('visit_type')
        review_title = request.POST.get('review_title')
        review_content = request.POST.get('review_content')

        # Get the user's UID from the session
        uid = request.session.get('uid')

        if uid:
            # Create a new document reference under the user's reviews subcollection
            user_ref = db.collection('users').document(uid)
            reviews_ref = user_ref.collection('reviews')

            # Get the current date and time
            review_date = datetime.now()

            # Create a dictionary to store the review data
            new_review_data = {
                'rating': rating,
                'visit_date': visit_date,
                'visit_type': visit_type,
                'review_title': review_title,
                'review_content': review_content,
                'review_date': review_date,

            }

            # Add the new review data to Firestore
            reviews_ref.add(new_review_data)

            # Redirect to a success page or any other desired action
            return redirect('user-profile')
        else:
            # Handle the case where the user is not authenticated
            return HttpResponse('User not authenticated', status=401)
    else:
        # Handle the case where the request method is not POST
        return HttpResponse('Method not allowed', status=405)

from datetime import datetime

def get_user_reviews(request):
    # Get the user's UID from the session
    uid = request.session.get('uid')

    # Check if the user is authenticated
    if uid:
        try:
            # Get a reference to the user's document
            user_ref = db.collection('users').document(uid)

            # Access the subcollection "reviews" under the user document
            reviews_ref = user_ref.collection('reviews')

            # Get all documents from the "reviews" subcollection
            reviews = reviews_ref.stream()

            # Initialize an empty list to store formatted review data
            formatted_reviews = []

            # Iterate over each review document and format its data
            for review_doc in reviews:
                review_data = review_doc.to_dict()

                # Format the datetime object into a string
                review_data['review_date'] = review_data['review_date'].strftime('%Y-%m-%d %H:%M:%S')

                formatted_reviews.append(review_data)


            # Pass the formatted review data to the template context
            return render(request, 'user_profile.html', {'reviews_data': formatted_reviews})
        except Exception as e:
            # Handle any exceptions that may occur during Firestore operation
            return HttpResponse(f'Error retrieving reviews: {str(e)}', status=500)
    else:
        # Handle the case where the user is not authenticated
        return HttpResponse('User not authenticated', status=401)
