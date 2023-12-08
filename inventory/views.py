from django.db.models import Q
from django.views import generic

from inventory.models import Series, Genre


class SeriesListView(generic.ListView):
    model = Series

    def get_queryset(self):
        object_list = Series.objects.all()

        search = self.request.GET.get("search")
        if search:
            object_list = object_list.filter(Q(name__icontains=search) | Q(authors__name__icontains=search))

        author = self.request.GET.get("author")
        if author:
            object_list = object_list.filter(authors__name__exact=author)

        editor = self.request.GET.get("editor")
        if editor:
            object_list = object_list.filter(editors__name__exact=editor)

        book_type = self.request.GET.get("type")
        if book_type:
            object_list = object_list.filter(type__exact=book_type)

        genre = self.request.GET.get("genre")
        if genre:
            object_list = object_list.filter(genre__name__exact=genre)

        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["types"] = Series.TYPES
        context["genres"] = Genre.objects.all()
        return context


class SeriesDetailView(generic.DetailView):
    model = Series
