import json

from django import test
from django.core.urlresolvers import reverse

from wyniki import models
from wyniki.tests import factories


class TestCommuneListJsonView(test.TestCase):
    def test_view(self):
        candidate = factories.KandydatFactory()
        factories.KandydatFactory(nazwa="Htin Kyaw")
        gmina = factories.GminaFactory()
        models.Wynik.objects.create(gmina=gmina, kandydat=candidate, liczba=5)
        response = self.client.get(reverse('commune-list', args=('voivodeship', 'mazowieckie')))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data["status"], "OK")
        self.assertEqual(len(data["communeList"]), 1)
