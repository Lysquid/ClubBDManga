from django.contrib import admin
from django import forms
from django.db import models as db_models

from . import models
from inventory.models import Book


class DepositListFilter(admin.SimpleListFilter):
    title = "caution"
    parameter_name = "deposit"

    def lookups(self, request, model_admin):
        return [("yes", "Oui")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(deposit__gt=0)
        else:
            return queryset


@admin.register(models.Member)
class MembersAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]
    list_display = ["__str__", "membership", "deposit", "date_added", "loans_count", "comment"]
    list_filter = ["membership", DepositListFilter, "date_added"]
    actions = ["mark_has_not_paid"]

    @admin.action(description="Réinitialiser la cotisation des membres sélectionnés")
    def mark_has_not_paid(self, request, queryset):
        queryset.update(membership=models.Member.Membership.NOT_PAID)


class CurrentLoansListFilter(admin.SimpleListFilter):
    title = "en cours"
    parameter_name = "current"

    def lookups(self, request, model_admin):
        return [("yes", "Oui")]

    def queryset(self, request, queryset: models.LoanQuerySet):
        if self.value() == "yes":
            return queryset.current_loans()
        else:
            return queryset


class LateLoansListFilter(admin.SimpleListFilter):
    title = "en retard"
    parameter_name = "late"

    def lookups(self, request, model_admin):
        return [("yes", "Oui")]

    def queryset(self, request, queryset: models.LoanQuerySet):
        if self.value() == "yes":
            return queryset.late_loans()
        else:
            return queryset


def get_next_volume(book: Book):
    try:
        return Book.objects.get(series=book.series, volume_nb=book.volume_nb + 1, duplicate_nb=1)
    except Book.DoesNotExist:
        return None


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
    search_fields = ["book__series__name", "book__volume_nb", "member__first_name", "member__last_name"]
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = [CurrentLoansListFilter, LateLoansListFilter, "loan_return"]
    actions = ["mark_returned"]

    @admin.action(description="Marquer les emprunts sélectionnés comme rendus")
    def mark_returned(self, request, queryset):
        for loan in queryset:
            loan.return_book()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            # Quickly add loans in bulk by pre-filling the fields from the last loan
            if models.Loan.objects.exists():
                latest_loan = models.Loan.objects.latest("id")
                form.base_fields['member'].initial = latest_loan.member
                form.base_fields['book'].initial = get_next_volume(latest_loan.book)
        return form


@admin.register(models.News)
class NewsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    list_display = ["title", "date"]
    search_fields = ["title"]
    list_filter = ["date"]
    formfield_overrides = {
        db_models.CharField: {'widget': forms.TextInput(attrs={'size': '100'})},
        db_models.TextField: {'widget': forms.Textarea(attrs={'rows': 40, 'cols': 100})},
    }


@admin.register(models.Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    formfield_overrides = {
        db_models.TextField: {'widget': forms.Textarea(attrs={'rows': 30, 'cols': 100})},
    }
