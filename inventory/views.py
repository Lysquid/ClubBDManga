from django.http import HttpResponse
from django.views import generic
from django.shortcuts import render

from inventory.models import Series


class HomePageView(generic.TemplateView):
    template_name = "inventory/home.html"


class SeriesListView(generic.ListView):
    model = Series


class SeriesDetailView(generic.DetailView):
    model = Series
