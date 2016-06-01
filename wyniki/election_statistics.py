from collections import namedtuple

import itertools
from typing import Union

import pytz
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from wyniki import models


StatisticRow = namedtuple("StatisticRow", ["code", "name", "queryset"])


def get_commune_statistics_list():
    limits = [5000, 10000, 20000, 50000, 100000, 200000, 500000]
    special_types = [models.Gmina.RODZAJ_STATKI, models.Gmina.RODZAJ_ZAGRANICA]
    rows = [
        StatisticRow("statki-zagranica", 'Statki i zagranica',
                     models.Wynik.objects.filter(gmina__rodzaj__in=special_types)),
        StatisticRow("do", "do {}".format(limits[0]),
                     models.Wynik.objects.filter(gmina__liczba_mieszkancow__lte=limits[0]
                                                 ).exclude(gmina__rodzaj__in=special_types))
    ]
    for lower_limit, upper_limit in zip(limits[:-1], limits[1:]):
        rows.append(
            StatisticRow("{}-{}".format(lower_limit, upper_limit),
                         "od {} do {}".format(lower_limit + 1, upper_limit),
                         models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=lower_limit,
                                                     gmina__liczba_mieszkancow__lte=upper_limit
                                                     ).exclude(gmina__rodzaj__in=special_types))
        )
    rows.append(
        StatisticRow("od", "pow. {}".format(limits[-1]),
                     models.Wynik.objects.filter(gmina__liczba_mieszkancow__gt=limits[-1])))
    return rows


def get_commune_type_statistics_list():
    items = []
    for commune_type, _ in models.Gmina.RODZAJ_CHOICES:
        queryset = models.Wynik.objects.filter(gmina__rodzaj=commune_type)
        items.append(StatisticRow(commune_type, commune_type, queryset))
    return items


def get_voivodeship_statistics_list():
    items = []
    for item in models.Wojewodztwo.objects.all().order_by('nazwa'):
        queryset = models.Wynik.objects.filter(gmina__wojewodztwo=item)
        items.append(StatisticRow(item.nazwa, item.nazwa, queryset))
    return items

STATISTICS = {
    "commune_size": get_commune_statistics_list,
    "commune_type": get_commune_type_statistics_list,
    "voivodeship": get_voivodeship_statistics_list
}


class ElectionStatistics:
    def __init__(self, candidates):
        assert len(candidates) == 2, "Exactly two candidates are required"
        self.candidates = candidates

    def get_candidates(self):
        return self.candidates

    def get_statistics(self, category):
        list_func = STATISTICS[category]
        rows = list_func()
        return [self.statistic_row_to_items(row) for row in rows]

    def statistic_row_to_items(self, row: StatisticRow):
        row_dict = self.get_aggregates_for_queryset(row.name, row.queryset)
        row_dict['kod'] = row.code
        return row_dict

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
        data['zaludnienie'] = round(data['liczba_mieszkancow'] / data['powierzchnia'], 2)
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
        data['kandydat_a_nazwa'] = self.candidates[0].nazwa
        data['kandydat_a_procent'] = data['candidates_summary'][0]['percent']
        data['kandydat_b_nazwa'] = self.candidates[1].nazwa
        data['kandydat_b_procent'] = data['candidates_summary'][1]['percent']
        now = timezone.now().astimezone(pytz.timezone("Europe/Warsaw"))
        data['generation_info'] = "Dane wygenerowane {0:%H}:{0:%M}:{0:%S} {0:%Z}.".format(now)

        return data

    @staticmethod
    def format_percent(fraction):
        percent = "{0:.2f}".format(100 * fraction)
        return percent

    @staticmethod
    def format_fraction(fraction):
        return "{0:.4f}".format(fraction)

    def get_commune_list(self, category, code):
        group = self.get_statistic_group(category, code)
        wyniki = group.queryset
        grouped = self.pair_results_by_commune(wyniki)
        result = []
        for commune, candidate_a, candidate_b in grouped:
            result.append(self.pack_result_pair(candidate_a, candidate_b, commune))
        return result

    def pair_results_by_commune(self, wyniki):
        aggregates = ['liczba_glosow_kandydat_a', 'liczba_glosow_kandydat_b']
        grouped = {}
        for num, agg, candidate in zip(itertools.count(1), aggregates, self.candidates):
            candidate_queryset = wyniki.filter(kandydat=candidate)
            for result in candidate_queryset:
                record = grouped.get(result.gmina.pk, [None, None, None])
                record[0] = result.gmina
                record[num] = result
                grouped[result.gmina.pk] = record
        return list(grouped.values())

    @staticmethod
    def pack_result_pair(result_a: Union[models.Wynik, None], result_b: Union[models.Wynik, None],
                         commune: models.Gmina):
        return {
            'communePk': commune.pk,
            'communeName': commune.nazwa,
            'resultCandidateA': getattr(result_a, "liczba", None),
            'resultCandidateB': getattr(result_b, "liczba", None),
            'previousModification': commune.data_modyfikacji.strftime("%c"),
        }

    @staticmethod
    def get_statistic_group(category, code) -> StatisticRow:
        statistics_list = STATISTICS[category]()
        statistics_dict = {row.code: row for row in statistics_list}
        group = statistics_dict[code]
        return group
