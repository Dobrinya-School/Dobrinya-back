from rest_framework.test import APITestCase

from .models import User

class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="12345"
        )

    def test_login(self):
        exp = self.client.login(email="student@example.com", password="12345")
        exp2 = self.client.login(email="student@example.com", password="1111111")
        self.assertTrue(exp)
        self.assertFalse(exp2)