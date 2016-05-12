from django import forms

from wyniki import models


class ChangeResults(forms.Form):
    commune = forms.ModelChoiceField(models.Gmina.objects.all())
    candidate_a = forms.ModelChoiceField(models.Kandydat.objects.all())
    result_a = forms.IntegerField()
    candidate_b = forms.ModelChoiceField(models.Kandydat.objects.all())
    result_b = forms.IntegerField()

    @staticmethod
    def save_result(commune, candidate, number):
        result = models.Wynik.objects.filter(gmina=commune, kandydat=candidate).first()
        if result is None:
            result = models.Wynik(gmina=commune, kandydat=candidate)
        result.liczba = number
        result.save()

    def save(self):
        commune = self.cleaned_data['commune']
        self.save_result(commune, self.cleaned_data['candidate_a'], self.cleaned_data['result_a'])
        self.save_result(commune, self.cleaned_data['candidate_b'], self.cleaned_data['result_b'])
