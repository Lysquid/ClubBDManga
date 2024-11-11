from django.core import validators
from django.db import models


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
        ("manga", "manga"),
        ("comics", "comic"),
        ("novel", "roman")
    ]
    id = models.CharField("code", primary_key=True, max_length=5, validators=[
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

    @property
    def reference(self):
        return str(self.genre.id).zfill(2) + self.id
    reference.fget.short_description = "référence"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "série"
        ordering = ["name"]


def _last_book_series():
    if Book.objects.exists() and Book.last_book_id:
        return Book.objects.get(id=Book.last_book_id).series
    return None


def _next_volume_nb():
    if Book.objects.exists() and Book.last_book_id:
        return Book.objects.get(id=Book.last_book_id).volume_nb + 1
    return None


def _last_book_condition():
    if Book.objects.exists() and Book.last_book_id:
        return Book.objects.get(id=Book.last_book_id).condition
    return None


class Book(models.Model):
    id = models.CharField("cote", primary_key=True, max_length=12, editable=False, validators=[
        validators.RegexValidator('^[0-9]{2}[A-Z0-9]{5}[0-9]{5}$')
    ])
    name = models.CharField("nom", max_length=255, blank=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, verbose_name="série", default=_last_book_series)
    volume_nb = models.PositiveIntegerField("volume", default=_next_volume_nb)
    duplicate_nb = models.PositiveIntegerField("numéro de duplicata", default=1)
    condition = models.PositiveSmallIntegerField("état", default=_last_book_condition, validators=[
        validators.MinValueValidator(1),
        validators.MaxValueValidator(10)
    ])
    date_added = models.DateField("date d'ajout", auto_now_add=True)
    comment = models.TextField("commentaire", blank=True)

    last_book_id = None

    @property
    def available(self):
        return not self.loan_set.filter(loan_return=None).exists()
    available.fget.short_description = "disponible"

    def __str__(self):
        return f"{self.series} {self.volume_nb}"

    def save(self, *args, **kwargs):
        self.id = self.series.reference + str(self.volume_nb).zfill(3) + str(self.duplicate_nb).zfill(2)
        Book.last_book_id = self.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "livre"
        unique_together = ("series", "volume_nb", "duplicate_nb")
        ordering = ["id"]
