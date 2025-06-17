from django.core import validators
from django.db import models
from django.db.models import functions
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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


class Book(models.Model):
    call_number = models.CharField("cote", unique=True, db_index=True, max_length=12, editable=False, validators=[
        validators.RegexValidator('^[0-9]{2}[A-Z0-9]{5}[0-9]{5}$')
    ])
    series = models.ForeignKey(Series, verbose_name="série", on_delete=models.CASCADE)
    name = models.CharField("nom", max_length=255, blank=True,
                            help_text="Laisser vide si le tome n'a pas de nom spécial, et son nom sera automatiquement généré.")
    volume_nb = models.PositiveIntegerField("tome")
    duplicate_nb = models.PositiveIntegerField("numéro de duplicata", default=1)
    condition = models.PositiveSmallIntegerField("état", validators=[
        validators.MinValueValidator(1),
        validators.MaxValueValidator(10)
    ])
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateTimeField("date d'ajout", auto_now_add=True)
    added_by = models.ForeignKey(User, verbose_name="ajouté par", editable=False, null=True, on_delete=models.SET_NULL)

    @property
    def available(self):
        return not self.loan_set.filter(loan_return=None).exists()
    available.fget.short_description = "disponible"

    def __str__(self):
        return f"{self.series} T.{self.volume_nb}"

    def clean(self):
        book_name = self.name.lower()
        series_name = self.series.name.lower()
        if (self.name.lower() == series_name
                or (book_name.startswith(series_name) and book_name.endswith(str(self.volume_nb)))):
            raise ValidationError("Laissez le nom vide si c'est le même que la série, il sera automatiquement généré.")

    def save(self, *args, **kwargs):
        # We can't use a generated field because it doesn't support using other model fields or other generated fields
        self.call_number = self.series.call_number + str(self.volume_nb).zfill(3) + str(self.duplicate_nb).zfill(2)
        Book.last_book_id = self.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "livre"
        unique_together = ("series", "volume_nb", "duplicate_nb")
        ordering = ["call_number"]
