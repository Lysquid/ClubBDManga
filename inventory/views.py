from django.db.models import Q
from django.views import generic

from inventory.models import Series


class SeriesListView(generic.ListView):
    model = Series

    def get_queryset(self):
        object_list = Series.objects.all()
        search = self.request.GET.get("search")
        if search:
            object_list = object_list.filter(Q(name__icontains=search) | Q(authors__name__icontains=search))
        book_type = self.request.GET.get("type")
        if book_type:
            object_list = object_list.filter(type__exact=book_type)
        return object_list


class SeriesDetailView(generic.DetailView):
    model = Series
