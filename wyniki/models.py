from django.core.exceptions import ValidationError
from django.db import models


class Wojewodztwo(models.Model):
    nazwa = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'województwa'


class Gmina(models.Model):
    RODZAJ_MIASTO = 'miasto'
    RODZAJ_WIEŚ = 'wieś'
    RODZAJ_STATKI = 'statki'
    RODZAJ_ZAGRANICA = 'zagranica'
    RODZAJ_CHOICES = [
        (v, v) for v in [RODZAJ_MIASTO, RODZAJ_WIEŚ, RODZAJ_STATKI, RODZAJ_ZAGRANICA]
    ]
    nazwa = models.CharField(unique=True, max_length=100)
    rodzaj = models.CharField(choices=RODZAJ_CHOICES, max_length=100)
    wojewodztwo = models.ForeignKey(Wojewodztwo)
    liczba_mieszkancow = models.IntegerField()
    liczba_uprawnionych = models.IntegerField()
    liczba_wydanych_kart = models.IntegerField()
    liczba_glosow_oddanych = models.IntegerField()
    liczba_glosow_kandydat_a = models.IntegerField()
    liczba_glosow_kandydat_b = models.IntegerField()

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'gminy'

    def clean(self):
        if self.liczba_glosow_kandydat_a + self.liczba_glosow_kandydat_b > self.liczba_glosow_oddanych:
            raise ValidationError("Łączna liczba głosow na kandydatów nie może przekraczać liczby głosów oddanych")
        if self.liczba_glosow_oddanych > self.liczba_wydanych_kart:
            raise ValidationError("Liczba głosów oddanych nie może przekrazać liczby wydanych kart")
        if self.liczba_wydanych_kart > self.liczba_uprawnionych:
            raise ValidationError("Liczba wydanych kart nie może przekraczać liczby uprawnionych")
        if self.liczba_uprawnionych > self.liczba_mieszkancow:
            raise ValidationError("Liczba uprawnionych nie może przekraczać liczby mieszkańców")
        super().clean()


class Kandydat(models.Model):
    nazwa = models.CharField(max_length=200)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'kandydaci'