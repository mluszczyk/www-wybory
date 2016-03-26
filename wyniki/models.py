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


class Kandydat(models.Model):
    nazwa = models.CharField(max_length=200)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'kandydaci'