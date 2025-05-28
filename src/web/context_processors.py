from web.models import Customers
from django.conf import settings


def customer_context(request):
    # Логика для получения данных
    customer = Customers.objects.filter().first()

    return {
        'customer': customer,
        "telegram_bot_name": settings.TELEGRAM_BOT_NAME,
        "telegram_bot_id": settings.TELEGRAM_BOT_TOKEN.split(":")[0] if ":" in settings.TELEGRAM_BOT_TOKEN else None,
    }

def theme(request):
    return {
        'theme': request.session.get('theme', 'light') 
    }