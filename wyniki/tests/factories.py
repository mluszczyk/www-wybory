import datetime

from django.contrib.auth.models import User
from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory

from wyniki import models


class WojewodztwoFactory(DjangoModelFactory):
    nazwa = "mazowieckie"

    class Meta:
        model = models.Wojewodztwo


class UzytkownikFactory(DjangoModelFactory):
    username = "jan"

    class Meta:
        model = User


class GminaFactory(DjangoModelFactory):
    nazwa = "Pruszków"
    rodzaj = models.Gmina.RODZAJ_MIASTO
    wojewodztwo = SubFactory(WojewodztwoFactory)
    liczba_mieszkancow = 100000
    liczba_uprawnionych = 70000
    liczba_wydanych_kart = 50000
    liczba_glosow_oddanych = 45500
    data_modyfikacji = timezone.make_aware(datetime.datetime(2002, 2, 2))
    uzytkownik = SubFactory(UzytkownikFactory)

    class Meta:
        model = models.Gmina


class KandydatFactory(DjangoModelFactory):
    nazwa = "Aung San Suu Kyi"

    class Meta:
        model = models.Kandydat
