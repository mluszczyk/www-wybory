from django.core.exceptions import ValidationError
from django.test import TestCase

from wyniki import models
from wyniki.tests import factories


class TestKandydat(TestCase):
    def setUp(self):
        self.gmina = factories.GminaFactory()
        self.kandydat = factories.KandydatFactory()
        self.kandydat2 = factories.KandydatFactory(nazwa="Htin Kyaw")

    def test_clean_ok(self):
        wynik = models.Wynik(
            gmina=self.gmina, kandydat=self.kandydat, liczba=3000
        )
        wynik.clean()

    def test_clean_result_too_big(self):
        models.Wynik.objects.create(
            gmina=self.gmina, kandydat=self.kandydat2, liczba=40000)
        with self.assertRaises(ValidationError):
            models.Wynik(
                gmina=self.gmina, kandydat=self.kandydat, liczba=6000
            ).clean()

