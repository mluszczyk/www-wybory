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
        iterables = [
            cls.get_aggregates_for_queryset('Statki i zagranica', models.Gmina.objects.filter(
                rodzaj__in=[models.Gmina.RODZAJ_STATKI, models.Gmina.RODZAJ_ZAGRANICA])),
            cls.get_aggregates_for_queryset("do {}", models.Gmina.objects.filter(liczba_mieszkancow__lte=limits[0]))
        ]

        for lower_limit, upper_limit in zip(limits[:-1], limits[1:]):
            iterables.append(
                cls.get_aggregates_for_queryset(
                    "od {} do {}".format(lower_limit + 1, upper_limit),
                    models.Gmina.objects.filter(liczba_mieszkancow__gt=lower_limit, liczba_mieszkancow__lte=upper_limit)
                )
            )

        iterables.append(
            cls.get_aggregates_for_queryset(
                "pow. {}".format(limits[-1]),
                models.Gmina.objects.filter(liczba_mieszkancow__gt=limits[-1])))
        items = chain.from_iterable(iterables)
        return items

    @classmethod
    def get_voivodeship_statistics(cls):
        annotations = ['liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b']
        kwargs = {k: Coalesce(Sum('gmina__{}'.format(k)), 0) for k in annotations}
        items = models.Wojewodztwo.objects.annotate(**kwargs).order_by('nazwa')
        return items

    @classmethod
    def get_commune_type_statistics(cls):
        items = []
        for commune_type, _ in models.Gmina.RODZAJ_CHOICES:
            queryset = models.Gmina.objects.filter(rodzaj=commune_type)
            for row in cls.get_aggregates_for_queryset(commune_type, queryset):
                items.append(row)
        return items

    @classmethod
    def get_aggregates_for_queryset(cls, name, queryset):
        aggregates = ['liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b']
        row = queryset.aggregate(**{
            aggregate: Coalesce(Sum(aggregate), 0) for aggregate in aggregates
            })
        row['nazwa'] = name
        if row['liczba_glosow_kandydat_a'] + row['liczba_glosow_kandydat_b'] > 0:
            yield row

    @classmethod
    def get_general_statistics(cls):
        aggregates = [
            'liczba_mieszkancow', 'liczba_uprawnionych',
            'liczba_wydanych_kart', 'liczba_glosow_oddanych',
            'liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b'
        ]
        data = {}
        for aggregate in aggregates:
            result = models.Gmina.objects.aggregate(**{aggregate: Sum(aggregate)})
            data.update(result)
        data['powierzchnia'] = 312685
        data['zaludnienie'] = data['liczba_mieszkancow'] / data['powierzchnia']
        data['liczba_glosow_waznych'] = data['liczba_glosow_kandydat_a'] + data['liczba_glosow_kandydat_b']
        data['candidates_summary'] = []
        for num, letter in enumerate(['a', 'b']):
            vote_count = data['liczba_glosow_kandydat_{}'.format(letter)]
            fraction = vote_count / data['liczba_glosow_waznych']
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
