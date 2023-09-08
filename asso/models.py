from datetime import timedelta

from django.core import validators
from django.db import models
from django.utils.datetime_safe import datetime

import inventory


class Member(models.Model):
    ROLES = (
        ("member", "Membre"),
        ("member+", "Membre +"),
        ("not member", "Non membre"),
        ("board", "Bureau"),
    )
    name = models.CharField("nom", unique=True, max_length=255)
    mail = models.EmailField("email")
    tel = models.CharField("tel", max_length=12, blank=True)
    max_loans = models.PositiveIntegerField("nombre d'emprunts maximum", default=1,
                                            help_text="nombre d'emprunts simultanés maximum")
    loan_length = models.PositiveIntegerField("durée d'emprunt", default=30,
                                              help_text="durée maximale d'un emprunt en jours")
    bail = models.FloatField("caution", default=0, help_text="en euros", validators=[
        validators.MinValueValidator(0)
    ])
    last_loan = models.DateField("date du dernier emprunt", editable=False, blank=True, null=True)
    role_bdm = models.CharField("rôle au Club BDManga", max_length=64, choices=ROLES)
    role_alir = models.CharField("rôle à l'Alir", max_length=64, choices=ROLES)
    archived = models.BooleanField("ancien membre", default=False)
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    @property
    def nb_loans(self):
        return self.loan_set.count()
    nb_loans.fget.short_description = "nb d'emprunts"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "membre"
        ordering = ["-date_added"]


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="membre")
    book = models.ForeignKey(inventory.models.Book, on_delete=models.CASCADE, verbose_name="livre")
    loan_start = models.DateField("date de début", default=datetime.now)
    late_return = models.DateField("date de retour maximum", editable=False,
                                   help_text="date avant laquelle le livre devra être rendu")
    loan_return = models.DateField("date de retour", blank=True, null=True,
                                   help_text="laisser vide jusqu'au retour")

    def __str__(self):
        return f"{self.member} - {self.book.name}"

    def save(self, *args, **kwargs):
        self.late_return = self.loan_start + timedelta(days=self.member.loan_length)  # might make this a property ?
        self.book.available = self.loan_return is not None
        self.book.save()
        super().save(*args, **kwargs)

    def return_book(self):
        self.loan_return = datetime.now()
        self.save()

    class Meta:
        verbose_name = "emprunt"
        unique_together = ('member', 'book', 'loan_start')
        ordering = ["-loan_start"]
