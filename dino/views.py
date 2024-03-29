import firebase_admin
from firebase_admin import firestore, credentials
from django.contrib import messages
import firebase_admin.auth
from datetime import datetime
import pytz
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyrebase
from firebase_admin import firestore
from django.contrib import messages
import json
from requests.exceptions import HTTPError
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth


# helper function
# Function to parse the Firestore timestamp
def parse_firestore_timestamp(timestamp):
    # Assuming the timestamp format is: "March 13, 2024 at 11:35:46 PM UTC"
    return datetime.strptime(timestamp, "%B %d, %Y at %I:%M:%S %p UTC").replace(
        tzinfo=pytz.UTC
    )


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


def index(request):
    return redirect("home")


def hotel_detail(request):
    return render(request, "base.html")


def About(request):
    return render(request, "About.html")


def latest_reviews(request):
    reviews_ref = db.collection("review").order_by(
        "review_date", direction=firestore.Query.DESCENDING
    )
    reviews_docs = reviews_ref.stream()

    reviews = []
    for review_doc in reviews_docs:
        review = review_doc.to_dict()
        review_date = review.get("review_date")
        if review_date:
            # Format the Firestore Timestamp to a human-readable date-time string.
            # Adjust the format as per your requirement.
            review["review_date"] = review_date.strftime("%B %d, %Y at %H:%M %p")

        user_ref = db.collection("users").document(review["uid"])
        user_doc = user_ref.get()
        if user_doc.exists:
            user_info = user_doc.to_dict()
            # Include the user's name with the review information.
            review["user_name"] = user_info.get(
                "username", "A user"
            )  # Assuming the user's name is stored under 'name'.

        reviews.append(review)

    if reviews:
        context = {"reviews": reviews}
    else:
        context = {
            "reviews": None,
            "message": "There seems to be no reviews. Visit your account or hotels page to add some!.",
        }

    return render(request, "latest_reviews.html", context)


def update_profile_pic(request):
    if request.method == "POST":
        pic_update = request.FILES.get("pic_update")
        uid = request.session.get("uid")
        if pic_update and uid:
            storage = firebase.storage()
            filename = f"profile_pics/{uid}/profile_picture.jpg"
            # Upload the image to Firebase Storage
            storage.child(filename).put(pic_update)

            # Get the URL of the uploaded image
            profile_pic_url = storage.child(filename).get_url(None)

            # Update session variable
            request.session["profile_pic_url"] = profile_pic_url

            # Update Firestore document
            user_ref = db.collection("users").document(uid)
            user_ref.update({"profile_pic_url": profile_pic_url})
        return redirect("user-profile")
    else:
        return redirect("user-profile")


def admin(request):
    uid = request.session.get("uid")
    if uid and request.session["is_admin"]:
        hotel_ref = db.collection("hotel")
        hotels = []
        for hotel in hotel_ref.stream():
            hotel_data = hotel.to_dict()
            hotels.append(hotel_data)
        return render(request, "admin.html", {"hotels": hotels})

    else:
        return redirect("home")


def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            # Send password reset email using Firebase Authentication API
            auth.send_password_reset_email(email)
            # messages.success(request, "A password reset link has been sent to your email.")

            # Clear session data
            request.session.clear()
            return redirect("login")

        except Exception as e:
            messages.error(
                request, "Failed to send password reset email. Please try again."
            )
            return render(request, "user_profile.html", {"reset_failed": True})

    # If it's not a POST request or some other condition, just render the profile page again
    return render(request, "user_profile.html")


def login(request):
    # Clear session data at the beginning
    request.session.flush()

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            uid = user["localId"]

            # Retrieve profile picture URL from Firestore
            user_ref = db.collection("users").document(uid)
            user_data = user_ref.get().to_dict()
            profile_pic_url = user_data.get("profile_pic_url")

            # Store user ID and profile picture URL in session
            request.session["uid"] = uid
            if user_data["role"] and user_data["role"] == "admin":
                request.session["is_admin"] = True
            else:
                request.session["is_admin"] = False
            request.session["profile_pic_url"] = profile_pic_url

            # Redirect user to home page after successful login
            return redirect("home")
        except HTTPError as e:
            error_message = (
                "Login failed. Check your credentials or verify your email if not done!"
            )
            print("HTTPError:", error_message)
            return render(request, "login.html", {"error_message": error_message})
        except Exception as e:
            error_message = "An unexpected error occurred. Please try again later."
            print("Exception:", e)
            return render(request, "login.html", {"error_message": error_message})

    # If it's a GET request, render the login page without an error message
    return render(request, "login.html", {"error_message": None})


