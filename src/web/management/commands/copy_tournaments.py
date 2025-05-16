from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from web.models import Tournament

class Command(BaseCommand):
    help = 'Copy tomorrow\'s tournaments to next week'

    def handle(self, *args, **options):
        # Определяем даты
        tomorrow = timezone.now().date() + timedelta(days=1)
        next_week_date = tomorrow + timedelta(days=7)

        # Копируем турниры
        copied = 0
        for original_tournament in Tournament.objects.filter(date=tomorrow):
            new_tournament = Tournament(
                customer = original_tournament.customer,
                name = original_tournament.name,
                date = original_tournament.date + timedelta(days=7),
                start_time = original_tournament.start_time,
                end_time = original_tournament.end_time,
                max_participants = original_tournament.max_participants,
                min_participants = original_tournament.min_participants,
                is_canceled = False,
                is_finished = False,
                is_training = original_tournament.is_training,
                description = original_tournament.description,
            )
            new_tournament.save()
            new_tournament.tables.add(*original_tournament.tables.all())
            copied += 1

        self.stdout.write(f"Copied {copied} tournaments from {tomorrow} to {next_week_date}")