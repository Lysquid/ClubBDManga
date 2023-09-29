from datetime import timedelta

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.datetime_safe import datetime

from inventory.models import Book


class Member(models.Model):
    first_name = models.CharField("prénom", max_length=255)
    last_name = models.CharField("nom", max_length=255)
    email = models.EmailField("email")
    tel = models.CharField("tel", max_length=12, blank=True)
    has_paid = models.BooleanField("a cotisé",
                                   help_text="Ce champ est réinitialisé tous les ans")
    can_make_loan = models.BooleanField("membre +",
                                        help_text="Les membres + peuvent emprunter des livres")
    bail = models.FloatField("caution déposée", default=0, help_text="en euros", validators=[
        validators.MinValueValidator(0)
    ])
    account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="compte",
                                   help_text="compte pour accéder à ce site")
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    MAX_NB_LOANS = 5

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


class LoanQuerySet(models.QuerySet):

    def current_loans(self):
        return self.filter(loan_return__exact=None)

    def late_loans(self):
        late_start = datetime.now() - Loan.MAX_LOAN_LENGTH
        return self.current_loans().filter(loan_start__lt=late_start)


def can_make_loan(member_id):
    member = Member.objects.get(pk=member_id)
    if not member.has_paid:
        raise ValidationError(f"{member} n'a pas encore cotisé cette année")
    if not member.can_make_loan:
        raise ValidationError("Il faut être Membre+ pour pouvoir emprunter")
    if member.loan_set.current_loans().count() > Member.MAX_NB_LOANS:
        raise ValidationError(f"{member} à dépassé le quota des {Member.MAX_NB_LOANS} emprunts maximums")


def _last_loan_member():
    if Loan.objects.exists():
        return Loan.objects.latest("id").member
    return None


def _last_loan_book():
    if Loan.objects.exists():
        latest_book = Loan.objects.latest("id").book
        try:
            return Book.objects.get(series=latest_book.series, volume_nb=latest_book.volume_nb + 1)
        except models.ObjectDoesNotExist:
            return None
    return None


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="membre", validators=[can_make_loan],
                               default=_last_loan_member)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="livre",
                             default=_last_loan_book)
    loan_start = models.DateField("date de début", default=datetime.now)
    loan_return = models.DateField("date de retour", blank=True, null=True,
                                   help_text="laisser vide jusqu'au retour")
    objects = LoanQuerySet.as_manager()

    MAX_LOAN_LENGTH = timedelta(days=30)

    @property
    def late_return(self):
        return self.loan_start + Loan.MAX_LOAN_LENGTH
    late_return.fget.short_description = "date de retour maximum"

    @property
    def returned(self):
        return self.loan_return is not None
    late_return.fget.short_description = "emprunt rendu"

    def __str__(self):
        return f"{self.member} - {self.book.name}"

    def save(self, *args, **kwargs):
        self.book.available = self.returned
        self.book.save()
        super().save(*args, **kwargs)

    def return_book(self):
        self.loan_return = datetime.now()
        self.save()

    class Meta:
        verbose_name = "emprunt"
        unique_together = ('member', 'book', 'loan_start')
        ordering = ["-loan_start"]
