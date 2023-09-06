from django.contrib import admin

from inventory import models


class MyAdminSite(admin.AdminSite):
    site_title = "Club BDManga"
    site_header = "Club BDManga"


class BookInline(admin.TabularInline):
    model = models.Book
    fields = ["name", "volume_nb", "id", "duplicate_nb"]
    extra = 0


class SeriesAdmin(admin.ModelAdmin):
    inlines = [BookInline]
    search_fields = ["name"]
    filter_horizontal = ["authors", "editors"]
    list_display = ["name", "id", "type", "genre", "nb_books"]
    list_filter = ["type"]


class BookAdmin(admin.ModelAdmin):
    search_fields = ["series__name", "volume_nb"]
    autocomplete_fields = ["series"]
    list_display = ["__str__", "id", "date_added", "comment"]
    list_filter = ["available", "date_added"]


class LoanInline(admin.TabularInline):
    model = models.Loan
    extra = 0


class MembersAdmin(admin.ModelAdmin):
    # inlines = [LoanInline]   slow for some reason
    search_fields = ["name"]
    list_display = ["name", "role_bdm", "date_added", "nb_loans", "last_loan", "comment"]
    list_filter = ["archived", "role_bdm", "date_added"]


class LoanAdmin(admin.ModelAdmin):
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = ["archived", "late_return", "loan_return"]


class SeriesInline(admin.TabularInline):
    extra = 0


class SeriesAuthorsInline(SeriesInline):
    model = models.Author.series_set.through


class SeriesEditorsInline(SeriesInline):
    model = models.Editor.series_set.through


class SeriesGenreInline(SeriesInline):
    model = models.Series
    fields = ["name", "type", "id"]


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "nb_series"]
    inlines = [SeriesAuthorsInline]


class EditorAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "nb_series"]
    inlines = [SeriesEditorsInline]


class GenreAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "id", "nb_series"]
    inlines = [SeriesGenreInline]


admin_site = MyAdminSite()

admin_site.register(models.Book, BookAdmin)
admin_site.register(models.Author, AuthorAdmin)
admin_site.register(models.Series, SeriesAdmin)
admin_site.register(models.Member, MembersAdmin)
admin_site.register(models.Editor, EditorAdmin)
admin_site.register(models.Loan, LoanAdmin)
admin_site.register(models.Genre, GenreAdmin)
