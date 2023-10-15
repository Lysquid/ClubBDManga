from django.views import generic

from inventory.models import Series


class SeriesListView(generic.ListView):
    model = Series

    def get_queryset(self):
        print("in get_queryset")
        object_list = Series.objects.all()
        query = self.request.GET.get("search")
        if query:
            object_list = object_list.filter(name__icontains=query)
        return object_list


class SeriesDetailView(generic.DetailView):
    model = Series
