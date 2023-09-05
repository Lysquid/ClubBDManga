from django.contrib import admin

from inventory import models


class MyAdminSite(admin.AdminSite):
    site_title = "Club BDManga"
    site_header = "Club BDManga"


admin_site = MyAdminSite()

admin_site.register(models.Book)
admin_site.register(models.Author)
admin_site.register(models.Series)
admin_site.register(models.Member)
admin_site.register(models.Editor)
admin_site.register(models.Loan)
admin_site.register(models.Genre)
