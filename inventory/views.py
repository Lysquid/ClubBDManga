from django.db.models import Q
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.views import generic
from django.views.decorators.http import require_POST

from inventory.models import Series, Genre
from django_htmx.middleware import HtmxDetails


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


class LibraryView(generic.TemplateView):
    template_name = "inventory/library.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["types"] = Series.TYPES
        context["genres"] = Genre.objects.all()
        return context


class SeriesDetailView(generic.DetailView):
    model = Series


@require_POST
def series_search(request: HtmxHttpRequest) -> HttpResponse:
    series = Series.objects.all()

    search = request.POST.get("search")
    if search:
        series = series.filter(Q(name__icontains=search) | Q(authors__name__icontains=search))
    book_type = request.POST.get("type")
    if book_type:
        series = series.filter(type__exact=book_type)
    genre = request.POST.get("genre")
    if genre:
        series = series.filter(genre__name__exact=genre)

    return render(
        request,
        "inventory/series_list.html",
        {"series_list": series.distinct()},
    )
