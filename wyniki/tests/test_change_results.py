import json
from datetime import timedelta, datetime
from unittest import mock

from django import test
from django.core.urlresolvers import reverse
from django.utils import timezone

from wyniki import models
from wyniki.tests import factories


class ChangeResultsJsonViewTest(test.TestCase):
    def setUp(self):
        self.candidates = [
            factories.KandydatFactory(),
            factories.KandydatFactory(nazwa="Htin Kyaw")
        ]
        self.commune = factories.GminaFactory()

    @mock.patch("django.utils.timezone.now")
    def test_post(self, now_mock):
        now = timezone.make_aware(datetime(2100, 3, 5))
        now_mock.return_value = now
        data = {
            'commune': self.commune.pk,
            'result_a': 123,
            'candidate_a': self.candidates[0].pk,
            'result_b': 10,
            'candidate_b': self.candidates[1].pk,
            'modification': self.commune.data_modyfikacji.strftime("%c")
        }
        response = self.client.post(reverse("change-results"), data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'OK')
        result = models.Wynik.objects.get(gmina=self.commune, kandydat=self.candidates[0])
        self.assertEqual(result.liczba, 123)
        self.commune.refresh_from_db()
        self.assertEqual(self.commune.data_modyfikacji, now)

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
