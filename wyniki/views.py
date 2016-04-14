from django.views.generic import TemplateView

from wyniki import models
from wyniki.election_statistics import ElectionStatistics


class ResultsView(TemplateView):
    template_name = "wyniki/results.html"

    def get_context_data(self, **kwargs):
        candidates = list(models.Kandydat.objects.all())
        statistics = ElectionStatistics(candidates)
        data = statistics.get_general_statistics()
        data['voivodeship_statistics'] = statistics.get_voivodeship_statistics()
        data['commune_type_statistics'] = statistics.get_commune_type_statistics()
        data['commune_size_statistics'] = statistics.get_commune_size_statistics()
        data['candidates'] = statistics.get_candidates()
        data['candidates_data'] = ({'model': model, 'summary': summary}
                                   for model, summary in zip(data['candidates'], data['candidates_summary']))

        return data
