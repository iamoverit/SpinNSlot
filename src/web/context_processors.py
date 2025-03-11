from web.models import Customers


def customer_context(request):
    # Логика для получения данных
    customer = Customers.objects.filter().first()
    return {
        'customer': customer,
    }