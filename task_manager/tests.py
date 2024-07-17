from django.test import TestCase

from task_manager.models import CustomUser

# Create your tests here.
# TODO: Write tests


class AuthorizationTest(TestCase):
    def test_register_function(self):
        test_user_data = {"email": "example@example.com", "password": "L5Kr72Xb8i", "username": "TestUser"}

        response = self.client.post("/api/auth/signup/", data=test_user_data)
        response_body = response.json()

        self.assertEqual(response.status_code, 201)

        self.assertIsNotNone(response_body.get("tokens"))
        self.assertIsNotNone(response_body.get("user"))
        self.assertIsNotNone(response_body.get("tokens", {}).get("access_token"))

        self.assertEqual(CustomUser.objects.first().username, "TestUser")
        self.assertEqual(CustomUser.objects.first().email, "example@example.com")

    def test_register_with_simple_password(self):
        test_user_data = {"email": "example@example.com", "password": "12345678", "username": "TestUser"}

        error = {"password": ["This password is too common.", "This password is entirely numeric."]}
        response = self.client.post("/api/auth/signup/", data=test_user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), error)

    def test_register_already_registered_user(self):
        test_user_data = {"email": "example@example.com", "password": "L5Kr72Xb8i", "username": "TestUser"}

        response1 = self.client.post("/api/auth/signup/", data=test_user_data)
        self.assertEqual(response1.status_code, 201)

        error = {"username": ["This field must be unique."], "email": ["This field must be unique."]}
        response2 = self.client.post("/api/auth/signup/", data=test_user_data)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json(), error)

    def test_refresh_token(self):
        pass

    def test_refresh_token_with_undefined_token(self):
        pass

    def test_login(self):
        pass

    def test_login_to_undefined_account(self):
        pass
