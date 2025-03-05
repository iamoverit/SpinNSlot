from django import template

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
