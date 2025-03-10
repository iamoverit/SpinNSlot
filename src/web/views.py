import datetime
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

from web.utils import DaySlot, get_week_range, prepare_schedule, week_date_iterator
from .models import Customers, Tournament, TournamentRegistration, GuestParticipant
from .permissions import staff_or_author_required
from .validators import validate_telegram_data
from .models import TimeSlot, ItemSlot, UserSlot, CustomUser

from django.db import connection

def tournament_list(request):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=10)
    tournaments = Tournament.objects.filter(is_finished=False, is_canceled=False, date__gt=yesterday).all()
    for tournament in tournaments:
        participants = tournament.tournamentregistration_set.all().values_list('user__username', flat=True)
        guests = tournament.guestparticipant_set.all().values_list('full_name', flat=True)
        tournament.participants_list = list(participants) + list(guests)
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

def daily_schedule(request, selected_date_str=None):
    # TODO: add filter by customer here:
    timeSlots = TimeSlot.objects.all()
    itemSlots = ItemSlot.objects.all()

    try:
        selected_date = datetime.date.fromisoformat(selected_date_str) if selected_date_str else datetime.date.today()
        if selected_date < datetime.date.today():
            selected_date = datetime.date.today()
    except ValueError:
        selected_date = datetime.date.today()

    userSlots = UserSlot.objects.filter(reservation_date=selected_date) \
        .prefetch_related('user', 'table', 'time').all()
    tournaments = Tournament.objects.filter(date=selected_date, is_canceled=False) \
        .prefetch_related('time_slots', 'tables').all()
    
    for tournament in tournaments:
        participants = tournament.tournamentregistration_set.all().values_list('user__username', flat=True)
        guests = tournament.guestparticipant_set.all().values_list('full_name', flat=True)
        tournament.participants_list = list(participants) + list(guests)

    schedule = {}
    for timeSlot in timeSlots:
        schedule[timeSlot.id] = {}
        for itemSlot in itemSlots:
            reserved_user = next((userSlot for userSlot in userSlots if userSlot.time == timeSlot and userSlot.table == itemSlot), None)
            reserved_tournament = next((tournament for tournament in tournaments if timeSlot in tournament.time_slots.all() and itemSlot in tournament.tables.all()), None)
            if reserved_user:
                schedule[timeSlot.id][itemSlot.id] = {
                    "type": "user",
                    "reserved_by": reserved_user,
                    "compare_by": reserved_user.user.id,
                    "colspan": 1,
                    "rowspan": 1,
                }
            elif reserved_tournament:
                schedule[timeSlot.id][itemSlot.id] =  {
                    "type": "tournament",
                    "reserved_by": reserved_tournament,
                    "compare_by": reserved_tournament.id,
                    "colspan": 1,
                    "rowspan": 1,
                }
            else:
                schedule[timeSlot.id][itemSlot.id] = {
                    "type": 'free',
                    "reserved_by": None,
                    "colspan": 1,
                    "rowspan": 1,
                }

    context = {
        'timeSlots': timeSlots,
        'itemSlots': itemSlots,
        'schedule': prepare_schedule(schedule, timeSlots, itemSlots),
        'selected_date': selected_date,
        'today': datetime.date.today(),
    }
    return render(request, 'daily_schedule.html', context)


def weekly_schedule(request, selected_date_str=None):
    # TODO: add filter by customer here:
    timeSlots = TimeSlot.objects.all()

    try:
        selected_date = datetime.date.fromisoformat(selected_date_str) if selected_date_str else datetime.date.today()
        if selected_date < datetime.date.today():
            selected_date = datetime.date.today()
    except ValueError:
        selected_date = datetime.date.today()
    monday, sunday = get_week_range(selected_date)

    tournaments = Tournament.objects.filter(date__range=(monday, sunday), is_canceled=False) \
        .prefetch_related('time_slots', 'tables').all()
    for tournament in tournaments:
        participants = tournament.tournamentregistration_set.all().values_list('user__username', flat=True)
        guests = tournament.guestparticipant_set.all().values_list('full_name', flat=True)
        tournament.participants_list = list(participants) + list(guests)
    schedule = {}

    days = []
    for i, day in enumerate(week_date_iterator(monday, sunday)):
        days.append(DaySlot(i, day))

    for timeSlot in timeSlots:
        schedule[timeSlot.id] = {}
        for day in days:
            reserved_tournament = next((tournament for tournament in tournaments if timeSlot in tournament.time_slots.all() and day.day == tournament.date), None)
            if reserved_tournament:
                schedule[timeSlot.id][day.id] =  {
                    "type": "tournament",
                    "reserved_by": reserved_tournament,
                    "compare_by": reserved_tournament.id,
                    "colspan": 1,
                    "rowspan": 1,
                }
            else:
                schedule[timeSlot.id][day.id] = {
                    "type": 'free',
                    "reserved_by": None,
                    "colspan": 1,
                    "rowspan": 1,
                }
        # print([monday + timedelta(days=i) for i in range((sunday - monday).days + 1)])
              
    context = {
        'week_range': (monday, sunday),
        'timeSlots': timeSlots,
        'days': days,
        'schedule': prepare_schedule(schedule, timeSlots, days),
        'selected_date': selected_date,
        'today': datetime.date.today(),
    }
    return render(request, 'weekly_schedule.html', context)

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
def book_slot(request, time_slot_id, item_slot_id, reservation_date_str):
    time_slot = get_object_or_404(TimeSlot, id=time_slot_id)
    item_slot = get_object_or_404(ItemSlot, id=item_slot_id)
    
    try:
        reservation_date = datetime.date.fromisoformat(reservation_date_str) if reservation_date_str else datetime.date.today()
        if reservation_date < datetime.date.today():
            reservation_date = datetime.date.today()
    except ValueError:
        reservation_date = datetime.date.today()
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

def get_timeslot_choices(request):
    customer_id = request.GET.get('customer_id')
    customer = get_object_or_404(Customers, id=customer_id)
    if customer_id:
        # Фильтруем временные слоты по customer_id
        time_slots= customer.get_time_slots()
    else:
        time_slots = []
    return JsonResponse({'time_slots': time_slots})

