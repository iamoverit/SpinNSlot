import datetime

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task, on_commit_task
from web.telegram_messages import NotificationService, NotificationStrategyFactory
from .models import Tournament, TournamentRegistration, GuestParticipant

@receiver(post_save, sender=Tournament)
def handle_tournament_status_change(sender, instance: Tournament, **kwargs):
    if kwargs.get('created', False):
        return
    
    try:
        old_tournament = Tournament.objects.get(pk=instance.pk)
    except Tournament.DoesNotExist:
        return

    service = NotificationService(NotificationStrategyFactory.create(instance))
    eta = datetime.datetime.combine(instance.date,instance.start_time)
    eta -= datetime.timedelta(minutes=30)
    # eta = datetime.datetime.now() + datetime.timedelta(seconds=5)
    service.send_tournament_reminder.schedule((instance), eta=eta)
    if old_tournament.is_canceled != instance.is_canceled:
        if instance.is_canceled:
            service.send_cancellation_notices(instance)
        else:
            service.send_reactivation_notices(instance)

@receiver([post_save, post_delete], sender=TournamentRegistration)
def update_on_registration_change(sender, instance: TournamentRegistration, **kwargs):
    service = NotificationService(NotificationStrategyFactory.create(instance.tournament, instance.user))
    service.send_registration_update(is_created=kwargs.get('created', False))
    # instance.tournament.check_participants()

@receiver([post_save, post_delete], sender=GuestParticipant)
def update_on_guest_change(sender, instance: GuestParticipant, **kwargs):
    service = NotificationService(NotificationStrategyFactory.create(instance.tournament, instance.registered_by, instance))
    service.send_registration_update(is_created=kwargs.get('created', False))
    # instance.tournament.check_participants()

