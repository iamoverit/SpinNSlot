# Generated by Django 5.1.5 on 2025-03-05 20:54

import datetime
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0003_tournament_tournamentregistration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeslot',
            name='is_booked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournament',
            name='is_canceled',
            field=models.BooleanField(default=False, verbose_name='Отменен'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='min_participants',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Минимум участников'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='registration_deadline',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 5, 20, 54, 51, 548938), verbose_name='Срок регистрации'),
        ),
        migrations.AddField(
            model_name='tournament',
            name='time_slots',
            field=models.ManyToManyField(to='web.timeslot', verbose_name='Временные слоты'),
        ),
        migrations.CreateModel(
            name='GuestParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Полное имя')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('registered_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registered_guests', to=settings.AUTH_USER_MODEL)),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guestparticipant_set', to='web.tournament')),
                ('user_account', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='guest_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Гостевой участник',
                'verbose_name_plural': 'Гостевые участники',
            },
        ),
    ]
