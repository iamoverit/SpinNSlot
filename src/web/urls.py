from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('logout/', views.logout_view, name='logout'),
    path('telegram-login/', views.telegram_login, name='telegram_login'),
    path('book/<int:time_slot_id>/<int:item_slot_id>/', views.book_slot, name='book_slot'),
    path('unbook/<int:user_slot_id>/', views.unbook_slot, name='unbook_slot'),
]
