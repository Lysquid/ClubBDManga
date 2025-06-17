from django.contrib import admin
from django.db.models import TextField
from django.forms import Textarea

from inventory import models
from datetime import timedelta
from django.utils import timezone

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


def get_last_book(user):
    last_week = timezone.now() - timedelta(weeks=1)
    return models.Book.objects.filter(added_by=user, date_added__gte=last_week).order_by('-date_added').first()


def get_last_book_series(user):
    last_book = get_last_book(user)
    return last_book.series if last_book else None


def get_next_volume_nb(user):
    last_book = get_last_book(user)
    return last_book.volume_nb + 1 if last_book else 1


def get_last_book_condition(user):
    last_book = get_last_book(user)
    return last_book.condition if last_book else None


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ["call_number"]
    search_fields = ["series__name", "volume_nb"]
    autocomplete_fields = ["series"]
    list_display = ["__str__", "call_number", "date_added_short", "comment"]
    list_filter = [AvailableListFilter, "date_added"]

    def date_added_short(self, obj):
        return obj.date_added.date()
    date_added_short.short_description = "date d'ajout"

    def save_model(self, request, obj, _, change):
        if not change:
            obj.added_by = request.user
        obj.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            # Quickly add books in bulk by pre-filling the fields from the last book
            form.base_fields['series'].initial = get_last_book_series(request.user)
            form.base_fields['volume_nb'].initial = get_next_volume_nb(request.user)
            form.base_fields['condition'].initial = get_last_book_condition(request.user)
        return form


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
    list_display = ["__str__", "call_number", "type", "genre", "books_count"]
    list_filter = ["type", "language", "genre"]


class SeriesInline(admin.TabularInline):
    extra = 0

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SeriesAuthorsInline(SeriesInline):
    model = models.Author.series_set.through


class SeriesEditorsInline(SeriesInline):
    model = models.Editor.series_set.through


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "series_count"]
    inlines = [SeriesAuthorsInline]


@admin.register(models.Editor)
class EditorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "series_count"]
    inlines = [SeriesEditorsInline]


@admin.register(models.Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]
