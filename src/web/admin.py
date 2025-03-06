from django.contrib import admin
from .models import CustomUser, ItemSlot, UserSlot, Customers, TimeSlot, Tournament, TournamentRegistration
# Register your models here.

@admin.register(Customers)
class CustomersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_number')  # Поля для отображения в списке
    search_fields = ('name', 'phone_number')  # Поля для поиска
    ordering = ('name',)  # Сортировка по имени

# Регистрация модели Table
@admin.register(ItemSlot)
class ItemSlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'customer')  # Поля для отображения, включая связь с Customers
    list_filter = ('customer',)  # Фильтры по связанному полю
    search_fields = ('name', 'customer__name')  # Поиск по имени и связанному клиенту
    ordering = ('name',)  # Сортировка по имени

# Регистрация модели UserDateTime
@admin.register(UserSlot)
class UserSlotAdmin(admin.ModelAdmin):
    list_display = ('user', 'table', 'time', 'reservation_date')
    list_filter = ('table', 'user')  # Фильтры по связанным полям
    search_fields = ('user__username', 'table__name')  # Поиск по связанной таблице и пользователю

@admin.register(TimeSlot)
class TimeSlotsAdmin(admin.ModelAdmin):
    list_display = ('customer', 'time_slot')
    list_filter = ('time_slot',)
    search_fields = ('customer__name',)

# ТОЛЬКО через декоратор
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'customer', 'participants_count', 'min_participants')
    filter_horizontal = ('tables',)
    fieldsets = (
        (None, {
            'fields': ('customer', 'name', 'date', 'start_time', 'end_time')
        }),
        ('Участники', {
            'fields': ('min_participants', 'max_participants', 'tables', 'time_slots')
        }),
        ('Дополнительно', {
            'fields': ('registration_deadline', 'description', 'is_canceled', 'is_finished')
        }),
    )
    
    def participants_count(self, obj):
        return f"{obj.participants.count()}/{obj.max_participants}"

# НЕТ повторной регистрации через admin.site.register()
@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tournament', 'registration_date')
    list_filter = ('tournament',)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)
