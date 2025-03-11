from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.urls import path

from web.admin.forms import TournamentForm
from web.models import CustomUser, ItemSlot, UserSlot, Customers, TimeSlot, Tournament, TournamentRegistration
import datetime
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
    
@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    class Media:
        js = ('js/custom_datetime.js',)
    form = TournamentForm
    change_form_template = 'admin/web/tournament/change_form.html'
    list_display = ('name', 'date', 'customer', 'participants_count', 'min_participants_')
    list_filter = ('is_training', 'is_finished', 'is_canceled', 'name')
    filter_horizontal = ('tables',)
    fieldsets = (
        (None, {
            'fields': ('customer', 'name', 'date', 'start_time', 'end_time')
        }),
        ('Участники', {
            'fields': ('min_participants', 'max_participants', 'tables')
        }),
        ('Дополнительно', {
            'fields': ('description', 'is_canceled', 'is_finished', 'is_training')
        }),
    )
    save_as = True

    def get_changeform_initial_data(self, request):
        return {
            'date': datetime.date.today() + datetime.timedelta(days=1),
        }
    
    @admin.display(description='Min',)
    def min_participants_(self, obj):
        return obj.min_participants
    
    @admin.display(description='Registred',)
    def participants_count(self, obj):
        return f'{obj.tournamentregistration_set.count()}+{obj.guestparticipant_set.count()}/{obj.max_participants}'

# НЕТ повторной регистрации через admin.site.register()
@admin.register(TournamentRegistration)
class TournamentRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tournament', 'registration_date')
    list_filter = ('tournament',)

# # Кастомная форма для редактирования пользователя
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем обязательность поля пароля
        self.fields['password'].required = False
        self.fields['password'].help_text = (
            'Пароль хранится в зашифрованном виде. '
            'Вы можете изменить пароль <a href=\'../password/\'>здесь</a>.'
        )

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm  # Используем кастомную форму
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<id>/password/', self.admin_site.admin_view(self.user_change_password)),
        ]
        return custom_urls + urls

    def user_change_password(self, request, id, form_url=''):
        from django.contrib.auth.views import PasswordChangeView
        return PasswordChangeView.as_view()(request, id, form_url)
