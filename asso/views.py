from collections import defaultdict

from django.views import generic
from inventory.models import Book, Series, Author
from asso.models import Member, Loan


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"


class StatsPageView(generic.TemplateView):
    template_name = "asso/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        count = defaultdict(list)
        for loan in Loan.objects.all():
            count[loan.book.series].append(loan.member)
        context["top_series"] = tuple(sorted((
            (len(set(members)), len(members), series) for series, members in count.items()),
            key=lambda x: x[:-1],
            reverse=True)
        )[:10]

        context["books"] = Book.objects
        context["types"] = {}
        for book_type, type_name in Series.TYPES:
            context["types"][type_name] = Book.objects.filter(series__type=book_type)
        context["authors"] = Author.objects.filter(series__isnull=False).distinct()
        context["series"] = Series.objects
        context["members"] = Member.objects.filter(has_paid=True)
        context["loans"] = Loan.objects.filter(member__has_paid=True)
        return context
