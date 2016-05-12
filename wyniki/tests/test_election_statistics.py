from django import test

from wyniki import models
from wyniki.election_statistics import ElectionStatistics
from wyniki.tests import factories


class TestElectionStatistic(test.TestCase):
    def setUp(self):
        self.candidates = [factories.KandydatFactory(), factories.KandydatFactory(nazwa="Htin Kyaw")]
        self.warszawa = factories.GminaFactory(nazwa="Warszawa")
        self.wynik_a = models.Wynik.objects.create(kandydat=self.candidates[0], liczba=7, gmina=self.warszawa)
        self.wynik_b = models.Wynik.objects.create(kandydat=self.candidates[1], liczba=5, gmina=self.warszawa)

    def test_pack_result_pair(self):
        paired = ElectionStatistics.pack_result_pair(self.wynik_a, self.wynik_b, self.warszawa)
        self.assertEqual(paired, {"communePk": self.warszawa.pk, "communeName": "Warszawa",
                                  "resultCandidateA": 7, "resultCandidateB": 5})

    def test_pack_result_pair_nones(self):
        gmina = factories.GminaFactory(nazwa="Pruszków", wojewodztwo=self.warszawa.wojewodztwo)
        paired = ElectionStatistics.pack_result_pair(None, None, gmina)
        self.assertEqual(paired, {"communePk": gmina.pk, "communeName": "Pruszków",
                                  "resultCandidateA": None, "resultCandidateB": None})

    def test_pair_results_by_commune(self):
        es = ElectionStatistics(self.candidates)
        result = es.pair_results_by_commune(models.Wynik.objects.all())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][1].liczba, 7)
