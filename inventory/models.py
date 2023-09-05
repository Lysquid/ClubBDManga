from django.db import models
from django.core import validators


class Author(models.Model):
    name = models.CharField("nom", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "auteur"


class Editor(models.Model):
    name = models.CharField("nom", unique=True, max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "éditeur"


class Genre(models.Model):
    name = models.CharField("nom", unique=True, max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "catégorie"


class Series(models.Model):
    TYPES = [
        ("bd", "BD"),
        ("manga", "manga"),
        ("comics", "comics"),
        ("novel", "roman")
    ]
    id = models.CharField("référence", primary_key=True, max_length=5, validators=[
        validators.RegexValidator('^[A-Z0-9]{5}$')
    ])
    name = models.CharField("nom", max_length=255)
    type = models.CharField("type", max_length=16, choices=TYPES)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="genre")
    authors = models.ManyToManyField(Author, verbose_name="auteurs")
    editors = models.ManyToManyField(Editor, verbose_name="éditeurs")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "série"


class Book(models.Model):
    id = models.CharField("cote", primary_key=True, max_length=12, validators=[
        validators.RegexValidator('^[0-9]{2}[A-Z0-9]{5}[0-9]{5}$')
    ])
    name = models.CharField("nom", max_length=255, blank=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, verbose_name="série")
    volume_nb = models.PositiveIntegerField("numéro de volume")
    duplicate_nb = models.PositiveIntegerField("nombre d'exemplaires", default=1)
    available = models.BooleanField("disponible", default=True)
    condition = models.PositiveSmallIntegerField("état", validators=[
        validators.MinValueValidator(1),
        validators.MaxValueValidator(10)
    ])
    date_added = models.DateField("date d'ajout", auto_now_add=True)
    comment = models.TextField("commentaire", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "livre"
        unique_together = (("series", "volume_nb", "duplicate_nb"),)


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
    role_bdm = models.CharField("rôle au ClubBDM", max_length=64, choices=ROLES)
    role_alir = models.CharField("rôle à l'Alir", max_length=64, choices=ROLES)
    archived = models.BooleanField("ancien membre", default=False)
    comment = models.TextField("commentaire", blank=True)
    date_added = models.DateField("date d'inscription", auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "membre"


class Loan(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name="membre")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name="livre")
    loan_start = models.DateField("date de début")
    late_return = models.DateField("date de retard", blank=True, null=True,
                                   help_text="date à partir de laquelle l'emprunt est en retard")
    loan_return = models.DateField("date de retour", blank=True, null=True)
    archived = models.BooleanField("archivé", default=False)

    def __str__(self):
        return f"{self.member} - {self.book}"

    class Meta:
        verbose_name = "prêt"
        unique_together = (('member', 'book', 'loan_start'),)
