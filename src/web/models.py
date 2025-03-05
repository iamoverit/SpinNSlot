from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, datetime

class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        if self.first_name.strip():
            return self.first_name + ' ' + self.last_name
        return self.username

class Customers(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название уникальное
    phone_number = models.CharField(max_length=100)       # Номер телефона, уникальное
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания записи
    updated_at = models.DateTimeField(auto_now=True)      # Дата последнего обновления
    working_hours_start = models.TimeField(default='10:00')  # Время начала работы по умолчанию
    working_hours_end = models.TimeField(default='22:00')    # Время окончания работы по умолчанию

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_time_slots()

    def update_time_slots(self):
        # Delete existing TimeSlot entries for this customer
        TimeSlot.objects.filter(customer=self).delete()

        # Create new TimeSlot entries with 30-minute intervals
        current_time = datetime.combine(datetime.today(), self.working_hours_start)
        end_time = datetime.combine(datetime.today(), self.working_hours_end)

        while current_time.time() < end_time.time():
            TimeSlot.objects.create(
                time_slot=current_time.time(),
                customer=self,
            )
            current_time += timedelta(minutes=30)

class ItemSlot(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Название стола, уникальное
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name="customer")  # Связь с таблицей customer
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания записи
    updated_at = models.DateTimeField(auto_now=True)      # Дата последнего обновления

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ItemSlot"
        verbose_name_plural = "ItemSlots"

class TimeSlot(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name="time_slots")  # Связь с Customers
    time_slot = models.TimeField()  # Поле для хранения времени без даты

    def __str__(self):
        return f"Visit {self.customer.name} at {self.time_slot}"

    class Meta:
        verbose_name = "TimeSlot"
        verbose_name_plural = "TimeSlots"

from django.utils import timezone

class Tournament(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name="Организатор")
    name = models.CharField(max_length=200, verbose_name="Название турнира")
    date = models.DateField(verbose_name="Дата проведения")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    tables = models.ManyToManyField(ItemSlot, verbose_name="Используемые столы")
    max_participants = models.PositiveIntegerField(verbose_name="Максимум участников")
    description = models.TextField(verbose_name="Описание")
    participants = models.ManyToManyField(
        CustomUser,
        through='TournamentRegistration',
        through_fields=('tournament', 'user'),
        verbose_name="Участники"
    )

    class Meta:
        verbose_name = "Турнир"
        verbose_name_plural = "Турниры"

    def __str__(self):
        return f"{self.name} ({self.date} {self.start_time}-{self.end_time})"

class TournamentRegistration(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, verbose_name="Турнир")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Регистрация на турнир"
        verbose_name_plural = "Регистрации на турниры"
        unique_together = ('user', 'tournament')

    def __str__(self):
        return f"{self.user} → {self.tournament}"

class UserSlot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='users')
    table = models.ForeignKey(ItemSlot, on_delete=models.CASCADE, related_name="user_item_slots")  # Связь с таблицей ItemSlot
    time =  models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="user_time_slots")  # Связь с таблицей TimeSlot
    reservation_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.time.time_slot} on {self.reservation_date}"

    class Meta:
        verbose_name = "UserSlot"
        verbose_name_plural = "UserSlots"
        constraints = [
            models.UniqueConstraint(
                fields=['table', 'time', 'reservation_date'],
                name='unique_user_table_time_date'
            )
        ]
