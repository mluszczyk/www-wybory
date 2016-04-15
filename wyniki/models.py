from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce

MESSAGE_TOO_MANY_VOTES = (
    "Suma głosów na kandydatów w gminie nie może być wyższa niż "
    "liczba głosów oddanych"
)


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

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'gminy'

    def clean(self):
        super().clean()
        votes_agg = self.wynik_set.select_for_update().aggregate(sum=Coalesce(Sum("liczba"), 0))
        votes_sum = votes_agg["sum"]
        if self.liczba_glosow_oddanych is not None and votes_sum is not None:
            if votes_sum > self.liczba_glosow_oddanych:
                raise ValidationError(MESSAGE_TOO_MANY_VOTES)
        if self.liczba_glosow_oddanych is not None and self.liczba_wydanych_kart is not None:
            if self.liczba_glosow_oddanych > self.liczba_wydanych_kart:
                raise ValidationError("Liczba głosów oddanych nie może przekrazać liczby wydanych kart")
        if self.liczba_wydanych_kart is not None and self.liczba_uprawnionych is not None:
            if self.liczba_wydanych_kart > self.liczba_uprawnionych:
                raise ValidationError("Liczba wydanych kart nie może przekraczać liczby uprawnionych")
        if self.liczba_uprawnionych is not None and self.liczba_mieszkancow is not None:
            if self.liczba_uprawnionych > self.liczba_mieszkancow:
                raise ValidationError("Liczba uprawnionych nie może przekraczać liczby mieszkańców")


class Wynik(models.Model):
    """Wynik kandydata w gminie."""
    kandydat = models.ForeignKey('Kandydat')
    gmina = models.ForeignKey('Gmina')
    liczba = models.IntegerField()

    class Meta:
        unique_together = ('kandydat', 'gmina')
        verbose_name_plural = 'wyniki'

    def __str__(self):
        return "Wynik: kandydat {}, gmina {}".format(self.kandydat, self.gmina)

    def clean(self):
        super().clean()
        gmina = Gmina.objects.select_for_update().get(pk=self.gmina.pk)
        votes_aggr = self.gmina.wynik_set.all().exclude(
            pk=self.pk
        ).select_for_update().aggregate(sum=Coalesce(Sum("liczba"), 0))
        if self.liczba is None:
            return
        rest = votes_aggr["sum"]
        if rest + self.liczba > gmina.liczba_glosow_oddanych:
            raise ValidationError(MESSAGE_TOO_MANY_VOTES)


class Kandydat(models.Model):
    nazwa = models.CharField(max_length=200)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name_plural = 'kandydaci'
