from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import UserSlot  # Импорт модели резервации

# Проверка: пользователь в группе "staff" или автор резервации
def is_staff_or_author(user, user_slot_id):
    if not user.is_active:
        return False
    
    # Проверяем, является ли пользователь частью группы "staff"
    if user.is_staff or user.is_superuser or user.groups.filter(name='staff').exists():
        return True

    # Проверяем, является ли пользователь автором резервации
    reservation = get_object_or_404(UserSlot, id=user_slot_id)
    if reservation.user == user:
        return True

    return False

# Декоратор для использования в представлении
def staff_or_author_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        user_slot_id = kwargs.get('user_slot_id')
        if not is_staff_or_author(request.user, user_slot_id):
            return HttpResponseForbidden("You don't have permission to perform this action.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
