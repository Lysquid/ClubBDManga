from datetime import timedelta

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.datetime_safe import datetime

import inventory


class Member(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)
    mail = models.EmailField("email")
    tel = models.CharField("tel", max_length=12, blank=True)
    bail = models.FloatField("caution déposée", default=0, help_text="en euros", validators=[
        validators.MinValueValidator(0)
    ])
    can_make_loan = models.BooleanField("membre +",
                                        help_text="Les membres + peuvent emprunter des livres")
    is_alir_member = models.BooleanField("Membre de l'ALIR", default=False)
    archived = models.BooleanField("ancien membre", default=False)
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    MAX_NB_LOANS = 10
    MAX_LOAN_LENGTH = timedelta(days=30)

    @property
    def nb_loans(self):
        return self.loan_set.count()
    nb_loans.fget.short_description = "nb d'emprunts"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "membre"
        ordering = ["-date_added"]


def can_make_loan(member_id):
    member = Member.objects.get(pk=member_id)
    if not member.can_make_loan:
        raise ValidationError("Il faut être Membre+ pour pouvoir emprunter")
    if member.loan_set.count() > Member.MAX_NB_LOANS:
        raise ValidationError(f"{member} à dépassé le quota des {Member.MAX_LOAN_LENGTH} emprunts maximums")


def _last_loan_member():
    if Loan.objects.count() > 0:
        return Loan.objects.latest("id").member
    return None


def _last_loan_book():
    if Loan.objects.count() > 0:
        return Loan.objects.latest("id").book
    return None


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="membre", validators=[can_make_loan],
                               default=_last_loan_member)
    book = models.ForeignKey(inventory.models.Book, on_delete=models.CASCADE, verbose_name="livre",
                             default=_last_loan_book)
    loan_start = models.DateField("date de début", default=datetime.now)
    late_return = models.DateField("date de retour maximum", editable=False,
                                   help_text="date avant laquelle le livre devra être rendu")
    loan_return = models.DateField("date de retour", blank=True, null=True,
                                   help_text="laisser vide jusqu'au retour")

    def __str__(self):
        return f"{self.member} - {self.book.name}"

    def save(self, *args, **kwargs):
        self.late_return = self.loan_start + Member.MAX_LOAN_LENGTH  # might make this a property ?
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
