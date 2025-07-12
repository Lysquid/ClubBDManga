# Generated migration for merging has_paid and plus_membership into membership_type

from django.db import migrations, models


def migrate_membership_forward(apps, schema_editor):
    """Convert old fields to new enum field"""
    Member = apps.get_model('asso', 'Member')
    
    for member in Member.objects.all():
        if member.plus_membership:
            member.membership = 2  # MEMBER_PLUS
        elif member.has_paid:
            member.membership = 1  # MEMBER
        else:
            member.membership = 0  # NOT_PAID
        member.save()


def migrate_membership_backward(apps, schema_editor):
    """Convert new enum field back to old fields"""
    Member = apps.get_model('asso', 'Member')
    
    for member in Member.objects.all():
        if member.membership == 2:  # MEMBER_PLUS
            member.has_paid = True
            member.plus_membership = True
        elif member.membership == 1:  # MEMBER
            member.has_paid = True
            member.plus_membership = False
        else:  # NOT_PAID (0)
            member.has_paid = False
            member.plus_membership = False
        member.save()


class Migration(migrations.Migration):

    dependencies = [
        ('asso', '0023_alter_member_plus_membership_alter_news_title'),
    ]

    operations = [
        # Add the new field
        migrations.AddField(
            model_name='member',
            name='membership',
            field=models.IntegerField(
                choices=[(0, 'Pas cotisé'), (1, 'Membre'), (2, 'Membre+')],
                default=0,
                verbose_name='cotisation',
                help_text='Seuls les membres+ peuvent emprunter des livres. Ce champ est réinitialisé tous les ans.'
            ),
        ),
        
        # Migrate data from old fields to new field
        migrations.RunPython(migrate_membership_forward, migrate_membership_backward),
        
        # Remove the old fields
        migrations.RemoveField(
            model_name='member',
            name='has_paid',
        ),
        migrations.RemoveField(
            model_name='member',
            name='plus_membership',
        ),
    ]