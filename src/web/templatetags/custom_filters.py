import datetime
from django import template

from web.models import UserSlot, Tournament
import markdown

register = template.Library()

@register.filter
def get(dictionary, key):
    return dictionary.get(key, {})

@register.filter
def percentage(value, total):
    try:
        return f"{(value / total * 100):.0f}%"
    except (ZeroDivisionError, TypeError):
        return "0%"

@register.filter
def split_tournament_reason(value):
    """Парсит строку причины бронирования для турниров"""
    if value and value.startswith('Турнир #'):
        parts = value.split('#', 1)
        if len(parts) < 2:
            return None
            
        tournament_parts = parts[1].split(' ', 1)
        return {
            'id': tournament_parts[0].strip(),
            'name': tournament_parts[1].strip() if len(tournament_parts) > 1 else ''
        }
    return None

@register.filter
def is_userslot(value):
    return isinstance(value, UserSlot)

@register.filter
def is_tournament(value):
    return isinstance(value, Tournament)

@register.filter
def format_string(value, arg):
    return value.format(arg)

@register.filter
def weekday(value):
    return value.strftime('%a')

@register.filter
def is_today(value):
    return value == datetime.datetime.today().date()