# Generated by Django 4.2.4 on 2023-09-08 19:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('asso', '0008_member_last_name_alter_member_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='name',
            new_name='first_name',
        ),
        migrations.AlterField(
            model_name='member',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='compte'),
        ),
    ]
