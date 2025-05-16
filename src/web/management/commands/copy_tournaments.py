from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from web.models import Tournament


class Command(BaseCommand):
    help = "Copy tournaments from X days ahead to X+7 days. Default X=1 (tomorrow)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Days delta for initial date (positive or negative). Default: 1',
        )

    def handle(self, *args, **options):
        days_delta = options['days']
        
        # Определяем базовую дату
        base_date = timezone.now().date() + timedelta(days=days_delta)
        target_date = base_date + timedelta(days=7)

        copied = 0
        for original_tournament in Tournament.objects.filter(date=base_date):
            new_tournament = Tournament(
                customer=original_tournament.customer,
                name=original_tournament.name,
                date=original_tournament.date + timedelta(days=7),
                start_time=original_tournament.start_time,
                end_time=original_tournament.end_time,
                max_participants=original_tournament.max_participants,
                min_participants=original_tournament.min_participants,
                is_canceled=False,
                is_finished=False,
                is_training=original_tournament.is_training,
                description=original_tournament.description,
            )
            new_tournament.save()
            new_tournament.tables.add(*original_tournament.tables.all())
            copied += 1

        self.stdout.write(
            f"Copied {copied} tournaments from {base_date} to {target_date} "
            f"(delta: {days_delta} days)"
        )