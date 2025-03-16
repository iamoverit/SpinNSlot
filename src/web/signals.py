from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task, on_commit_task

from web.telegram_messages import NotificationService, NotificationStrategyFactory
from .models import Tournament, TournamentRegistration, GuestParticipant

@receiver(post_save, sender=Tournament)
def handle_tournament_status_change(sender, instance, **kwargs):
    if kwargs.get('created', False):
        return
    
    try:
        old_tournament = Tournament.objects.get(pk=instance.pk)
    except Tournament.DoesNotExist:
        return

    service = NotificationService(NotificationStrategyFactory.create(instance))
    if old_tournament.is_canceled != instance.is_canceled:
        if instance.is_canceled:
            service.send_cancellation_notifications(instance)
        else:
            service.send_reactivation_notifications(instance)

@receiver([post_save, post_delete], sender=TournamentRegistration)
def update_on_registration_change(sender, instance: TournamentRegistration, **kwargs):
    service = NotificationService(NotificationStrategyFactory.create(instance.tournament, instance.user))
    service.send_registration_update(
        user=instance.user,
        is_created=kwargs.get('created', False)
    )
    # instance.tournament.check_participants()

@receiver([post_save, post_delete], sender=GuestParticipant)
def update_on_guest_change(sender, instance: GuestParticipant, **kwargs):
    service = NotificationService(NotificationStrategyFactory.create(instance.tournament, instance.registered_by, instance))
    service.send_registration_update(
        user=instance.registered_by,
        is_created=kwargs.get('created', False)
    )
    # instance.tournament.check_participants()

