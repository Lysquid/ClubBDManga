from django.views import generic

from inventory.models import Series


class SeriesListView(generic.ListView):
    model = Series


class SeriesDetailView(generic.DetailView):
    model = Series
    
    def get_queryset(self):  # new
        object_list = Series.objects
        query = self.request.GET.get("search")
        if query:
            object_list = object_list.filter(name__icontains=query)
        return object_list
