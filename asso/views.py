from datetime import datetime

from django.db.models import Count
from django.views import generic
from inventory.models import Book, Series, Author
from asso.models import Member, Loan, News, Page


class HomePageView(generic.TemplateView):
    template_name = "asso/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["text_accueil"] = Page.objects.get_or_create(identifier="accueil")[0].content
        return context


class StatsPageView(generic.TemplateView):
    template_name = "asso/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["top_series"] = Series.objects.annotate(
            nb_members=Count('book__loan__member', distinct=True),
            nb_loans=Count('book__loan')
        ).filter(nb_loans__gt=0).order_by('-nb_members', '-nb_loans')[:10]

        context["books"] = Book.objects.all()
        context["types"] = {}
        for book_type, type_name in Series.TYPES:
            context["types"][type_name] = Book.objects.filter(series__type=book_type)
        context["authors"] = Author.objects.filter(series__isnull=False).distinct()
        context["series"] = Series.objects.all()
        context["members"] = Member.objects.filter(has_paid=True)
        context["loans"] = Loan.objects.filter(member__has_paid=True)

        return context


class NewsListView(generic.ListView):
    model = News
    queryset = News.objects.filter(date__lte=datetime.today())


class NewsDetailView(generic.DetailView):
    model = News
