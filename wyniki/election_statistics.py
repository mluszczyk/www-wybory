from django.db.models import Sum
from django.db.models.functions import Coalesce

from wyniki import models


class ElectionStatistics:
    def __init__(self, candidates):
        assert len(candidates) == 2, "Exactly two candidates are required"
        self.candidates = candidates

    def get_candidates(self):
        return self.candidates

    def get_commune_size_statistics(self):
        limits = [5000, 10000, 20000, 50000, 100000, 200000, 500000]
        special_types = [models.Gmina.RODZAJ_STATKI, models.Gmina.RODZAJ_ZAGRANICA]
        rows = [
            self.get_aggregates_for_queryset('Statki i zagranica', models.Wynik.objects.filter(
                gmina__rodzaj__in=special_types)),
            self.get_aggregates_for_queryset(
                "do {}".format(limits[0]),
                models.Wynik.objects.filter(gmina__liczba_mieszkancow__lte=limits[0]
                                            ).exclude(gmina__rodzaj__in=special_types))
        ]

        for lower_limit, upper_limit in zip(limits[:-1], limits[1:]):
            rows.append(
                self.get_aggregates_for_queryset(
                    "od {} do {}".format(lower_limit + 1, upper_limit),
                    models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=lower_limit,
                                                gmina__liczba_mieszkancow__lte=upper_limit
                                                ).exclude(gmina__rodzaj__in=special_types)
                )
            )

        rows.append(
            self.get_aggregates_for_queryset(
                "pow. {}".format(limits[-1]),
                models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=limits[-1])))
        return rows

    def get_voivodeship_statistics(self):
        items = []
        for item in models.Wojewodztwo.objects.all().order_by('nazwa'):
            for letter, kandydat in zip(['a', 'b'], self.candidates):
                aggregate = kandydat.wynik_set.filter(gmina__wojewodztwo=item).aggregate(
                    sum=Coalesce(Sum('liczba'), 0))
                setattr(item, 'liczba_glosow_kandydat_{}'.format(letter), aggregate['sum'])
            items.append(item)
        return items

    def get_commune_type_statistics(self):
        items = []
        for commune_type, _ in models.Gmina.RODZAJ_CHOICES:
            queryset = models.Wynik.objects.filter(gmina__rodzaj=commune_type)
            row = self.get_aggregates_for_queryset(commune_type, queryset)
            items.append(row)
        return items

    def get_aggregates_for_queryset(self, name, queryset):
        row = self.get_vote_aggregates(queryset)
        row['nazwa'] = name
        return row

    def get_vote_aggregates(self, queryset):
        aggregates = ['liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b']
        row = {}
        for agg, candidate in zip(aggregates, self.candidates):
            queryset_aggregate = queryset.filter(
                kandydat=candidate
            ).aggregate(
                sum=Coalesce(Sum("liczba"), 0)
            )
            row[agg] = queryset_aggregate["sum"]
        return row

    def get_general_statistics(self):
        aggregates = [
            'liczba_mieszkancow', 'liczba_uprawnionych',
            'liczba_wydanych_kart', 'liczba_glosow_oddanych',
        ]
        data = {}
        for aggregate in aggregates:
            result = models.Gmina.objects.aggregate(
                **{aggregate: Coalesce(Sum(aggregate), 0)}
            )
            data.update(result)
        data.update(self.get_vote_aggregates(models.Wynik.objects.all()))
        data['powierzchnia'] = 312685
        data['zaludnienie'] = data['liczba_mieszkancow'] / data['powierzchnia']
        data['liczba_glosow_waznych'] = data['liczba_glosow_kandydat_a'] + data['liczba_glosow_kandydat_b']
        data['candidates_summary'] = []
        for num, letter in enumerate(['a', 'b']):
            vote_count = data['liczba_glosow_kandydat_{}'.format(letter)]
            fraction = vote_count / data['liczba_glosow_waznych'] if data['liczba_glosow_waznych'] else 0
            data['candidates_summary'].append({
                'count': vote_count,
                'fraction': self.format_fraction(fraction),
                'percent': self.format_percent(fraction),
            })
        return data

    @staticmethod
    def format_percent(fraction):
        percent = "{0:.2f}".format(100 * fraction)
        return percent

    @staticmethod
    def format_fraction(fraction):
        return "{0:.4f}".format(fraction)
