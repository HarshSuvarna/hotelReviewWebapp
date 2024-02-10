// Auth.js

function toggleForm() {
    var formTitle = document.getElementById("formTitle");
    var signupFields = document.getElementById("signupFields");
    var submitButton = document.getElementById("submitButton");
    var googleButton = document.getElementById("googleButton");
    var toggleLink = document.getElementById("toggleLink");

    if (formTitle.innerText === "Login") {
        formTitle.innerText = "Sign Up";
        submitButton.innerText = "Sign Up";
        googleButton.style.display = "none";
        toggleLink.innerHTML = "Already have an account? <a href='#' onclick='toggleForm()'>Login</a>";
        signupFields.style.display = "block";
    } else {
        formTitle.innerText = "Login";
        submitButton.innerText = "Login";
        googleButton.style.display = "block";
        toggleLink.innerHTML = "Don't have an account? <a href='#' onclick='toggleForm()'>Sign Up</a>";
        signupFields.style.display = "none";
    }
}

function loginWithGoogle() {
    // Add your Google login logic here
}
