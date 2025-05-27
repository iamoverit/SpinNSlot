import datetime
from django import template
from django.utils.safestring import mark_safe

from web.models import UserSlot, Tournament
import hashlib

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

@register.filter(name='initials')
def initials(value, default='??'):
    # Обработка пустых значений
    if not value:
        return default.upper()

    value = str(value)
    
    # Удаление лишних пробелов и разделение на части
    parts = value.strip().split()
    
    # Генерация инициалов
    chars = []
    if len(parts) >= 2:
        # Если есть и имя, и фамилия
        chars.append(parts[0][0] if parts[0] else '')
        chars.append(parts[-1][0] if parts[-1] else '')
    else:
        # Если только одно слово
        word = parts[0] if parts else ''
        chars = list(word[:2].ljust(2, ' '))
    
    # Объединение и преобразование в верхний регистр
    return mark_safe(''.join(chars).upper().replace(' ', '&nbsp;'))

@register.filter(name='string_to_color')
def string_to_color(s):
    s = str(s)
    if not s:
        return '#6c757d'
    hash = int(hashlib.md5(s.encode()).hexdigest(), 16)
    colors = [
        "#FF845E",
        "#FEBB5B",
        "#B694F9",
        "#9AD164",
        "#5BCBE3",
        "#5CAFFA",
        "#FF8AAC",
    ]

    return colors[hash % len(colors)]

@register.filter(name='initials_badge')
def initials_badge(value):
    initials_value = initials(value)
    initials_color = string_to_color(value)
    return mark_safe(
        f'<div style="background-color: {initials_color}" class="circle-logo">{initials_value}</div>'
    )