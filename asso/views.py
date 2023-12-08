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
        context["top_series"] = Loan.objects.raw(
            """
            SELECT s.*, count(DISTINCT l.member_id) as nb_members, count(l.id) as nb_loans
            FROM inventory_series s JOIN inventory_book b ON s.id=b.series_id JOIN asso_loan l ON b.id=l.book_id
            GROUP BY s.id
            ORDER BY nb_members DESC, nb_loans DESC
            LIMIT 10;
            """
        )
        context["books"] = Book.objects
        context["types"] = {}
        for book_type, type_name in Series.TYPES:
            context["types"][type_name] = Book.objects.filter(series__type=book_type)
        context["authors"] = Author.objects.filter(series__isnull=False).distinct()
        context["series"] = Series.objects
        context["members"] = Member.objects.filter(has_paid=True)
        context["loans"] = Loan.objects.filter(member__has_paid=True)
        return context
