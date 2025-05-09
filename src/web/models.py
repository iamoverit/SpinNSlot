from django.db import models
from django.db.models import Q, Prefetch
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, datetime
from django.core.validators import MinValueValidator
from django.utils import timezone

class CustomUser(AbstractUser):
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        if self.first_name.strip():
            return f"{self.first_name} {self.last_name}" if self.last_name else self.first_name
        return self.username

class Customers(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        null=True,  # Временно для существующих записей
        verbose_name="Пользователь"
    )
    name = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    working_hours_start = models.TimeField(default='10:00')
    working_hours_end = models.TimeField(default='22:00')
    base_description_tournament = models.TextField(verbose_name="Базовое описание турнира", default="")
    base_description_training = models.TextField(verbose_name="Базовое описание тренировки", default="")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_time_slots()

    def update_time_slots(self):
        current_time = datetime.combine(datetime.today(), self.working_hours_start)
        end_time = datetime.combine(datetime.today(), self.working_hours_end)
        old_time_slots= TimeSlot.objects.filter(~Q(time_slot__gte=current_time) | ~Q(time_slot__lte=end_time), customer=self).all()
        old_time_slots.delete()
        while current_time.time() < end_time.time():
            TimeSlot.objects.get_or_create(
                time_slot=current_time.time(),
                customer=self,
            )
            current_time += timedelta(minutes=30)
            
    def get_time_slots(self):
        time_slots = self.time_slots.all()
        result = [{'id': slot.time_slot.strftime('%H:%M'), 'time': slot.time_slot.strftime('%H:%M')} for slot in time_slots]
        last_time = datetime.combine(datetime.today(), datetime.strptime(result[-1]['time'], "%H:%M").time()) + timedelta(minutes=30)
        result.append({'id': last_time.strftime('%H:%M'), 'time': last_time.strftime('%H:%M')})
        return result
    
class ItemSlot(models.Model):
    name = models.CharField(max_length=100, unique=True)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name="customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "ItemSlot"
        verbose_name_plural = "ItemSlots"
        ordering = ['name']

class TimeSlot(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name="time_slots")
    time_slot = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"Visit {self.customer.name} at {self.time_slot}"

    class Meta:
        verbose_name = "TimeSlot"
        verbose_name_plural = "TimeSlots"
        ordering = ['time_slot']

class TournamentQuerySet(models.QuerySet):
    def prefetch_registred_users(self):
        return self.prefetch_related(
            "guestparticipant_set",
            Prefetch(
                'tournamentregistration_set',
                queryset=TournamentRegistration.objects.prefetch_related('user'),
                to_attr='tournamentregistration_users'
            ),
        )

class TournamentManager(models.Manager):
    def get_queryset(self):
        return TournamentQuerySet(self.model, using=self._db)
    
    def prefetch_registred_users(self):
        return self.get_queryset().prefetch_registred_users()

class Tournament(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, verbose_name="Организатор")
    name = models.CharField(max_length=200, verbose_name="Название турнира")
    date = models.DateField(verbose_name="Дата проведения")
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    tables = models.ManyToManyField(ItemSlot, verbose_name="Используемые столы")
    time_slots = models.ManyToManyField(TimeSlot, verbose_name="Временные слоты")
    max_participants = models.PositiveIntegerField(verbose_name="Максимум участников")
    min_participants = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Минимум участников"
    )
    registration_deadline = models.DateTimeField(
        verbose_name="Дедлайн регистрации",
        help_text="Автоматически устанавливается за 2 часа до начала"
    )
    is_canceled = models.BooleanField(default=False, verbose_name="Отменен")
    is_finished = models.BooleanField(default=False, verbose_name="Завершен")
    is_training = models.BooleanField(default=False, verbose_name="Тренировка")
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

    objects = TournamentManager()

    def __str__(self):
        return f"{self.name} ({self.date} {self.start_time}-{self.end_time})"

    def save(self, *args, **kwargs):
        # Сначала вычисляем дедлайн
        start_datetime = timezone.make_aware(
            datetime.combine(self.date, self.start_time)
        )
        self.registration_deadline = start_datetime - timedelta(hours=2)
        super().save(*args, **kwargs)
        self.reserve_slots()

    def check_available_slots(self):
        """Проверка доступности слотов для турнира"""
        for table in self.tables.all():
            for slot in self.time_slots.filter(customer=self.customer):
                if UserSlot.objects.filter(
                    table=table,
                    time=slot,
                    reservation_date=self.date
                ).exists():
                    return False
        return True

    def reserve_slots(self):
        """Бронирование слотов с привязкой к турниру"""
        if self.time_slots.exists():
            self.time_slots.remove(*[slot.id for slot in self.time_slots.all()])
        slots = TimeSlot.objects.filter(
            customer=self.customer,
            time_slot__gte=self.start_time,
            time_slot__lt=self.end_time,
        ).all()
        self.time_slots.add(*[slot.id for slot in slots])

    def check_participants(self):
        total = self.participants.count() + self.guestparticipant_set.count()
        new_status = total < self.min_participants

        if self.is_canceled != new_status:
            self.is_canceled = new_status
            self.save(update_fields=['is_canceled'])
    
    @staticmethod
    def get_time_choices():
        return [(ts.time.strftime('%H:%M'), ts.time.strftime('%H:%M')) for ts in TimeSlot.objects.all()]

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

class GuestParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='guestparticipant_set')
    registered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registered_guests')
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    user_account = models.OneToOneField(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='guest_profile'
    )

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    class Meta:
        verbose_name = "Гостевой участник"
        verbose_name_plural = "Гостевые участники"

class UserSlot(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='users')
    table = models.ForeignKey(ItemSlot, on_delete=models.CASCADE, related_name="user_item_slots")
    time =  models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="user_time_slots")
    reservation_date = models.DateField(default=timezone.now)
    reason = models.CharField(max_length=255, blank=True, null=True)

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
