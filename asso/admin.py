from django.contrib import admin

from . import models


class LoanInline(admin.TabularInline):
    model = models.Loan
    extra = 0


class BailListFilter(admin.SimpleListFilter):
    title = "caution"
    parameter_name = "bail"

    def lookups(self, request, model_admin):
        return [(True, "oui")]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(bail__gt=0)


@admin.register(models.Member)
class MembersAdmin(admin.ModelAdmin):
    # inlines = [LoanInline]  # slow for some reason
    search_fields = ["first_name", "last_name"]
    list_display = ["__str__", "has_paid", "can_make_loan", "bail", "date_added", "nb_loans", "comment"]
    list_filter = ["has_paid", "can_make_loan", BailListFilter, "date_added"]
    actions = ["mark_has_not_paid"]

    @admin.action(description="Réinitialiser la cotisation des membres sélectionnés")
    def mark_has_not_paid(self, request, queryset):
        queryset.update(has_paid=False)


class CurrentLoansListFilter(admin.SimpleListFilter):
    title = "en cours"
    parameter_name = "current"

    def lookups(self, request, model_admin):
        return [(True, "oui")]

    def queryset(self, request, queryset: models.LoanQuerySet):
        if self.value():
            return queryset.current_loans()


class LateLoansListFilter(admin.SimpleListFilter):
    title = "en retard"
    parameter_name = "late"

    def lookups(self, request, model_admin):
        return [(True, "oui")]

    def queryset(self, request, queryset: models.LoanQuerySet):
        if self.value():
            return queryset.late_loans()


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
    search_fields = ["book__series__name", "book__volume_nb", "member__name"]
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = [CurrentLoansListFilter, LateLoansListFilter, "loan_return"]
    actions = ["mark_returned"]

    @admin.action(description="Marquer les emprunts sélectionnés comme rendus")
    def mark_returned(self, request, queryset):
        for loan in queryset:
            loan.return_book()
