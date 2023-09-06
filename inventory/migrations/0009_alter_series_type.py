# Generated by Django 4.2.4 on 2023-09-06 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_alter_book_options_alter_editor_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='series',
            name='type',
            field=models.CharField(choices=[('bd', 'BD'), ('manga', 'Manga'), ('comics', 'Comics'), ('novel', 'Roman')], max_length=16, verbose_name='type'),
        ),
    ]
