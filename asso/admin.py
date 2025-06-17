from django.contrib import admin
from django import forms
from django.db import models as db_models

from . import models
from inventory.models import Book


class BailListFilter(admin.SimpleListFilter):
    title = "caution"
    parameter_name = "bail"

    def lookups(self, request, model_admin):
        return [("yes", "Oui")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(bail__gt=0)
        else:
            return queryset


@admin.register(models.Member)
class MembersAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]
    list_display = ["__str__", "has_paid", "plus_membership", "bail", "date_added", "loans_count", "comment"]
    list_filter = ["has_paid", "plus_membership", BailListFilter, "date_added"]
    actions = ["mark_has_not_paid"]

    @admin.action(description="Réinitialiser la cotisation des membres sélectionnés")
    def mark_has_not_paid(self, request, queryset):
        queryset.update(has_paid=False, plus_membership=False)


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


def get_last_loan_member():
    if models.Loan.objects.exists():
        return models.Loan.objects.latest("id").member
    return None


def get_last_loan_book():
    if models.Loan.objects.exists():
        latest_book = models.Loan.objects.latest("id").book
        try:
            return Book.objects.get(series=latest_book.series, volume_nb=latest_book.volume_nb + 1, duplicate_nb=1)
        except Book.DoesNotExist:
            return None
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
            form.base_fields['member'].initial = get_last_loan_member()
            form.base_fields['book'].initial = get_last_loan_book()
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
