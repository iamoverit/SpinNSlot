import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import Tournament, TournamentRegistration, GuestParticipant
from .permissions import staff_or_author_required
from .validators import validate_telegram_data
from .models import TimeSlot, ItemSlot, UserSlot, CustomUser
from datetime import date
from django.db import connection

def tournament_list(request):
    tournaments = Tournament.objects.all()
    return render(request, 'tournament_list.html', {'tournaments': tournaments})

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    registration = TournamentRegistration.objects.filter(
        user=request.user,
        tournament=tournament
    ).first() if request.user.is_authenticated else None

    # Основные участники с информацией о регистрации
    main_participants = tournament.participants.select_related('guest_profile').all()
    
    # Все гостевые участники
    guest_participants_all = tournament.guestparticipant_set.select_related('registered_by').all()
    
    # Словарь с датами регистрации для отображения
    registration_dates = {
        reg.user_id: reg.registration_date 
        for reg in tournament.tournamentregistration_set.all()
    }

    return render(request, 'tournament_detail.html', {
        'tournament': tournament,
        'current_time': timezone.now(),
        'is_registered': registration is not None,
        'registration_date': registration.registration_date if registration else None,
        'guest_participants': guest_participants_all.filter(registered_by=request.user) if request.user.is_authenticated else [],
        'main_participants': main_participants,
        'guest_participants_all': guest_participants_all,
        'registration_dates': registration_dates,
        'max_guests': 3,
        'total_participants': tournament.total_participants
    })

@login_required
def add_guest_participant(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    current_count = GuestParticipant.objects.filter(
        tournament=tournament,
        registered_by=request.user
    ).count()
    
    if current_count >= 3:
        messages.error(request, "Вы можете зарегистрировать не более 3 гостей")
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    if request.method == 'POST':
        GuestParticipant.objects.create(
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            tournament=tournament,
            registered_by=request.user
        )
        messages.success(request, "Гостевой участник успешно добавлен")
    
    return redirect('tournament_detail', tournament_id=tournament_id)

def index(request):
    timeSlots = TimeSlot.objects.all()
    itemSlots = ItemSlot.objects.all()

    selected_date_str = request.GET.get('date')
    try:
        selected_date = date.fromisoformat(selected_date_str) if selected_date_str else date.today()
        if selected_date < date.today():
            selected_date = date.today()
    except ValueError:
        selected_date = date.today()
        
    userSlots = UserSlot.objects.filter(reservation_date=selected_date) \
        .prefetch_related('user', 'table', 'time').all()
    tournaments = Tournament.objects.filter(date=selected_date) \
        .prefetch_related('time_slots', 'tables').all()
    schedule = {}
    for timeSlot in timeSlots:
        schedule[timeSlot] = {}
        for itemSlot in itemSlots:
            reserved_user = next((userSlot.user for userSlot in userSlots if userSlot.time == timeSlot and userSlot.table == itemSlot), None)
            reserved_tournament = next((tournament for tournament in tournaments if timeSlot in tournament.time_slots.all() and itemSlot in tournament.tables.all()), None)
            if reserved_user:
                schedule[timeSlot][itemSlot] = reserved_user
            elif reserved_tournament:
                schedule[timeSlot][itemSlot] = reserved_tournament
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
def register_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    if TournamentRegistration.objects.filter(user=request.user, tournament=tournament).exists():
        return render(request, 'error.html', {'message': 'Вы уже зарегистрированы на этот турнир'})
    
    if tournament.participants.count() >= tournament.max_participants:
        return render(request, 'error.html', {'message': 'Достигнут лимит участников'})
    
    TournamentRegistration.objects.create(user=request.user, tournament=tournament)
    return redirect('tournament_detail', tournament_id=tournament.id)

@login_required
def book_slot(request, time_slot_id, item_slot_id):
    time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
    item_slot = get_object_or_404(ItemSlot, id=item_slot_id)
    
    reservation_date_str = request.GET.get('date')
    try:
        reservation_date = date.fromisoformat(reservation_date_str) if reservation_date_str else date.today()
        if reservation_date < date.today():
            reservation_date = date.today()
    except ValueError:
        reservation_date = date.today()
    try:
        if UserSlot.objects.filter(time=time_slot, table=item_slot, reservation_date=reservation_date).exists():
            return render(request, 'error.html', {'message': 'This slot is already booked for the selected date!'})
        
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
