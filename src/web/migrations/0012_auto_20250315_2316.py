# Generated by Django 5.1.7 on 2025-03-15 23:16

from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_initial_roles(apps, schema_editor):
    Group.objects.get_or_create(name="Tournament managers")
    Group.objects.get_or_create(name="Coaches")
    Group.objects.get_or_create(name="Admins")


def delete_initial_roles(apps, schema_editor):
    Group.objects.filter(name__in=["Tournament managers", "Coaches", "Admins"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('web', '0011_alter_itemslot_options_alter_timeslot_options'),
    ]

    operations = [
        migrations.RunPython(create_initial_roles, delete_initial_roles),
    ]