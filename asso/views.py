from django.views import generic

from inventory.models import Series


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"


class SeriesListView(generic.ListView):
    model = Series


class SeriesDetailView(generic.DetailView):
    model = Series
