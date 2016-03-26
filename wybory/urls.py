"""wybory URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin

from wyniki import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.ResultsView.as_view())
]
