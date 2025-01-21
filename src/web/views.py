import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q

from .permissions import staff_or_author_required
from .validators import validate_telegram_data
from .models import TimeSlot, ItemSlot, UserSlot, CustomUser

from datetime import date

def index(request):
    timeSlots = TimeSlot.objects.all()
    itemSlots = ItemSlot.objects.all()
    
    # Get selected date from query params or use today's date
    selected_date_str = request.GET.get('date')
    try:
        selected_date = date.fromisoformat(selected_date_str) if selected_date_str else date.today()
        # Validate date is not in the past
        if selected_date < date.today():
            selected_date = date.today()
    except ValueError:
        selected_date = date.today()
        
    userSlots = UserSlot.objects.filter(reservation_date=selected_date) \
        .select_related('user', 'table', 'time')

    # Подготовка данных для шаблона
    schedule = {}
    for timeSlot in timeSlots:
        schedule[timeSlot] = {}
        for itemSlot in itemSlots:
            reserved_user = userSlots.filter(
                Q(time=timeSlot) & Q(table=itemSlot)
            ).first()
            if reserved_user:
                schedule[timeSlot][itemSlot] = reserved_user
            else:
                schedule[timeSlot][itemSlot] = None

    context = {
        'timeSlots': timeSlots,
        'itemSlots': itemSlots,
        'schedule': schedule,
        'selected_date': selected_date,
        'today': date.today(),
    }
    return render(request, 'index.html', context)

@login_required
def book_slot(request, time_slot_id, item_slot_id):
    time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
    item_slot = get_object_or_404(ItemSlot, id=item_slot_id)
    
    # Get date from query params or use today's date
    reservation_date_str = request.GET.get('date')
    try:
        reservation_date = date.fromisoformat(reservation_date_str) if reservation_date_str else date.today()
        # Validate date is not in the past
        if reservation_date < date.today():
            reservation_date = date.today()
    except ValueError:
        reservation_date = date.today()
    try:
        # Check if slot is already booked for this date
        if UserSlot.objects.filter(time=time_slot, table=item_slot, reservation_date=reservation_date).exists():
            return render(request, 'error.html', {'message': 'This slot is already booked for the selected date!'})
        
        # Create booking
        UserSlot.objects.create(
            user=request.user,
            time=time_slot,
            table=item_slot,
            reservation_date=reservation_date
        )
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except ValueError:
        return render(request, 'error.html', {'message': 'Invalid date format'})


@login_required
@staff_or_author_required
def unbook_slot(request, user_slot_id):
    try:
        # Check if slot is already booked for this date
        userSlot = UserSlot.objects.filter(pk=user_slot_id)
        if userSlot.exists():
            userSlot.delete()
        else:
            return render(request, 'error.html', {'message': 'This slot is not booked for the selected date!'})
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    except ValueError:
        return render(request, 'error.html', {'message': 'Invalid date format'})


def logout_view(request):
    logout(request)
    return redirect('index')


def telegram_login(request):
    if request.method == "GET":
        data = request.GET
        if validate_telegram_data(settings.TELEGRAM_BOT_TOKEN, data):
            telegram_id = data.get("id")

            user, created = CustomUser.objects.get_or_create(telegram_id=telegram_id, 
                                                    defaults={
                                                        "username": data.get("username", telegram_id),
                                                        "first_name": data.get("first_name", ""),
                                                        "last_name": data.get("last_name", ""),
                                                        "avatar_url": data.get("photo_url")
                                                    })
            if not created:
                user.username = data.get("username", telegram_id)
                user.first_name = data.get("first_name", "")
                user.last_name = data.get("last_name", "")
                user.save()
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'error.html', {'message': 'Invalid Telegram authentication data.'})
