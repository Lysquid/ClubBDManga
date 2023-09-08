from datetime import timedelta

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.datetime_safe import datetime
from django.contrib.auth.models import User

import inventory


class Member(models.Model):
    first_name = models.CharField("prénom", max_length=255)
    last_name = models.CharField("nom", max_length=255)
    email = models.EmailField("email")
    tel = models.CharField("tel", max_length=12, blank=True)
    has_paid = models.BooleanField("a cotisé",
                                   help_text="Ce champ est réinitialisé tous les ans")
    can_make_loan = models.BooleanField("membre +",
                                        help_text="Les membres + peuvent emprunter des livres")
    is_alir_member = models.BooleanField("membre de l'ALIR", default=False)
    bail = models.FloatField("caution déposée", default=0, help_text="en euros", validators=[
        validators.MinValueValidator(0)
    ])
    account = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, verbose_name="compte",
                                   help_text="compte pour accéder à ce site")
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    MAX_NB_LOANS = 10
    MAX_LOAN_LENGTH = timedelta(days=30)

    @property
    def nb_loans(self):
        return self.loan_set.count()
    nb_loans.fget.short_description = "nb d'emprunts"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.account:
            self.account.first_name = self.first_name
            self.account.last_name = self.last_name
            self.account.email = self.email
            self.account.save()

    class Meta:
        verbose_name = "membre"
        ordering = ["-date_added"]


def can_make_loan(member_id):
    member = Member.objects.get(pk=member_id)
    if not member.has_paid:
        raise ValidationError(f"{member} n'a pas encore cotisé cette année")
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
