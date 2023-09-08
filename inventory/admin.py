from django.contrib import admin

from inventory import models


class BookInline(admin.TabularInline):
    model = models.Book
    fields = ["name", "volume_nb", "duplicate_nb"]
    extra = 0


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    inlines = [BookInline]
    search_fields = ["name"]
    filter_horizontal = ["authors", "editors"]
    list_display = ["name", "id", "type", "genre", "nb_books"]
    list_filter = ["type"]


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ["id"]
    search_fields = ["series__name", "volume_nb"]
    autocomplete_fields = ["series"]
    list_display = ["__str__", "id", "date_added", "comment"]
    list_filter = ["date_added"]


class LoanInline(admin.TabularInline):
    model = models.Loan
    extra = 0


@admin.register(models.Member)
class MembersAdmin(admin.ModelAdmin):
    # inlines = [LoanInline]   slow for some reason
    search_fields = ["name"]
    list_display = ["name", "role_bdm", "date_added", "nb_loans", "last_loan", "comment"]
    list_filter = ["archived", "role_bdm", "date_added"]


@admin.register(models.Loan)
class LoanAdmin(admin.ModelAdmin):
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = ["late_return", "loan_return"]


class SeriesInline(admin.TabularInline):
    extra = 0


class SeriesAuthorsInline(SeriesInline):
    model = models.Author.series_set.through


class SeriesEditorsInline(SeriesInline):
    model = models.Editor.series_set.through


class SeriesGenresInline(SeriesInline):
    model = models.Series
    fields = ["name", "type", "id"]


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "nb_series"]
    inlines = [SeriesAuthorsInline]


@admin.register(models.Editor)
class EditorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "nb_series"]
    inlines = [SeriesEditorsInline]


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "id", "nb_series"]
    inlines = [SeriesGenresInline]
