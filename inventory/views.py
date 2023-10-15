from django.views import generic

from inventory.models import Series


class SeriesListView(generic.ListView):
    model = Series

    # queryset = Series.objects.filter(name__icontains="test")
    
    def get_queryset(self):
        print("in get_queryset")
        object_list = Series.objects.all()
        query = self.request.GET.get("search")
        print(query)
        if query:
            object_list = object_list.filter(name__icontains=query)
        return object_list


class SeriesDetailView(generic.DetailView):
    model = Series