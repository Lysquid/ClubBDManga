from django.contrib import admin

from inventory import models


class MyAdminSite(admin.AdminSite):
    site_title = "Club BDManga"
    site_header = "Club BDManga"


class SeriesAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    filter_horizontal = ["authors", "editors"]
    list_display = ["name", "id", "type", "genre"]
    list_filter = ["type"]


class BookAdmin(admin.ModelAdmin):
    search_fields = ["id"]
    autocomplete_fields = ["series"]
    list_display = ["name", "series", "volume_nb", "id", "date_added", "comment"]
    list_filter = ["available", "date_added"]


class MembersAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "role_bdm", "date_added", "last_loan", "comment"]
    list_filter = ["archived", "role_bdm", "date_added"]


class LoanAdmin(admin.ModelAdmin):
    autocomplete_fields = ["book", "member"]
    list_display = ["book", "member", "loan_start", "late_return", "loan_return"]
    list_filter = ["archived", "late_return", "loan_return"]


admin_site = MyAdminSite()

admin_site.register(models.Book, BookAdmin)
admin_site.register(models.Author)
admin_site.register(models.Series, SeriesAdmin)
admin_site.register(models.Member, MembersAdmin)
admin_site.register(models.Editor)
admin_site.register(models.Loan, LoanAdmin)
admin_site.register(models.Genre)
