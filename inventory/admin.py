from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea

from inventory import models


class AvailableListFilter(admin.SimpleListFilter):
    title = "disponible"
    parameter_name = "available"

    def lookups(self, request, model_admin):
        return [("no", "Non")]

    def queryset(self, request, queryset):
        if self.value() == "no":
            return queryset.filter(loan__isnull=False, loan__loan_return=None)
        else:
            return queryset


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ["call_number"]
    search_fields = ["series__name", "volume_nb"]
    autocomplete_fields = ["series"]
    list_display = ["__str__", "call_number", "date_added", "comment"]
    list_filter = [AvailableListFilter, "date_added"]


class BookInline(admin.TabularInline):
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 1})},
    }
    model = models.Book
    fields = ["name", "volume_nb", "duplicate_nb", "condition", "comment"]
    extra = 0


@admin.register(models.Series)
class SeriesAdmin(admin.ModelAdmin):
    inlines = [BookInline]
    search_fields = ["name"]
    filter_horizontal = ["authors", "editors"]
    list_display = ["name", "code", "type", "genre", "nb_books"]
    list_filter = ["type"]


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
