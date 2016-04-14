from factory import SubFactory
from factory.django import DjangoModelFactory

from wyniki import models


class WojewodztwoFactory(DjangoModelFactory):
    nazwa = "mazowieckie"

    class Meta:
        model = models.Wojewodztwo


class GminaFactory(DjangoModelFactory):
    nazwa = "Pruszków"
    rodzaj = models.Gmina.RODZAJ_MIASTO
    wojewodztwo = SubFactory(WojewodztwoFactory)
    liczba_mieszkancow = 100000
    liczba_uprawnionych = 70000
    liczba_wydanych_kart = 50000
    liczba_glosow_oddanych = 45500

    class Meta:
        model = models.Gmina


class KandydatFactory(DjangoModelFactory):
    nazwa = "Aung San Suu Kyi"

    class Meta:
        model = models.Kandydat
