from django import forms
from django.utils import timezone

from wyniki import models


class OutdatedModificationError(Exception):
    def __init__(self, user, last):
        self.user = user
        self.last = last

    def __str__(self):
        return "Wrong modification date. User provided {}, expected {}".format(self.user, self.last)


class ChangeResults(forms.Form):
    commune = forms.ModelChoiceField(models.Gmina.objects.all())
    candidate_a = forms.ModelChoiceField(models.Kandydat.objects.all())
    result_a = forms.IntegerField()
    candidate_b = forms.ModelChoiceField(models.Kandydat.objects.all())
    result_b = forms.IntegerField()
    modification = forms.DateTimeField(input_formats=["%c"])

    @staticmethod
    def save_result(commune, candidate, number):
        result = models.Wynik.objects.filter(gmina=commune, kandydat=candidate).first()
        if result is None:
            result = models.Wynik(gmina=commune, kandydat=candidate)
        result.liczba = number
        result.save()

    def validate_commune(self):
        commune = self.cleaned_data['commune']
        if commune.data_modyfikacji.replace(microsecond=0) != self.cleaned_data['modification']:
            raise OutdatedModificationError(user=commune.uzytkownik,
                                            last=commune.data_modyfikacji)

    def save(self, user):
        commune = self.cleaned_data['commune']
        self.validate_commune()
        self.save_result(commune, self.cleaned_data['candidate_a'], self.cleaned_data['result_a'])
        self.save_result(commune, self.cleaned_data['candidate_b'], self.cleaned_data['result_b'])
        commune.data_modyfikacji = timezone.now()
        commune.uzytkownik = user
        commune.save()
