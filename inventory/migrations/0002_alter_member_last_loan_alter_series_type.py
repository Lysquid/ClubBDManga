# Generated by Django 4.2.4 on 2023-09-05 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='last_loan',
            field=models.DateField(blank=True, editable=False, verbose_name='date du dernier emprunt'),
        ),
        migrations.AlterField(
            model_name='series',
            name='type',
            field=models.CharField(choices=[('bd', 'BD'), ('manga', 'manga'), ('comics', 'comics'), ('novel', 'roman')], max_length=16, verbose_name='type'),
        ),
    ]
