import json

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView, View

from wyniki import forms, models
from wyniki.election_statistics import ElectionStatistics


def format_percent(a, b):
    percent = "{0:.2f}".format(100 * a / b)
    return percent


def prepare_table(raw_rows, category):
    ready_rows = []
    for numer, raw_row in enumerate(raw_rows, start=1):
        liczba_a = raw_row['liczba_glosow_kandydat_a']
        liczba_b = raw_row['liczba_glosow_kandydat_b']
        vote_sum = liczba_a + liczba_b

        ready_row = {
            'numer': numer,
            'nazwa': raw_row['nazwa'],
            'liczba_a': liczba_a,
            'liczba_b': liczba_b,
            'liczba_waznych_glosow': vote_sum,
            'kod': raw_row['kod'],
            'kategoria': category,
            'procent_a_tekst': format_percent(liczba_a, vote_sum) if vote_sum else "-",
            'procent_b_tekst': format_percent(liczba_b, vote_sum) if vote_sum else "-"
        }
        ready_rows.append(ready_row)

    return ready_rows


class ResultsView(TemplateView):
    template_name = "wyniki/results.html"


class ResultsDataView(View):
    def get(self, request):
        candidates = list(models.Kandydat.objects.all())
        statistics = ElectionStatistics(candidates)
        data = {
            'general': statistics.get_general_statistics(),
            'candidates': [{"pk": candidate.pk, "name": candidate.nazwa} for candidate in candidates],
            'tables': {
                'voivodeship': prepare_table(statistics.get_statistics("voivodeship"), 'voivodeship'),
                'commune_type': prepare_table(statistics.get_statistics("commune_type"), 'commune_type'),
                'commune_size': prepare_table(statistics.get_statistics("commune_size"), 'commune_size')
            }
        }
        return JsonResponse(data)

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super(ResultsDataView, self).dispatch(request, *args, *kwargs)


class CommuneListJsonView(View):

    def get(self, request, category, code):
        candidates = list(models.Kandydat.objects.all())
        statistics = ElectionStatistics(candidates)
        commune_list = statistics.get_commune_list(category, code)
        return JsonResponse({"communeList": commune_list, 'status': 'OK'})


class ChangeResultsJsonView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = forms.ChangeResults(request.POST)
        if form.is_valid():
            try:
                form.save(request.user)
            except forms.OutdatedModificationError as e:
                return JsonResponse({'status': 'outdatedModification',
                                     'modified': e.last.strftime('%c'),
                                     'user': e.user.username})
            except ValidationError as e:
                return JsonResponse({"status": "saveFailed", "messageDict": e.message_dict})
            else:
                return JsonResponse({'status': 'OK'})
        else:
            return JsonResponse({
                'status': 'formError',
                'formErrors': form.errors
            })


class AjaxLogin(View):

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            raise PermissionDenied("Login failed")
        else:
            login(request, user)
            return JsonResponse({"status": "OK"})


class Username(View):

    def get(self, request):
        data = {
            'is_authenticated': request.user.is_authenticated(),
            'username': request.user.username,
        }
        return JsonResponse(data)
