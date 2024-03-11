from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
class LoginViewTestCase(TestCase):
    def setUp(self):
        # Create a test user for authentication
        self.test_email = 'adityamadhira07@gmail.com'
        self.test_password = '12345678'
        User.objects.create_user(username='testuser', email=self.test_email, password=self.test_password)

        # Define login URL in setUp so it's available to all test methods
        self.login_url = reverse('login')

    def test_login_success(self):
        # Correct credentials with 'email' field instead of 'username'
        credentials = {
            'email': self.test_email,
            'password': self.test_password,
        }

        # Use self.login_url, which is defined in setUp
        response = self.client.post(self.login_url, credentials, follow=True)

        # Check for successful redirect (adjust the expected_url as per your project's redirect URL after successful login)
        self.assertRedirects(response, expected_url=reverse('home'), status_code=302, target_status_code=200)

    def test_login_failure(self):
        # Incorrect credentials with 'email' field
        credentials = {
            'email': self.test_email,
            'password': 'wrongpassword',
        }

        # Use self.login_url, which is defined in setUp
        response = self.client.post(self.login_url, credentials)

        # Check that login failed and the user is not redirected
        self.assertEqual(response.status_code, 200)
        # Assert that the response context contains an error message (adjust 'error_message' according to your implementation)
        self.assertTrue('error_message' in response.context)


from django.test import TestCase
from django.urls import reverse

class ForgotPasswordTestCase(TestCase):
    def setUp(self):
        self.forgot_password_url = reverse('forgot_password')

    def test_forgot_password_with_valid_email(self):
        valid_email_data = {'email': 'adityamadhira07@gmail.com'}
        response = self.client.post(self.forgot_password_url, valid_email_data, follow=True)

        # If there's a specific page you redirect to on success, check for that
        # For example, redirecting back to the login page with a success message
        self.assertRedirects(response, expected_url=reverse('login'), status_code=302, target_status_code=200)
        # Check for success message in the context, if applicable
        # self.assertContains(response, 'Password reset link has been sent to your email.')

    def test_forgot_password_with_invalid_email(self):
        invalid_email_data = {'email': 'nonexistentuser@example.com'}
        response = self.client.post(self.forgot_password_url, invalid_email_data, follow=True)

        # Expect a redirect to the login page for an invalid email
        self.assertRedirects(response, expected_url=reverse('login'), status_code=302, target_status_code=200)

        # Optionally, check for a specific error message if your application uses the messages framework to communicate the result of the operation to the user
        # self.assertContains(response, 'No account found with this email.', status_code=200)