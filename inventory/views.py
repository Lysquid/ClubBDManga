from django.views import generic
from django.template import defaultfilters

from inventory.models import Series, Genre
from django.http import JsonResponse


class LibraryView(generic.TemplateView):
    template_name = "inventory/library.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["types"] = Series.TYPES
        context["genres"] = Genre.objects.all()
        context["languages"] = (
            (code, Series.LANGUAGES[code])
            for code in Series.objects.values_list("language", flat=True).distinct().order_by("language")
        )
        return context


class SeriesDetailView(generic.DetailView):
    model = Series
    slug_field = 'code'
    slug_url_kwarg = 'code'


def series_list(request) -> JsonResponse:
    """REST API endpoint that returns all series data for client-side filtering"""
    series = Series.objects.select_related('genre').prefetch_related('authors').all()
    
    series_data = []
    for s in series:
        series_data.append({
            'name': s.name,
            'code': s.code,
            'type': s.type,
            'type_display': s.get_type_display(),
            'genre': s.genre.name,
            'genre_display': s.genre.name,
            'language': s.language,
            'language_display': s.get_language_display(),
            'authors': [author.name for author in s.authors.all()],
            'url': f'/livre/{s.code}/'
        })
    
    return JsonResponse({'series': series_data})
