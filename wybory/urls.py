"""wybory URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin

from wyniki import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.ResultsView.as_view()),
    url(r'^result-data/$', views.ResultsDataView.as_view(), name='result-data'),
    url(r'^commune-list/([a-z_]+)/([a-zA-Z0-9-ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]+)/', views.CommuneListJsonView.as_view(), name='commune-list'),
    url(r'^change-results/', views.ChangeResultsJsonView.as_view(), name='change-results'),
    url(r'^ajax-login/', views.AjaxLogin.as_view(), name='ajax-login'),
    url(r'^username/', views.Username.as_view(), name='username'),
]
