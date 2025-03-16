from abc import ABC, abstractmethod
from django.contrib.auth import get_user_model
from django.conf import settings
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task, on_commit_task
import requests

CustomUser = get_user_model()

class NotificationStrategy(ABC):
    @abstractmethod
    def get_user_registration_message(self, is_created: bool) -> str: ...

    @abstractmethod
    def get_admin_registration_message(self, is_created: bool) -> str: ...
    
    @abstractmethod
    def get_admin_group(self) -> str: ...
    
    @abstractmethod
    def get_cancellation_message(self, for_admin: bool) -> str: ...
    
    @abstractmethod
    def get_reactivation_message(self) -> str: ...

class BaseNotificationStrategy(NotificationStrategy):
    def __init__(self, tournament, user=None, guest=None):
        self.user = user
        self.guest = guest
        self.tournament = tournament
        self.participants_count = self._calculate_participants_count()
    
    def _calculate_participants_count(self):
        return (
            self.tournament.participants.count() + 
            self.tournament.guestparticipant_set.count()
        )

    def _get_common_details(self) -> str:
        return (
            f"Дата: {self.tournament.date} время: {self.tournament.start_time}\n"
            f"Участников: {self.participants_count}"
        )
    
    def _get_all_participants(self):
        participants = list(self.tournament.participants.all())
        guests = list(self.tournament.guestparticipant_set.filter(user_account__isnull=False))
        return participants + guests
    
    def _send_to_admins(self, message: str):
        admins = CustomUser.objects.filter(
            is_staff=True,
            groups__name=self.get_admin_group()
        )
        for admin in admins:
            if admin.telegram_id:
                send_telegram_message(admin.telegram_id, message)
    
    def _send_to_participants(self, message: str):
        for participant in self._get_all_participants():
            telegram_id = getattr(participant, 'telegram_id', None) or \
                        getattr(participant.user_account, 'telegram_id', None)
            if telegram_id:
                send_telegram_message(telegram_id, message)

    def get_admin_registration_message(self, is_created: bool) -> str:
        if self.guest:
            base = "🎉 {user} зарегистрировал {guest} в \"{name}\"\n" if is_created \
                else "😔 {user} отменил регистрацию {guest} в \"{name}\"\n"
        else:
            base = "🎉 {user} зарегистрировался в \"{name}\"\n" if is_created \
                else "😔 {user} отменил регистрацию в \"{name}\"\n"
        return base.format(user=self.user, name=self.tournament.name, guest=self.guest) + self._get_common_details()

    def get_user_registration_message(self, is_created: bool) -> str:
        if self.guest:
            return self._get_guest_registration_message(is_created=is_created)
        return self._get_user_registration_message(is_created=is_created)

# 3. Конкретные стратегии
class TournamentNotificationStrategy(BaseNotificationStrategy):
    def _get_user_registration_message(self, is_created: bool) -> str:
        base = "🎉 Вы успешно зарегистрировались на турнир {name}\n" if is_created \
            else "😔 Регистрация в турнире {name} отменена\n"
        return base.format(name=self.tournament.name) + self._get_common_details()
    
    def _get_guest_registration_message(self, is_created: bool) -> str:
        base = "🎉 Вы успешно зарегистрировали {guest} на турнир \"{name}\"\n" if is_created \
            else "😔 Регистрация {guest} в турнире \"{name}\" отменена\n"
        return base.format(name=self.tournament.name, guest=self.guest) + self._get_common_details()
    
    def get_admin_group(self) -> str:
        return "Tournament managers"
    
    def get_cancellation_message(self, for_admin: bool) -> str:
        if for_admin:
            return (
                f"🚨 Турнир {self.tournament.name} отменён!\n"
                f"{self._get_common_details()}"
                f"Причина: недостаточно участников ({self.participants_count}/"
                f"{self.tournament.min_participants})"
            )
        return (
            f"😔 Турнир {self.tournament.name} отменён\n"
            f"{self._get_common_details()}"
        )
    
    def get_reactivation_message(self) -> str:
        return (
            f"🎉 Турнир {self.tournament.name} снова активен!\n"
            f"{self._get_common_details()}"
        )

class TrainingNotificationStrategy(BaseNotificationStrategy):
    def _get_user_registration_message(self, is_created: bool) -> str:
        base = "🎉 Вы успешно зарегистрировались на тренировку \"{name}\"\n" if is_created \
            else "😔 Регистрация в тренировке \"{name}\" отменена\n"
        return base.format(name=self.tournament.name) + self._get_common_details()
    
    def _get_guest_registration_message(self, is_created: bool) -> str:
        base = "🎉 Вы успешно зарегистрировали {guest} на тренировку \"{name}\"\n" if is_created \
            else "😔 Регистрация {guest} в тренировке \"{name}\" отменена\n"
        return base.format(name=self.tournament.name, guest=self.guest) + self._get_common_details()

    def get_admin_group(self) -> str:
        return "Coaches"
    
    def get_cancellation_message(self, for_admin: bool) -> str:
        if for_admin:
            return (
                f"🚨 Тренировка {self.tournament.name} отменена!\n"
                f"Причина: недостаточно участников ({self.participants_count}/"
                f"{self.tournament.min_participants})"
            )
        return (
            f"😔 Тренировка {self.tournament.name} отменена\n"
            f"{self._get_common_details()}"
        )
    
    def get_reactivation_message(self) -> str:
        return (
            f"🎉 Тренировка {self.tournament.name} снова активна!\n"
            f"{self._get_common_details()}"
        )

class NotificationStrategyFactory:
    @staticmethod
    def create(tournament, user=None, guest=None) -> NotificationStrategy:
        if tournament.is_training:
            return TrainingNotificationStrategy(tournament, user, guest)
        return TournamentNotificationStrategy(tournament, user, guest)

class NotificationService:
    def __init__(self, strategy: NotificationStrategy):
        self.strategy: BaseNotificationStrategy = strategy
    
    def send_registration_update(self, user, is_created: bool):
        admin_msg = self.strategy.get_admin_registration_message(is_created)
        message = self.strategy.get_user_registration_message(is_created)
        send_telegram_message(user.telegram_id, message)
        self.strategy._send_to_admins(admin_msg)
    
    def send_cancellation_notices(self):
        admin_msg = self.strategy.get_cancellation_message(for_admin=True)
        user_msg = self.strategy.get_cancellation_message(for_admin=False)
        self.strategy._send_to_admins(admin_msg)
        self.strategy._send_to_participants(user_msg)
    
    def send_reactivation_notices(self):
        message = self.strategy.get_reactivation_message()
        self.strategy._send_to_participants(message)
    

@task(retries=3, retry_delay=10)
def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")