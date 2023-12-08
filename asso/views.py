from django.views import generic
from inventory.models import Book, Series
from asso.models import Member


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["books_count"] = Book.objects.count()
        context["series_count"] = Series.objects.count()
        context["member_count"] = Member.objects.filter(has_paid__exact=True).count()
        return context
