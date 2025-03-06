from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import requests
from django.conf import settings
from .models import Tournament, CustomUser, TournamentRegistration, GuestParticipant

@receiver(post_save, sender=Tournament)
def handle_tournament_status_change(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return
    
    try:
        old_tournament = Tournament.objects.get(pk=instance.pk)
    except Tournament.DoesNotExist:
        return
    
    if old_tournament.is_canceled != instance.is_canceled:
        if instance.is_canceled:
            send_cancellation_notifications(instance)
        else:
            send_reactivation_notifications(instance)

def send_cancellation_notifications(tournament):
    # Для администраторов
    admins = CustomUser.objects.filter(is_staff=True)
    for admin in admins:
        if admin.telegram_id:
            send_telegram_message(
                admin.telegram_id,
                f"🚨 Турнир {tournament.name} отменён!\n"
                f"Причина: недостаточно участников ({tournament.participants.count() + tournament.guestparticipant_set.count()}/{tournament.min_participants})"
            )
    
    # Для участников
    all_participants = list(tournament.participants.all()) + list(tournament.guestparticipant_set.filter(user_account__isnull=False))
    for participant in all_participants:
        telegram_id = getattr(participant, 'telegram_id', None) or getattr(participant.user_account, 'telegram_id', None)
        if telegram_id:
            send_telegram_message(
                telegram_id,
                f"😔 Турнир {tournament.name} отменён\n"
                f"Дата: {tournament.date}\n"
                f"Зарегистрировано участников: {tournament.participants.count() + tournament.guestparticipant_set.count()}"
            )

def send_reactivation_notifications(tournament):
    all_participants = list(tournament.participants.all()) + list(tournament.guestparticipant_set.filter(user_account__isnull=False))
    for participant in all_participants:
        telegram_id = getattr(participant, 'telegram_id', None) or getattr(participant.user_account, 'telegram_id', None)
        if telegram_id:
            send_telegram_message(
                telegram_id,
                f"🎉 Турнир {tournament.name} снова активен!\n"
                f"Дата: {tournament.date}\n"
                f"Текущее количество участников: {tournament.participants.count() + tournament.guestparticipant_set.count()}"
            )

@receiver([post_save, post_delete], sender=TournamentRegistration)
def update_on_registration_change(sender, instance, **kwargs):
    instance.tournament.check_participants()

@receiver([post_save, post_delete], sender=GuestParticipant)
def update_on_guest_change(sender, instance, **kwargs):
    instance.tournament.check_participants()

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
