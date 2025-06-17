from datetime import timedelta

from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from inventory.models import Book


class Member(models.Model):
    first_name = models.CharField("prénom", max_length=255)
    last_name = models.CharField("nom", max_length=255)
    email = models.EmailField("email")
    tel = models.CharField("tel", max_length=15, blank=True)
    has_paid = models.BooleanField("a cotisé",
                                   help_text="Ce champ est réinitialisé tous les ans.")
    plus_membership = models.BooleanField("membre+",
                                          help_text="Les membres+ peuvent emprunter des livres.")
    bail = models.FloatField("caution déposée", default=0, help_text="en euros", validators=[
        validators.MinValueValidator(0)
    ])
    account = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="compte",
                                   help_text="Compte pour accéder à la partie admin du site (optionel).")
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    MAX_LOANS_COUNT = 5

    @property
    def loans_count(self):
        return self.loan_set.count()
    loans_count.fget.short_description = "nb d'emprunts"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if self.plus_membership and not self.has_paid:
            raise ValidationError("Un membre+ doit avoir cotisé.")

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
        late_start = timezone.now() - Loan.MAX_LOAN_LENGTH
        return self.current_loans().filter(loan_start__lt=late_start)


def can_make_loan(member_id):
    member = Member.objects.get(pk=member_id)
    if not member.has_paid or not member.plus_membership:
        raise ValidationError("Il faut être Membre+ pour pouvoir emprunter.")
    if member.loan_set.current_loans().count() > Member.MAX_LOANS_COUNT:
        raise ValidationError(f"{member} à dépassé le quota des {Member.MAX_LOANS_COUNT} emprunts maximums.")


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="membre", validators=[can_make_loan])
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="livre")
    loan_start = models.DateField("date de début", default=timezone.now)
    loan_return = models.DateField("date de retour", blank=True, null=True,
                                   help_text="Laisser vide jusqu'au retour.")
    objects = LoanQuerySet.as_manager()

    MAX_LOAN_LENGTH = timedelta(days=30)

    @property
    def late_return(self):
        return self.loan_start + Loan.MAX_LOAN_LENGTH
    late_return.fget.short_description = "date limite de retour"

    @property
    def returned(self):
        return self.loan_return is not None
    returned.fget.short_description = "emprunt rendu"

    def __str__(self):
        return f"{self.member} - {self.book.name}"

    def return_book(self):
        self.loan_return = timezone.now()
        self.save()

    class Meta:
        verbose_name = "emprunt"
        unique_together = ('member', 'book', 'loan_start')
        ordering = ["-loan_start"]


class News(models.Model):
    title = models.CharField("titre", max_length=100)
    slug = models.SlugField("adresse", unique=True,
                            help_text="Dernière partie de l'URL à laquelle on pourra trouver cet article.")
    date = models.DateField("date", default=timezone.now, help_text="""
        Si la date est dans le futur, l'article n'apparaitra pas dans les actualités avant cette date.
        Il reste accessible via son adresse.
    """)
    summary = models.CharField("résumé", max_length=400, blank=True)
    content = models.TextField("contenu", help_text="""
        Le texte doit utiliser le format Markdown.
        Pour les images, déposez les sur le Google Drive et utilisez le lien de partage.
    """)

    class Meta:
        verbose_name = "actualité"
        ordering = ["-date"]

    def __str__(self):
        return self.title


class Page(models.Model):
    description = models.CharField("description", max_length=100, blank=True)
    identifier = models.SlugField("identifiant", unique=True)
    content = models.TextField("contenu", blank=True,
                               help_text="Le texte doit utiliser le format Markdown.")

    class Meta:
        verbose_name = "page"

    def __str__(self):
        return self.description if self.description else self.identifier
