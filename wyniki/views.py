from itertools import chain

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.views.generic import TemplateView

from wyniki import models


class ResultsView(TemplateView):
    template_name = "wyniki/results.html"

    def get_candidates(self):
        return models.Kandydat.objects.all()

    def get_context_data(self, **kwargs):
        data = self.get_general_statistics()
        data['voivodeship_statistics'] = self.get_voivodeship_statistics()
        data['commune_type_statistics'] = self.get_commune_type_statistics()
        data['commune_size_statistics'] = self.get_commune_size_statistics()
        data['candidates'] = self.get_candidates()
        data['candidates_data'] = ({'model': model, 'summary': summary}
                                   for model, summary in zip(data['candidates'], data['candidates_summary']))

        return data

    @classmethod
    def get_commune_size_statistics(cls):
        limits = [5000, 10000, 20000, 50000, 100000, 200000, 500000]
        special_types = [models.Gmina.RODZAJ_STATKI, models.Gmina.RODZAJ_ZAGRANICA]
        rows = [
            cls.get_aggregates_for_queryset('Statki i zagranica', models.Wynik.objects.filter(
                gmina__rodzaj__in=special_types)),
            cls.get_aggregates_for_queryset(
                "do {}".format(limits[0]),
                models.Wynik.objects.filter(gmina__liczba_mieszkancow__lte=limits[0]
                                            ).exclude(gmina__rodzaj__in=special_types))
        ]

        for lower_limit, upper_limit in zip(limits[:-1], limits[1:]):
            rows.append(
                cls.get_aggregates_for_queryset(
                    "od {} do {}".format(lower_limit + 1, upper_limit),
                    models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=lower_limit,
                                                gmina__liczba_mieszkancow__lte=upper_limit
                                                ).exclude(gmina__rodzaj__in=special_types)
                )
            )

        rows.append(
            cls.get_aggregates_for_queryset(
                "pow. {}".format(limits[-1]),
                models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=limits[-1])))
        return rows

    @classmethod
    def get_voivodeship_statistics(cls):
        items = []
        for item in models.Wojewodztwo.objects.all().order_by('nazwa'):
            for letter, kandydat in zip(['a', 'b'], models.Kandydat.objects.all().order_by('id')):
                aggregate = kandydat.wynik_set.filter(gmina__wojewodztwo=item).aggregate(
                    sum=Coalesce(Sum('liczba'), 0))
                setattr(item, 'liczba_glosow_kandydat_{}'.format(letter), aggregate['sum'])
            items.append(item)
        return items

    @classmethod
    def get_commune_type_statistics(cls):
        items = []
        for commune_type, _ in models.Gmina.RODZAJ_CHOICES:
            queryset = models.Wynik.objects.filter(gmina__rodzaj=commune_type)
            row = cls.get_aggregates_for_queryset(commune_type, queryset)
            items.append(row)
        return items

    @classmethod
    def get_aggregates_for_queryset(cls, name, queryset):
        row = cls.get_vote_aggregates(queryset)
        row['nazwa'] = name
        return row

    @classmethod
    def get_vote_aggregates(cls, queryset):
        aggregates = ['liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b']
        candidates = models.Kandydat.objects.all()
        row = {}
        for agg, candidate in zip(aggregates, candidates):
            queryset_aggregate = queryset.filter(
                kandydat=candidate
            ).aggregate(
                sum=Coalesce(Sum("liczba"), 0)
            )
            row[agg] = queryset_aggregate["sum"]
        return row

    @classmethod
    def get_general_statistics(cls):
        aggregates = [
            'liczba_mieszkancow', 'liczba_uprawnionych',
            'liczba_wydanych_kart', 'liczba_glosow_oddanych',
        ]
        data = {}
        for aggregate in aggregates:
            result = models.Gmina.objects.aggregate(**{aggregate: Sum(aggregate)})
            data.update(result)
        data.update(cls.get_vote_aggregates(models.Wynik.objects.all()))
        data['powierzchnia'] = 312685
        data['zaludnienie'] = data['liczba_mieszkancow'] / data['powierzchnia']
        data['liczba_glosow_waznych'] = data['liczba_glosow_kandydat_a'] + data['liczba_glosow_kandydat_b']
        data['candidates_summary'] = []
        for num, letter in enumerate(['a', 'b']):
            vote_count = data['liczba_glosow_kandydat_{}'.format(letter)]
            fraction = vote_count / data['liczba_glosow_waznych'] if data['liczba_glosow_waznych'] else 0
            data['candidates_summary'].append({
                'count': vote_count,
                'fraction': cls.format_fraction(fraction),
                'percent': cls.format_percent(fraction),
            })
        return data

    @staticmethod
    def format_percent(fraction):
        percent = "{0:.2f}".format(100 * fraction)
        return percent

    @staticmethod
    def format_fraction(fraction):
        return "{0:.4f}".format(fraction)
