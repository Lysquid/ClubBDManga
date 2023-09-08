from datetime import timedelta

from django.db import models
from django.core import validators
from django.utils.datetime_safe import datetime


class Author(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)

    @property
    def nb_series(self):
        return self.series_set.count()
    nb_series.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "auteur"
        ordering = ["name"]


class Editor(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)

    @property
    def nb_series(self):
        return self.series_set.count()
    nb_series.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "éditeur"
        ordering = ["name"]


class Genre(models.Model):
    name = models.CharField("nom", unique=True, max_length=64)

    @property
    def nb_series(self):
        return self.series_set.count()
    nb_series.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "genre"
        ordering = ["name"]


class Series(models.Model):
    TYPES = [
        ("bd", "BD"),
        ("manga", "Manga"),
        ("comics", "Comics"),
        ("novel", "Roman")
    ]
    id = models.CharField("référence", primary_key=True, max_length=5, validators=[
        validators.RegexValidator('^[A-Z0-9]{5}$')
    ])
    name = models.CharField("nom", max_length=255)
    type = models.CharField("type", max_length=16, choices=TYPES)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="genre")
    authors = models.ManyToManyField(Author, verbose_name="auteurs")
    editors = models.ManyToManyField(Editor, verbose_name="éditeurs")

    @property
    def nb_books(self):
        return self.book_set.count()
    nb_books.fget.short_description = "nombre de volumes"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "série"
        ordering = ["id"]


class Book(models.Model):
    id = models.CharField("cote", primary_key=True, max_length=12, editable=False, validators=[
        validators.RegexValidator('^[0-9]{2}[A-Z0-9]{5}[0-9]{5}$')
    ])
    name = models.CharField("nom", max_length=255, blank=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, verbose_name="série")
    volume_nb = models.PositiveIntegerField("volume")
    duplicate_nb = models.PositiveIntegerField("numéro de duplicata", default=1)
    condition = models.PositiveSmallIntegerField("état", validators=[
        validators.MinValueValidator(1),
        validators.MaxValueValidator(10)
    ])
    date_added = models.DateField("date d'ajout", auto_now_add=True)
    comment = models.TextField("commentaire", blank=True)

    @property
    def available(self):
        if hasattr(self, "loan_set"):
            return self.loan_set.count() == 0
        else:
            return False

    def __str__(self):
        return f"{self.series} {self.volume_nb}"

    def save(self, *args, **kwargs):
        self.id = "".join((
            str(self.series.genre.id).zfill(2),
            self.series.id,
            str(self.volume_nb).zfill(3),
            str(self.duplicate_nb).zfill(2)
        ))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "livre"
        unique_together = ("series", "volume_nb", "duplicate_nb")
        ordering = ["id"]


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
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="livre")
    loan_start = models.DateField("date de début", default=datetime.now)
    late_return = models.DateField("date de retour maximum", editable=False,
                                   help_text="date avant laquelle le livre devra être rendu")
    loan_return = models.DateField("date de retour", blank=True, null=True,
                                   help_text="laisser vide jusqu'au retour")

    def __str__(self):
        return f"{self.member} - {self.book.name}"

    def save(self, *args, **kwargs):
        self.late_return = self.loan_start + timedelta(days=self.member.loan_length)  # might make this a property ?
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "emprunt"
        unique_together = ('member', 'book', 'loan_start')
        ordering = ["-loan_start"]