def signup(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        profile_pic = request.FILES.get("profile_pic")

        try:
            # Creating a user with the given email and password
            user = auth.create_user_with_email_and_password(email, password)

            # Get the user ID
            uid = user["localId"]

            # Store additional user data in Cloud Firestore
            user_data = {
                "username": username,
                "email": email,
                "uid": uid,
                "role": "user",
            }
            db.collection("users").document(uid).set(user_data)

            # Upload profile picture to Firebase Storage
            if profile_pic:
                storage = firebase.storage()
                filename = f"profile_pics/{uid}/profile_picture.jpg"
                storage.child(filename).put(profile_pic)

                # Get the profile picture URL
                profile_pic_url = storage.child(filename).get_url(None)

                # Update user data with profile picture URL
                db.collection("users").document(uid).update(
                    {"profile_pic_url": profile_pic_url}
                )

            return render(
                request,
                "signup.html",
                {
                    "message": "Account created successfully.Click on login from this form or homepage"
                },
            )

        except HTTPError as e:
            error_json = e.args[1]
            error_data = json.loads(error_json)["error"]
            error_message = "An error occurred during signup: " + error_data["message"]

            return render(request, "signup.html", {"error_message": error_message})

        except Exception as e:
            error_message = "An unexpected error occurred. Please try again later."

            return render(request, "signup.html", {"error_message": error_message})

    return render(request, "signup.html")


def test(request):
    return render(request, "test.html")


def update_profile(request):
    if request.method == "POST":
        new_username = request.POST.get("username", "").strip()
        new_email = request.POST.get("email", "").strip()
        uid = request.session.get("uid")

        if uid:
            user_data = db.collection("users").document(uid).get().to_dict()

            if new_username != user_data.get("username"):
                db.collection("users").document(uid).update({"username": new_username})

            if new_email and new_email != user_data.get("email"):
                try:
                    # Update email in Firebase Authentication
                    admin_auth.update_user(uid, email=new_email)
                    db.collection("users").document(uid).update({"email": new_email})
                    messages.success(
                        request,
                        "Profile updated successfully. Please log in with your new email.",
                    )
                    request.session.flush()  # Log the user out
                    return redirect("login")
                except Exception as e:
                    messages.error(
                        request, "Failed to update email in Firebase Authentication."
                    )
            else:
                messages.info(
                    request,
                    "No email changes detected!.(any username changes will be automatically applied)",
                )
        else:
            messages.error(request, "You must be logged in to update your profile.")

        return redirect("user-profile")
    else:
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


def giving_review(request, hotelID):
    uid = request.session.get("uid")
    if uid:
        hotel_ref = db.collection("hotel")

        hotel_doc = hotel_ref.document(hotelID).get()
        if hotel_doc.exists:
            hotel_data = hotel_doc.to_dict()
        return render(
            request,
            "giving_review.html",
            context={"hotelID": hotelID, "hotel": hotel_data},
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
        hotel_data["averageRating"] = round(hotel_data["averageRating"], 1)
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
        hotel_data["averageRating"] = round(hotel_data["averageRating"], 1)
        return render(
            request,
            "hotel_info.html",
            {
                "hotel": hotel_data,
                "reviews": reviews,
            },
        )

    return redirect("hotel-detail")


def user_profile(request):
    uid = request.session.get("uid")
    if uid:
        user_ref = db.collection("users").document(uid)
        user_data = user_ref.get().to_dict()
        profile_picture_url = user_data.get("profilePicture", None)
        reviews_ref = db.collection("review").where("uid", "==", uid)
        reviews = reviews_ref.stream()
        formatted_reviews = []
        for review_doc in reviews:
            review_data = review_doc.to_dict()
            review_data["review_date"] = review_data["review_date"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            formatted_reviews.append(review_data)
        if user_data:
            context = {
                "users": {
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                },
                "profile_picture": profile_picture_url,
                "reviews": formatted_reviews,
                "is_admin": request.session.get("is_admin"),
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


def post_user_hotel_data(request, hotelID):
    if request.method == "POST":
        rating = request.POST.get("rating")
        visit_date = request.POST.get("visit_date")
        visit_type = request.POST.get("visit_type")
        review_title = request.POST.get("review_title")
        review_content = request.POST.get("review_content")
        # Get the user's UID from the session
        uid = request.session.get("uid")
        if uid:
            # Create a new document reference under the user's reviews subcollection
            reviews_ref = db.collection("review")
            hotel_ref = db.collection("hotel")

            hotel_doc = hotel_ref.document(hotelID).get()
            if hotel_doc.exists:
                hotelData = hotel_doc.to_dict()
            # Get the current date and time
            review_date = datetime.now()
            # Create a dictionary to store the review data

            new_review_data = {
                "rating": rating,
                "visit_date": visit_date,
                "visit_type": visit_type,
                "review_title": review_title,
                "review_content": review_content,
                "review_date": review_date,
                "hotelID": hotelID,
                "hotel_name": hotelData["hotelName"],
                "uid": uid,
            }
            reviews_ref.add(new_review_data)
            reviews = reviews_ref.where("hotelID", "==", hotelID)
            ratings = []
            for doc in reviews.stream():
                review_data = doc.to_dict()
                rating = review_data["rating"]
                if rating is not None:
                    ratings.append(float(rating))
            reviewCount = len(ratings)
            if reviewCount > 0:
                avg_rating = float(sum(ratings) / len(ratings))
            else:
                avg_rating = 0.0
            hotel_ref.document(str(hotelID)).update(
                {"averageRating": avg_rating, "review_count": reviewCount}
            )
            return redirect("user-profile")
        else:
            # Handle the case where the user is not authenticated
            return HttpResponse("User not authenticated", status=401)
    else:
        # Handle the case where the request method is not POST
        return HttpResponse("Method not allowed", status=405)


from datetime import datetime


def search_hotels(request):

    return render(request)


def get_user_reviews(request):
    # Get the user's UID from the session
    uid = request.session.get("uid")

    # Check if the user is authenticated
    if uid:
        try:
            # Get a reference to the review document
            reviews_ref = db.collection("review")

            # Get all documents from the "reviews" subcollection
            reviews = reviews_ref.stream()

            # Initialize an empty list to store formatted review data
            formatted_reviews = []

            # Iterate over each review document and format its data
            for review_doc in reviews:
                review_data = review_doc.to_dict()

                # Format the datetime object into a string
                review_data["review_date"] = review_data["review_date"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                formatted_reviews.append(review_data)
            # Pass the formatted review data to the template context
            return render(
                request, "user_profile.html", {"reviews_data": formatted_reviews}
            )
        except Exception as e:
            # Handle any exceptions that may occur during Firestore operation
            return HttpResponse(f"Error retrieving reviews: {str(e)}", status=500)
    else:
        # Handle the case where the user is not authenticated
        return HttpResponse("User not authenticated", status=401)
