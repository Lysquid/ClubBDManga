from django.db.models import Q
from django.views import generic

from inventory.models import Series


class SeriesListView(generic.ListView):
    model = Series

    def get_queryset(self):
        object_list = Series.objects.all()
        query = self.request.GET.get("search")
        if query:
            object_list = object_list.filter(Q(name__icontains=query) | Q(authors__name__icontains=query))
        return object_list


class SeriesDetailView(generic.DetailView):
    model = Series
