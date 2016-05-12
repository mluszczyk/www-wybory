import json

from django import test
from django.core.urlresolvers import reverse

from wyniki import models
from wyniki.tests import factories


class ChangeResultsJsonViewTest(test.TestCase):
    def setUp(self):
        self.candidates = [
            factories.KandydatFactory(),
            factories.KandydatFactory(nazwa="Htin Kyaw")
        ]
        self.commune = factories.GminaFactory()

    def test_post(self):
        data = {
            'commune': self.commune.pk,
            'result_a': 123,
            'candidate_a': self.candidates[0].pk,
            'result_b': 10,
            'candidate_b': self.candidates[1].pk,
        }
        response = self.client.post(reverse("change-results"), data)
        self.assertEqual(response.status_code, 200)
        result = models.Wynik.objects.get(gmina=self.commune, kandydat=self.candidates[0])
        self.assertEqual(result.liczba, 123)

    def test_post_wrong(self):
        response = self.client.post(reverse("change-results"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data['status'], 'form_error')
