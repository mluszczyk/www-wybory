from django import test

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class TestLogin(test.TestCase):
    def setUp(self):
        self.username = "franek"
        self.password = "kenarf"
        self.user = User.objects.create_user(self.username, None, self.password)

    def test_login_wrong(self):
        response = self.client.post(reverse("ajax-login"),
                                    data={"username": "wrong", "password": "credentials"})
        self.assertEqual(response.status_code, 403)

    def test_login_ok(self):
        response = self.client.post(reverse("ajax-login"),
                                    data={"username": self.username, "password": self.password})
        self.assertEqual(response.status_code, 200)