import json
from datetime import timedelta, datetime
from unittest import mock

from django import test
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

from wyniki import models
from wyniki.tests import factories


class ChangeResultsJsonViewTest(test.TestCase):
    def setUp(self):
        self.username = "franek"
        self.password = "kenarf"
        self.user = User.objects.create_user(self.username, None, self.password)
        self.assertTrue(self.client.login(username=self.username, password=self.password))

        self.candidates = [
            factories.KandydatFactory(),
            factories.KandydatFactory(nazwa="Htin Kyaw")
        ]
        self.commune = factories.GminaFactory()

    def test_post(self):
        soon = timezone.now() + timedelta(hours=1)
        data = {
            'commune': self.commune.pk,
            'result_a': 123,
            'candidate_a': self.candidates[0].pk,
            'result_b': 10,
            'candidate_b': self.candidates[1].pk,
            'modification': self.commune.data_modyfikacji.strftime("%c")
        }
        with mock.patch("django.utils.timezone.now") as now_mock:
            now_mock.return_value = soon
            response = self.client.post(reverse("change-results"), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'OK')
        result = models.Wynik.objects.get(gmina=self.commune, kandydat=self.candidates[0])
        self.assertEqual(result.liczba, 123)
        self.commune.refresh_from_db()
        self.assertEqual(self.commune.data_modyfikacji, soon)

    def test_post_wrong_date(self):
        data = {
            'commune': self.commune.pk,
            'result_a': 123,
            'candidate_a': self.candidates[0].pk,
            'result_b': 10,
            'candidate_b': self.candidates[1].pk,
            'modification': (self.commune.data_modyfikacji + timedelta(days=1)).strftime("%c")
        }
        response = self.client.post(reverse("change-results"), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'outdatedModification')

    def test_post_wrong(self):
        response = self.client.post(reverse("change-results"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'formError')

    def test_post_overflow(self):
        wynik = models.Wynik.objects.create(gmina=self.commune, kandydat=self.candidates[0], liczba=1000)
        data = {
            'commune': self.commune.pk,
            'result_a': 30000,
            'candidate_a': self.candidates[0].pk,
            'result_b': 20000,
            'candidate_b': self.candidates[1].pk,
            'modification': self.commune.data_modyfikacji.strftime("%c")
        }
        response = self.client.post(reverse("change-results"), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'saveFailed')
        wynik.refresh_from_db()
        self.assertEqual(wynik.liczba, 1000)
