from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

from wyniki import forms, models
from wyniki.election_statistics import ElectionStatistics


class ResultsView(TemplateView):
    template_name = "wyniki/results.html"

    def get_context_data(self, **kwargs):
        candidates = list(models.Kandydat.objects.all())
        statistics = ElectionStatistics(candidates)
        data = statistics.get_general_statistics()
        data['voivodeship_statistics'] = statistics.get_statistics("voivodeship")
        data['commune_type_statistics'] = statistics.get_statistics("commune_type")
        data['commune_size_statistics'] = statistics.get_statistics("commune_size")
        data['candidates'] = statistics.get_candidates()
        data['candidates_data'] = ({'model': model, 'summary': summary}
                                   for model, summary in zip(data['candidates'], data['candidates_summary']))

        return data


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
                form.save()
            except forms.OutdatedModificationError as e:
                return JsonResponse({'status': 'outdatedModification',
                                     'modified': e.last.strftime('%c')})
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
