from huey import crontab
from huey.contrib.djhuey import periodic_task
from django.core.management import call_command

@periodic_task(crontab(minute=0, hour=0))
def run_daily_command():
    call_command('copy_tournaments')