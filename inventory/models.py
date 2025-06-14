from django.core import validators
from django.db import models
from django.db.models import functions
from django.core.exceptions import ValidationError


class Author(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)

    @property
    def series_count(self):
        return self.series_set.count()
    series_count.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "auteur"
        ordering = ["name"]


class Editor(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)

    @property
    def series_count(self):
        return self.series_set.count()
    series_count.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "éditeur"
        ordering = ["name"]


def validate_lowercase(value: str):
    if not value.islower():
        raise ValidationError("La valeur doit être en minuscules.")


class Genre(models.Model):

    name = models.CharField("nom", unique=True, max_length=64, validators=[validate_lowercase])

    @property
    def series_count(self):
        return self.series_set.count()
    series_count.fget.short_description = "nombre de séries"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "genre"
        ordering = ["name"]


class Series(models.Model):
    # Using lowercase singular to display in context, for example 10 comics
    TYPES = {
        "bd": "BD",
        "manga": "manga",
        "comics": "comics",
        "novel": "roman",
    }
    LANGUAGES = {
        "fr": "Français",
        "en": "English",
        "es": "Español",
        "de": "Deutsch",
        "it": "Italiano",
        "pt": "Português",
        "jp": "Japonais",
        "ch": "Chinois",
        "ru": "Russe",
        "ar": "Arabe",
    }
    name = models.CharField("nom", max_length=255)
    code = models.CharField("code", unique=True, db_index=True, max_length=5,
                            validators=[validators.RegexValidator('^[A-Z0-9]{5}$')],
                            help_text="5 caractères en majuscules (lettres et chiffres)")
    type = models.CharField("type", max_length=16, choices=TYPES)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="genre")
    language = models.CharField("langue", max_length=2, choices=LANGUAGES, default="fr")
    authors = models.ManyToManyField(Author, verbose_name="auteurs")
    editors = models.ManyToManyField(Editor, verbose_name="éditeurs")
    call_number = models.GeneratedField(
        expression=functions.Concat(
            functions.LPad(functions.Cast("genre__id", models.CharField()), 2, models.Value("0")),
            "code"
        ),
        output_field=models.CharField(unique=True, max_length=7),
        db_persist=True,
        verbose_name="référence"
    )

    @property
    def books_count(self):
        return self.book_set.count()
    books_count.fget.short_description = "nombre de volumes"

    def __str__(self):
        if self.language != "fr":
            return f"{self.name} ({self.get_language_display()})"
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Refresh the call_number materialized view
        self.refresh_from_db(fields=['call_number'])
        # Saves books in case the call number changed
        for book in self.book_set.all():
            book.save(force_update=True)

    class Meta:
        verbose_name = "série"
        ordering = ["name"]


def _last_book_series():
    if Book.objects.exists() and Book.last_book_id:
        try:
            return Book.objects.get(id=Book.last_book_id).series
        except Book.DoesNotExist:
            return None


def _next_volume_nb():
    if Book.objects.exists() and Book.last_book_id:
        try:
            return Book.objects.get(id=Book.last_book_id).volume_nb + 1
        except Book.DoesNotExist:
            return None


def _last_book_condition():
    if Book.objects.exists() and Book.last_book_id:
        try:
            return Book.objects.get(id=Book.last_book_id).condition
        except Book.DoesNotExist:
            return None


class Book(models.Model):
    call_number = models.CharField("cote", unique=True, db_index=True, max_length=12, editable=False, validators=[
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
        # We can't use a generated field because it doesn't support using other model fields or other generated fields
        self.call_number = self.series.call_number + str(self.volume_nb).zfill(3) + str(self.duplicate_nb).zfill(2)
        Book.last_book_id = self.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "livre"
        unique_together = ("series", "volume_nb", "duplicate_nb")
        ordering = ["call_number"]
