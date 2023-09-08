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
    search_fields = ["name"]
    list_display = ["name", "can_make_loan", "date_added", "bail", "nb_loans", "comment"]
    list_filter = [BailListFilter, "archived", "date_added", "is_alir_member"]


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
    search_fields = ["book__series__name", "book__volume_nb", "member__name"]
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = ["late_return", "loan_return"]
    actions = ["mark_returned"]

    @admin.action(description="Marquer les emprunts sélectionnés comme rendus")
    def mark_returned(self, request, queryset):
        for loan in queryset:
            loan.return_book()
