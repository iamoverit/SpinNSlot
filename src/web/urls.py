from django.urls import path
from . import views

urlpatterns = [
    path('admin/get_timeslot_choices/', views.get_timeslot_choices, name='get_timeslot_choices'),
    path("", views.weekly_schedule, name="index"),
    path("daily-schedule/", views.daily_schedule, name="daily_schedule"),
    path("daily-schedule/<str:selected_date_str>/", views.daily_schedule, name="daily_schedule"),
    path("weekly-schedule/", views.weekly_schedule, name="weekly_schedule"),
    path("weekly-schedule/<str:selected_date_str>/", views.weekly_schedule, name="weekly_schedule"),
    path('logout/', views.logout_view, name='logout'),
    path('telegram-login/', views.telegram_login, name='telegram_login'),
    path('book/<int:time_slot_id>/<int:item_slot_id>/<str:reservation_date_str>/', views.book_slot, name='book_slot'),
    path('unbook/<int:user_slot_id>/', views.unbook_slot, name='unbook_slot'),
    path('tournaments/', views.tournament_list, name='tournament_list'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:tournament_id>/register/', views.register_tournament, name='register_tournament'),
    path('tournaments/<int:tournament_id>/add-guest/', views.add_guest_participant, name='add_guest'),
]
