from django.http import HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import render

from inventory.models import Series


def index(request):
    return HttpResponse("Inventaire ClubBDM")


class SeriesListView(ListView):
    model = Series
